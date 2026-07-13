from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.models.subscription import AccountEntitlement, DetectionUsage

PLANS = {
    "guest": {
        "key": "guest",
        "name": "Guest",
        "price": "Free",
        "limit": 2,
        "windowHours": 24,
        "features": ["2 image trials per day", "Image result summary"],
    },
    "starter": {
        "key": "starter",
        "name": "Starter",
        "price": "Free",
        "limit": 10,
        "windowHours": 12,
        "features": ["10 detections every 12 hours", "Image and video detection", "Personal dashboard and history", "Reviewer feedback"],
    },
    "basic": {
        "key": "basic",
        "name": "Basic",
        "price": "RM 19/month",
        "limit": 100,
        "windowHours": 12,
        "features": ["100 detections every 12 hours", "DeepSight browser extension", "Video frame analysis", "Firebase history sync"],
    },
    "lite": {
        "key": "lite",
        "name": "Lite",
        "price": "RM 49/month",
        "limit": None,
        "windowHours": None,
        "features": ["Unlimited detections", "Live webcam detection", "Pro continuous-scanning extension", "All analytics and reports"],
    },
}


class SubscriptionService:
    @staticmethod
    def ensure_entitlement(db: Session, email: str) -> AccountEntitlement:
        entitlement = db.query(AccountEntitlement).filter(AccountEntitlement.email == email).first()
        if entitlement is None:
            entitlement = AccountEntitlement(email=email, plan="starter", status="active")
            db.add(entitlement)
            db.commit()
            db.refresh(entitlement)
        return entitlement

    @staticmethod
    def resolve_identity(db: Session, authorization: str | None, guest_id: str | None):
        if authorization and authorization.lower().startswith("bearer "):
            payload = decode_access_token(authorization.split(" ", 1)[1])
            if payload is None or not payload.get("sub"):
                raise HTTPException(status_code=401, detail="Invalid or expired session.")
            email = payload["sub"]
            entitlement = SubscriptionService.ensure_entitlement(db, email)
            return email, entitlement.plan, True
        return f"guest:{guest_id or 'anonymous'}", "guest", False

    @staticmethod
    def status(db: Session, authorization: str | None, guest_id: str | None) -> dict:
        identity, plan_key, authenticated = SubscriptionService.resolve_identity(db, authorization, guest_id)
        plan = PLANS[plan_key]
        if plan["limit"] is None:
            used = 0
            remaining = None
            resets_at = None
        else:
            if plan_key == "guest":
                now = datetime.utcnow()
                window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                resets_at = window_start + timedelta(days=1)
            else:
                window_start = datetime.utcnow() - timedelta(hours=plan["windowHours"])
                resets_at = datetime.utcnow() + timedelta(hours=plan["windowHours"])
            used = db.query(DetectionUsage).filter(
                DetectionUsage.identity == identity,
                DetectionUsage.created_at >= window_start,
            ).count()
            remaining = max(plan["limit"] - used, 0)

        return {
            "authenticated": authenticated,
            "plan": plan,
            "used": used,
            "remaining": remaining,
            "resetsAt": resets_at.isoformat() if resets_at else None,
        }

    @staticmethod
    def consume(
        db: Session,
        authorization: str | None,
        guest_id: str | None,
        media_type: str,
        client_type: str = "web",
    ):
        _, plan_key, authenticated = SubscriptionService.resolve_identity(db, authorization, guest_id)
        is_admin = False
        if authorization and authorization.lower().startswith("bearer "):
            payload = decode_access_token(authorization.split(" ", 1)[1])
            is_admin = bool(payload and payload.get("role") == "admin")
        if media_type == "video" and not authenticated:
            raise HTTPException(status_code=403, detail="Sign in to use video detection.")
        if client_type == "extension" and plan_key not in {"basic", "lite"} and not is_admin:
            raise HTTPException(status_code=403, detail="The browser extension requires a Basic or Lite plan.")
        if client_type in {"extension-pro", "live"} and plan_key != "lite" and not is_admin:
            raise HTTPException(status_code=403, detail="Live detection requires the Lite plan.")
        status = SubscriptionService.status(db, authorization, guest_id)
        if status["remaining"] == 0:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Detection limit reached for the current plan.",
                    "plan": status["plan"]["name"],
                    "resetsAt": status["resetsAt"],
                },
            )
        identity, _, _ = SubscriptionService.resolve_identity(db, authorization, guest_id)
        db.add(DetectionUsage(identity=identity, media_type=media_type))
        db.commit()
        return SubscriptionService.status(db, authorization, guest_id)
