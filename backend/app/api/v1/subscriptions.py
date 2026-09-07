from typing import Literal
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import AnalysisPrincipal, get_analysis_principal
from app.services.subscription_service import SubscriptionService
from app.services.stripe_service import StripeService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_code: Literal["basic", "lite"]
    billing_period: Literal["monthly", "annual"]


@router.get("/plans")
def plans(db: Session = Depends(get_db)):
    return [SubscriptionService.serialize_plan(plan) for plan in SubscriptionService.plans(db) if plan.code != "guest"]


@router.get("/status")
@router.get("/current")
def status(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    return SubscriptionService.status(
        db,
        authorization,
        str(principal.guest_session_id) if principal.guest_session_id else None,
    )


@router.post("/checkout")
def checkout(request: CheckoutRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return StripeService.checkout(db, user, request.plan_code, request.billing_period)


@router.post("/portal")
def portal(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return StripeService.portal(db, user)
