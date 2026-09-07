from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.guest_session import GuestSession
from app.models.user import User
from app.services.guest_session_service import GuestSessionService


@dataclass(frozen=True)
class AnalysisPrincipal:
    user: User | None = None
    guest_session: GuestSession | None = None

    @property
    def owner_user_id(self) -> int | None:
        return self.user.id if self.user else None

    @property
    def guest_session_id(self) -> int | None:
        return self.guest_session.id if self.guest_session else None


def get_optional_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization:
        return None
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme.")
    payload = decode_access_token(authorization.split(" ", 1)[1])
    if payload is None or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    query = db.query(User)
    token_user_id = payload.get("uid")
    user = query.filter(User.id == token_user_id).first() if isinstance(token_user_id, int) else None
    if user is None:
        user = query.filter(User.email == str(payload["sub"]).lower()).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Authenticated account no longer exists.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive.")
    return user


def get_current_user(
    user: User | None = Depends(get_optional_current_user),
) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user


def get_optional_guest_session(
    request: Request,
    db: Session = Depends(get_db),
) -> GuestSession | None:
    raw_token = request.cookies.get(GuestSessionService.cookie_name())
    if not raw_token:
        return None
    return GuestSessionService.verify(db, raw_token)


def get_analysis_principal(
    user: User | None = Depends(get_optional_current_user),
    guest_session: GuestSession | None = Depends(get_optional_guest_session),
) -> AnalysisPrincipal:
    if user is not None:
        return AnalysisPrincipal(user=user)
    if guest_session is not None:
        return AnalysisPrincipal(guest_session=guest_session)
    raise HTTPException(status_code=401, detail="Authentication or a valid guest session is required.")


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return user
