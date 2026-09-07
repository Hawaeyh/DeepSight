from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.subscription import AccountEntitlement, StripeEvent, SubscriptionPlan
from app.models.user import User
from app.services.notification_service import AuditService, NotificationService
from app.services.subscription_service import SubscriptionService


class StripeService:
    @staticmethod
    def configured() -> bool:
        return bool(settings.STRIPE_ENABLED and settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.startswith("sk_test_") and settings.STRIPE_WEBHOOK_SECRET)

    @staticmethod
    def status() -> dict:
        if not settings.STRIPE_ENABLED:
            return {"status": "not_configured", "mode": None}
        if not StripeService.configured():
            return {"status": "failed", "mode": "test"}
        return {"status": "ok", "mode": "test"}

    @staticmethod
    def client():
        if not StripeService.configured():
            raise HTTPException(status_code=503, detail={"status": "not_configured", "message": "Stripe test-mode payments are not configured."})
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    @staticmethod
    def sync_configured_prices(db: Session) -> None:
        configured = {("basic", "monthly"): settings.STRIPE_PRICE_BASIC_MONTHLY, ("basic", "annual"): settings.STRIPE_PRICE_BASIC_ANNUAL, ("lite", "monthly"): settings.STRIPE_PRICE_LITE_MONTHLY, ("lite", "annual"): settings.STRIPE_PRICE_LITE_ANNUAL}
        changed = False
        for (code, interval), price_id in configured.items():
            if not price_id: continue
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == code).first()
            field = f"stripe_{interval}_price_id"
            if plan is not None and getattr(plan, field) != price_id:
                setattr(plan, field, price_id); changed = True
        if changed: db.commit()

    @staticmethod
    def price_id(plan: SubscriptionPlan, interval: str) -> str | None:
        return plan.stripe_monthly_price_id if interval == "monthly" else plan.stripe_annual_price_id if interval == "annual" else None

    @staticmethod
    def checkout(db: Session, user: User, plan_code: str, interval: str) -> dict:
        stripe = StripeService.client()
        StripeService.sync_configured_prices(db)
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == plan_code, SubscriptionPlan.is_active.is_(True)).first()
        price = StripeService.price_id(plan, interval) if plan else None
        if plan is None or plan.monthly_price <= 0 or interval not in {"monthly", "annual"} or not price:
            raise HTTPException(status_code=422, detail="The selected billing plan is unavailable.")
        entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)
        if entitlement.stripe_subscription_id and entitlement.status in {"active", "trialing", "past_due"}:
            raise HTTPException(status_code=409, detail={"code": "SUBSCRIPTION_EXISTS", "message": "Manage the existing subscription in the billing portal."})
        params = {"mode": "subscription", "line_items": [{"price": price, "quantity": 1}], "success_url": settings.STRIPE_SUCCESS_URL, "cancel_url": settings.STRIPE_CANCEL_URL, "client_reference_id": str(user.id), "metadata": {"user_id": str(user.id), "plan_code": plan_code, "billing_interval": interval}, "subscription_data": {"metadata": {"user_id": str(user.id), "plan_code": plan_code, "billing_interval": interval}}}
        if entitlement.stripe_customer_id: params["customer"] = entitlement.stripe_customer_id
        else: params["customer_email"] = user.email
        session = stripe.checkout.Session.create(**params, idempotency_key=f"checkout-{user.id}-{plan_code}-{interval}-{datetime.utcnow().date().isoformat()}")
        AuditService.record(db, user.id, "stripe.checkout_created", "subscription_plan", plan_code); db.commit()
        return {"status": "ok", "checkoutUrl": session.url, "sessionId": session.id}

    @staticmethod
    def portal(db: Session, user: User) -> dict:
        stripe = StripeService.client(); entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)
        if not entitlement.stripe_customer_id: raise HTTPException(status_code=404, detail="No billing customer exists for this account.")
        session = stripe.billing_portal.Session.create(customer=entitlement.stripe_customer_id, return_url=settings.STRIPE_SUCCESS_URL)
        return {"status": "ok", "portalUrl": session.url}

    @staticmethod
    def process_event(db: Session, event: dict) -> dict:
        event_id, event_type = event["id"], event["type"]
        existing = db.query(StripeEvent).filter(StripeEvent.event_id == event_id).first()
        if existing: return {"status": "duplicate", "eventId": event_id}
        obj = event["data"]["object"]
        customer_id = obj.get("customer")
        subscription_id = obj.get("id") if event_type.startswith("customer.subscription.") else obj.get("subscription")
        record = StripeEvent(event_id=event_id, event_type=event_type, status="processed", customer_id=customer_id, subscription_id=subscription_id, safe_metadata={"livemode": bool(event.get("livemode"))})
        db.add(record)
        metadata = obj.get("metadata") or {}
        entitlement = db.query(AccountEntitlement).filter(AccountEntitlement.stripe_customer_id == customer_id).first() if customer_id else None
        user = db.query(User).filter(User.id == int(metadata["user_id"])).first() if metadata.get("user_id", "").isdigit() else None
        if entitlement is None and user is not None:
            entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id); entitlement.stripe_customer_id = customer_id
        if event_type == "checkout.session.completed" and entitlement:
            entitlement.stripe_customer_id = customer_id
            if subscription_id: entitlement.stripe_subscription_id = subscription_id
        elif entitlement and event_type in {"customer.subscription.created", "customer.subscription.updated"}:
            items = ((obj.get("items") or {}).get("data") or [])
            price_id = (((items[0].get("price") or {}).get("id")) if items else None)
            plan = db.query(SubscriptionPlan).filter((SubscriptionPlan.stripe_monthly_price_id == price_id) | (SubscriptionPlan.stripe_annual_price_id == price_id)).first() if price_id else None
            status = obj.get("status", "incomplete")
            if plan is not None:
                entitlement.plan = plan.code if status in {"active", "trialing"} else "starter"
                entitlement.status = status; entitlement.stripe_subscription_id = obj.get("id"); entitlement.stripe_price_id = price_id
                entitlement.billing_interval = "monthly" if plan.stripe_monthly_price_id == price_id else "annual"
                entitlement.provider = "stripe"; entitlement.cancel_at_period_end = bool(obj.get("cancel_at_period_end"))
                if obj.get("current_period_start"): entitlement.current_period_start = datetime.utcfromtimestamp(obj["current_period_start"])
                if obj.get("current_period_end"): entitlement.current_period_end = datetime.utcfromtimestamp(obj["current_period_end"])
                NotificationService.create(db, entitlement.user_id, "subscription_updated", "Subscription updated", f"Your {plan.name} subscription is {status}.")
            else:
                record.status = "ignored_unknown_price"
        elif entitlement and event_type == "customer.subscription.deleted":
            entitlement.plan = "starter"; entitlement.status = "canceled"; entitlement.stripe_price_id = None; entitlement.provider = "stripe"
        elif entitlement and event_type == "invoice.payment_failed":
            entitlement.status = "past_due"; NotificationService.create(db, entitlement.user_id, "payment_failed", "Payment failed", "Your subscription payment failed. Update your billing method.")
        elif entitlement and event_type == "invoice.paid":
            entitlement.status = "active"; NotificationService.create(db, entitlement.user_id, "subscription_renewed", "Subscription renewed", "Your subscription payment was received.")
        db.commit(); return {"status": record.status, "eventId": event_id}
