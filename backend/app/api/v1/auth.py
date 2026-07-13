from fastapi import APIRouter, Depends, Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    UserLogin,
    UserRegister,
    GoogleLogin,
)
from app.core.config import settings
from app.services.subscription_service import SubscriptionService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
def register(
    request: UserRegister,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    user = User(
        full_name=request.full_name,
        email=request.email,
        password=hash_password(request.password),
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    SubscriptionService.ensure_entitlement(db, user.email)

    return {
        "message": "Registration successful",
        "access_token": create_access_token({"sub": user.email, "role": user.role}),
        "token_type": "bearer",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "plan": "starter"},
    }


@router.post("/login")
def login(
    request: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
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

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    entitlement = SubscriptionService.ensure_entitlement(db, user.email)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "plan": entitlement.plan},
    }


@router.get("/me")
def me(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    payload = decode_access_token(authorization.split(" ", 1)[1])
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled.")
    entitlement = SubscriptionService.ensure_entitlement(db, user.email)
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "plan": entitlement.plan}


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

    email = identity.get("email")
    if not email or not identity.get("email_verified"):
        raise HTTPException(status_code=401, detail="A verified Google email is required.")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            full_name=identity.get("name") or email.split("@")[0],
            email=email,
            password="google-oauth",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled.")
    entitlement = SubscriptionService.ensure_entitlement(db, user.email)
    token = create_access_token({"sub": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "plan": entitlement.plan},
    }
