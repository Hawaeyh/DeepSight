import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.guest_session import GuestSession


class GuestSessionService:
    @staticmethod
    def cookie_name() -> str:
        return settings.GUEST_SESSION_COOKIE_NAME

    @staticmethod
    def _token_hash(token: str) -> str:
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"), token.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _request_hash(value: str | None) -> str | None:
        if not value:
            return None
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"), value.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @classmethod
    def create(cls, db: Session, request: Request, response: Response) -> GuestSession:
        raw_token = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        session = GuestSession(
            token_hash=cls._token_hash(raw_token),
            ip_hash=cls._request_hash(request.client.host if request.client else None),
            user_agent_hash=cls._request_hash(request.headers.get("user-agent")),
            expires_at=now + timedelta(hours=settings.GUEST_SESSION_HOURS),
            created_at=now,
            last_used_at=now,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        response.set_cookie(
            key=cls.cookie_name(),
            value=raw_token,
            max_age=settings.GUEST_SESSION_HOURS * 3600,
            httponly=True,
            secure=settings.APP_ENV in {"staging", "production"},
            samesite="lax",
            path="/",
        )
        return session

    @classmethod
    def verify(cls, db: Session, raw_token: str) -> GuestSession:
        session = (
            db.query(GuestSession)
            .filter(GuestSession.token_hash == cls._token_hash(raw_token))
            .first()
        )
        if session is None:
            raise HTTPException(status_code=401, detail="Invalid guest session.")
        if session.expires_at <= datetime.utcnow():
            raise HTTPException(status_code=401, detail="Guest session has expired.")
        if session.transferred_at is not None:
            raise HTTPException(status_code=401, detail="Guest session has already been transferred.")
        return session
