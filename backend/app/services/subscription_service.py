from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.models.subscription import AccountEntitlement, DetectionUsage, SubscriptionPlan
from app.models.user import User


DEFAULT_PLANS = (
    dict(code="guest", name="Guest", monthly_price=0, annual_price=0, image_limit=2, video_limit=0, webcam_limit=0, extension_limit=0, window_hours=24, history_retention_days=1, report_enabled=False, features=["2 image trials per day"]),
    dict(code="starter", name="Starter", monthly_price=0, annual_price=0, image_limit=10, video_limit=10, webcam_limit=0, extension_limit=0, window_hours=12, history_retention_days=90, report_enabled=True, features=["Image and video detection", "Personal history", "Reports"]),
    dict(code="basic", name="Basic", monthly_price=19, annual_price=190, image_limit=100, video_limit=30, webcam_limit=0, extension_limit=100, window_hours=12, history_retention_days=365, report_enabled=True, features=["Browser extension", "Video analysis", "Reports"]),
    dict(code="lite", name="Lite", monthly_price=49, annual_price=490, image_limit=None, video_limit=None, webcam_limit=None, extension_limit=None, window_hours=None, history_retention_days=None, report_enabled=True, features=["Unlimited detection", "Live webcam", "Continuous extension"]),
)


class SubscriptionService:
    @staticmethod
    def ensure_plans(db: Session) -> None:
        if db.query(SubscriptionPlan).count() == 0:
            db.add_all([SubscriptionPlan(**item, is_active=True) for item in DEFAULT_PLANS])
            db.commit()

    @staticmethod
    def plans(db: Session) -> list[SubscriptionPlan]:
        SubscriptionService.ensure_plans(db)
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active.is_(True)).order_by(SubscriptionPlan.monthly_price).all()

    @staticmethod
    def serialize_plan(plan: SubscriptionPlan) -> dict:
        price = "Free" if plan.monthly_price == 0 else f"RM {plan.monthly_price:g}/month"
        return {"key": plan.code, "code": plan.code, "name": plan.name, "price": price, "monthlyPrice": plan.monthly_price, "annualPrice": plan.annual_price, "limit": plan.image_limit, "windowHours": plan.window_hours, "features": plan.features or [], "limits": {"image": plan.image_limit, "video": plan.video_limit, "webcam": plan.webcam_limit, "extension": plan.extension_limit}, "historyRetentionDays": plan.history_retention_days, "reportEnabled": plan.report_enabled, "billingAvailable": {"monthly": bool(plan.stripe_monthly_price_id), "annual": bool(plan.stripe_annual_price_id)}}

    @staticmethod
    def ensure_entitlement(db: Session, email: str, user_id: int | None = None) -> AccountEntitlement:
        normalized_email = email.lower()
        entitlement = db.query(AccountEntitlement).filter(AccountEntitlement.user_id == user_id).first() if user_id is not None else None
        if entitlement is None:
            entitlement = db.query(AccountEntitlement).filter(AccountEntitlement.email == normalized_email).first()
        if entitlement is None:
            entitlement = AccountEntitlement(email=normalized_email, user_id=user_id, plan="starter", status="active")
            db.add(entitlement); db.commit(); db.refresh(entitlement)
        elif user_id is not None and entitlement.user_id is None:
            entitlement.user_id = user_id; db.commit()
        elif user_id is not None and entitlement.user_id != user_id:
            raise HTTPException(status_code=409, detail="The account entitlement is linked to another user.")
        return entitlement

    @staticmethod
    def resolve_identity(db: Session, authorization: str | None, guest_id: str | None):
        SubscriptionService.ensure_plans(db)
        if authorization and authorization.lower().startswith("bearer "):
            payload = decode_access_token(authorization.split(" ", 1)[1])
            if payload is None or not payload.get("sub"):
                raise HTTPException(status_code=401, detail="Invalid or expired session.")
            email = str(payload["sub"]).lower()
            user = db.query(User).filter(User.email == email).first()
            if user is None or not user.is_active:
                raise HTTPException(status_code=403, detail="Account is inactive or unavailable.")
            entitlement = SubscriptionService.ensure_entitlement(db, email, user.id)
            entitlement_active = entitlement.status == "active" and (
                entitlement.current_period_end is None or entitlement.current_period_end > datetime.utcnow()
            )
            plan_code = "lite" if user.role == "admin" else entitlement.plan if entitlement_active else "starter"
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == plan_code, SubscriptionPlan.is_active.is_(True)).first()
            if plan is None:
                raise HTTPException(status_code=403, detail="The account plan is unavailable.")
            return email, plan, True, user
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == "guest").one()
        return f"guest:{guest_id or 'anonymous'}", plan, False, None

    @staticmethod
    def _window_start(plan: SubscriptionPlan) -> datetime:
        now = datetime.utcnow()
        if plan.code == "guest":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        return now - timedelta(hours=plan.window_hours or 24)

    @staticmethod
    def _limit(plan: SubscriptionPlan, media_type: str) -> int | None:
        return {"image": plan.image_limit, "video": plan.video_limit, "webcam": plan.webcam_limit, "extension": plan.extension_limit}.get(media_type, plan.image_limit)

    @staticmethod
    def status(db: Session, authorization: str | None, guest_id: str | None, media_type: str = "image") -> dict:
        identity, plan, authenticated, user = SubscriptionService.resolve_identity(db, authorization, guest_id)
        limit = SubscriptionService._limit(plan, media_type)
        if limit is None:
            used = 0; remaining = None; resets_at = None
        else:
            window_start = SubscriptionService._window_start(plan)
            used = db.query(DetectionUsage).filter(DetectionUsage.identity == identity, DetectionUsage.media_type == media_type, DetectionUsage.status.in_(["reserved", "completed"]), DetectionUsage.created_at >= window_start).count()
            remaining = max(limit - used, 0)
            resets_at = window_start + timedelta(hours=24 if plan.code == "guest" else plan.window_hours or 24)
        entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id) if user else None
        return {"authenticated": authenticated, "plan": SubscriptionService.serialize_plan(plan), "used": used, "remaining": remaining, "resetsAt": resets_at.isoformat() if resets_at else None, "subscriptionStatus": entitlement.status if entitlement else None, "provider": entitlement.provider if entitlement else None, "cancelAtPeriodEnd": entitlement.cancel_at_period_end if entitlement else False, "currentPeriodEnd": entitlement.current_period_end.isoformat() if entitlement and entitlement.current_period_end else None, "hasBillingCustomer": bool(entitlement and entitlement.stripe_customer_id)}

    @staticmethod
    def reserve(db: Session, authorization: str | None, guest_id: str | None, media_type: str, client_type: str = "web") -> DetectionUsage:
        identity, plan, authenticated, user = SubscriptionService.resolve_identity(db, authorization, guest_id)
        effective_media_type = "webcam" if client_type == "live" else "extension" if client_type in {"extension", "extension-pro", "extension-video"} else media_type
        is_admin = bool(user and user.role == "admin")
        if media_type == "video" and not authenticated:
            raise HTTPException(status_code=403, detail="Sign in to use video detection.")
        if client_type in {"extension", "extension-video"} and plan.code not in {"basic", "lite"} and not is_admin:
            raise HTTPException(status_code=403, detail="The browser extension requires a Basic or Lite plan.")
        if client_type in {"extension-pro", "live"} and plan.code != "lite" and not is_admin:
            raise HTTPException(status_code=403, detail="Live detection requires the Lite plan.")
        if SubscriptionService.status(db, authorization, guest_id, effective_media_type)["remaining"] == 0:
            raise HTTPException(status_code=429, detail={"message": "Detection limit reached for the current plan.", "plan": plan.name})
        usage = DetectionUsage(identity=identity, media_type=effective_media_type, reservation_key=uuid4().hex, status="reserved")
        db.add(usage); db.commit(); db.refresh(usage)
        return usage

    @staticmethod
    def complete(db: Session, usage: DetectionUsage) -> None:
        usage.status = "completed"; usage.completed_at = datetime.utcnow(); db.commit()

    @staticmethod
    def release(db: Session, usage: DetectionUsage) -> None:
        usage.status = "released"; usage.released_at = datetime.utcnow(); db.commit()

    @staticmethod
    def complete_key(db: Session, reservation_key: str | None) -> None:
        usage = db.query(DetectionUsage).filter(DetectionUsage.reservation_key == reservation_key).first() if reservation_key else None
        if usage and usage.status == "reserved": SubscriptionService.complete(db, usage)

    @staticmethod
    def release_key(db: Session, reservation_key: str | None) -> None:
        usage = db.query(DetectionUsage).filter(DetectionUsage.reservation_key == reservation_key).first() if reservation_key else None
        if usage and usage.status == "reserved": SubscriptionService.release(db, usage)

    @staticmethod
    def consume(db: Session, authorization: str | None, guest_id: str | None, media_type: str, client_type: str = "web"):
        usage = SubscriptionService.reserve(db, authorization, guest_id, media_type, client_type)
        SubscriptionService.complete(db, usage)
        return SubscriptionService.status(db, authorization, guest_id, media_type)
