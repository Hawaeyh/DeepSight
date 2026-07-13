from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.subscription_service import PLANS, SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans")
def plans():
    return [PLANS[key] for key in ("starter", "basic", "lite")]


@router.get("/status")
def status(
    authorization: str | None = Header(None),
    x_guest_id: str | None = Header(None),
    db: Session = Depends(get_db),
):
    return SubscriptionService.status(db, authorization, x_guest_id)
