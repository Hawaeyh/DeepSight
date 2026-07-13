from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.database import get_db
from app.models.subscription import AccountEntitlement, DetectionUsage
from app.models.user import User
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/admin", tags=["Administration"])


class UserAdminUpdate(BaseModel):
    role: Literal["user", "admin"] | None = None
    plan: Literal["starter", "basic", "lite"] | None = None
    is_active: bool | None = None


def serialize_user(db: Session, user: User) -> dict:
    entitlement = SubscriptionService.ensure_entitlement(db, user.email)
    usage_count = db.query(DetectionUsage).filter(DetectionUsage.identity == user.email).count()
    last_used = (
        db.query(func.max(DetectionUsage.created_at))
        .filter(DetectionUsage.identity == user.email)
        .scalar()
    )
    return {
        "id": user.id,
        "fullName": user.full_name,
        "email": user.email,
        "role": user.role,
        "plan": entitlement.plan,
        "isActive": user.is_active,
        "usageCount": usage_count,
        "lastUsedAt": last_used,
        "createdAt": user.created_at,
    }


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [serialize_user(db, user) for user in users]


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    request: UserAdminUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == admin.id and (request.role == "user" or request.is_active is False):
        raise HTTPException(status_code=400, detail="You cannot demote or disable your current account.")

    if request.role is not None:
        user.role = request.role
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.plan is not None:
        entitlement = SubscriptionService.ensure_entitlement(db, user.email)
        entitlement.plan = request.plan
        entitlement.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return serialize_user(db, user)


@router.get("/usage")
def usage_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    registered_filter = ~DetectionUsage.identity.like("guest:%")
    window_start = datetime.utcnow() - timedelta(days=13)
    rows = (
        db.query(
            func.date(DetectionUsage.created_at).label("day"),
            func.count(DetectionUsage.id).label("runs"),
            func.count(func.distinct(DetectionUsage.identity)).label("active_users"),
        )
        .filter(DetectionUsage.created_at >= window_start, registered_filter)
        .group_by(func.date(DetectionUsage.created_at))
        .order_by(func.date(DetectionUsage.created_at))
        .all()
    )
    by_day = {str(row.day): row for row in rows}
    trend = []
    for offset in range(14):
        day = (window_start + timedelta(days=offset)).date().isoformat()
        row = by_day.get(day)
        trend.append({"date": day, "runs": row.runs if row else 0, "activeUsers": row.active_users if row else 0})

    plan_rows = (
        db.query(AccountEntitlement.plan, func.count(AccountEntitlement.id))
        .group_by(AccountEntitlement.plan)
        .all()
    )
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    total_runs = db.query(DetectionUsage).filter(registered_filter).count()
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalRuns": total_runs,
        "runsLast14Days": sum(item["runs"] for item in trend),
        "trend": trend,
        "plans": [{"plan": plan, "users": count} for plan, count in plan_rows],
    }
