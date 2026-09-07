from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from secrets import token_urlsafe
from datetime import datetime
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.user import (
    UserLogin,
    UserRegister,
    GoogleLogin,
)
from app.core.config import settings
from app.services.subscription_service import SubscriptionService
from app.auth.firebase import FirebaseNotConfiguredError, verify_firebase_token


class FirebaseLogin(BaseModel):
    id_token: str = Field(min_length=20)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def issue_user_token(user: User) -> str:
    return create_access_token(
        {"sub": user.email, "uid": user.id, "authentication_source": user.authentication_source}
    )


def user_payload(user: User, plan: str) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "plan": plan,
        "firebase_uid": user.firebase_uid,
        "email_verified": user.email_verified,
        "authentication_source": user.authentication_source,
    }


@router.post("/register")
def register(
    request: UserRegister,
    db: Session = Depends(get_db),
):
    normalized_email = request.email.strip().lower()
    existing = (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    user = User(
        full_name=request.full_name,
        email=normalized_email,
        password=hash_password(request.password),
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    SubscriptionService.ensure_entitlement(db, user.email, user.id)

    return {
        "message": "Registration successful",
        "access_token": issue_user_token(user),
        "token_type": "bearer",
        "user": user_payload(user, "starter"),
    }


@router.post("/login")
def login(
    request: UserLogin,
    db: Session = Depends(get_db),
):
    normalized_email = request.email.strip().lower()
    user = (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled.")

    if not verify_password(
        request.password,
        user.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = issue_user_token(user)

    entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_payload(user, entitlement.plan),
    }


@router.get("/me")
def me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)
    return user_payload(user, entitlement.plan)


@router.post("/google")
def google_login(request: GoogleLogin, db: Session = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured.")
    try:
        identity = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception as error:
        raise HTTPException(status_code=401, detail="Invalid Google credential.") from error

    email = str(identity.get("email") or "").strip().lower()
    if not email or not identity.get("email_verified"):
        raise HTTPException(status_code=401, detail="A verified Google email is required.")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            full_name=identity.get("name") or email.split("@")[0],
            email=email,
            password="google-oauth",
            authentication_source="google",
            email_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled.")
    entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)
    token = issue_user_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_payload(user, entitlement.plan),
    }


@router.post("/firebase")
def firebase_login(request: FirebaseLogin, db: Session = Depends(get_db)):
    try:
        identity = verify_firebase_token(request.id_token)
    except FirebaseNotConfiguredError:
        raise HTTPException(status_code=503, detail={"status": "not_configured", "message": "Firebase Admin authentication is not configured."}) from None
    except Exception as error:
        error_name = error.__class__.__name__
        if error_name == "ExpiredIdTokenError":
            code, message = "FIREBASE_TOKEN_EXPIRED", "The Firebase session has expired."
        elif error_name in {"RevokedIdTokenError", "UserDisabledError"}:
            code, message = "FIREBASE_USER_DISABLED", "This Firebase session is no longer active."
        else:
            code, message = "FIREBASE_TOKEN_INVALID", "The Firebase ID token is invalid."
        raise HTTPException(status_code=401, detail={"code": code, "message": message}) from None
    uid = str(identity.get("uid") or "")
    email = str(identity.get("email") or "").strip().lower()
    if not uid or not email or not identity.get("email_verified"):
        raise HTTPException(status_code=401, detail="A verified Firebase email is required.")
    user = db.query(User).filter(User.firebase_uid == uid).first()
    if user is None:
        email_owner = db.query(User).filter(func.lower(User.email) == email).first()
        if email_owner is not None:
            raise HTTPException(status_code=409, detail={"code": "ACCOUNT_LINK_CONFLICT", "message": "Sign in with the existing account before linking Firebase."})
        provider = str((identity.get("firebase") or {}).get("sign_in_provider") or "firebase")
        user = User(full_name=identity.get("name") or email.split("@")[0], email=email, password=hash_password(token_urlsafe(32)), firebase_uid=uid, firebase_email=email, firebase_provider=provider, firebase_linked_at=datetime.utcnow(), authentication_source="firebase", email_verified=True)
        db.add(user); db.commit(); db.refresh(user)
    if not user.is_active: raise HTTPException(status_code=403, detail={"code": "USER_INACTIVE", "message": "This account has been disabled."})
    entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)
    return {"access_token": issue_user_token(user), "token_type": "bearer", "user": user_payload(user, entitlement.plan)}
