from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.database import get_db
from app.models.subscription import AccountEntitlement, DetectionUsage
from app.models.user import User
from app.services.subscription_service import SubscriptionService
from app.services.notification_service import AuditService
from app.models.notification import AuditEvent
from app.models.analysis import Analysis
from app.models.video_job import VideoJob
from app.ai.model_status import get_model_catalog, get_model_load_status

router = APIRouter(prefix="/admin", tags=["Administration"])


class UserAdminUpdate(BaseModel):
    role: Literal["user", "admin"] | None = None
    plan: Literal["starter", "basic", "lite"] | None = None
    is_active: bool | None = None


def serialize_user(db: Session, user: User) -> dict:
    entitlement = SubscriptionService.ensure_entitlement(db, user.email, user.id)
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
    AuditService.record(db, admin.id, "admin.user_updated", "user", str(user.id), details={"roleChanged": request.role is not None, "planChanged": request.plan is not None, "activeChanged": request.is_active is not None})
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


@router.get("/overview")
def system_overview(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    guest = Analysis.guest_session_id.isnot(None)
    legacy = Analysis.owner_user_id.is_(None) & Analysis.guest_session_id.is_(None)
    return {
        "totalUsers": db.query(User).count(), "activeUsers": db.query(User).filter(User.is_active.is_(True)).count(),
        "newUsersToday": db.query(User).filter(User.created_at >= today).count(), "totalAnalyses": db.query(Analysis).count(),
        "analysesToday": db.query(Analysis).filter(Analysis.created_at >= today).count(), "failedAnalyses": db.query(Analysis).filter(Analysis.status.ilike("failed%" )).count(),
        "activeSubscriptions": db.query(AccountEntitlement).filter(AccountEntitlement.status == "active", AccountEntitlement.plan.in_(["basic", "lite"])).count(),
        "videoQueue": db.query(VideoJob).filter(VideoJob.status.in_(["pending", "queued"])).count(), "activeVideoJobs": db.query(VideoJob).filter(VideoJob.status == "processing").count(),
        "failedVideoJobs": db.query(VideoJob).filter(VideoJob.status == "failed").count(),
        "averageProcessingTime": db.query(func.avg(Analysis.processing_time)).scalar(),
        "ownedAnalyses": db.query(Analysis).filter(Analysis.owner_user_id.isnot(None)).count(),
        "guestAnalyses": db.query(Analysis).filter(guest).count(),
        "legacyAnalyses": db.query(Analysis).filter(legacy).count(),
        "imageAnalyses": db.query(Analysis).filter(Analysis.file_type.ilike("image")).count(),
        "videoAnalyses": db.query(Analysis).filter(Analysis.file_type.ilike("video")).count(),
        "webcamAnalyses": db.query(Analysis).filter(Analysis.source == "webcam").count(),
        "extensionAnalyses": db.query(Analysis).filter(Analysis.source.in_(["browser_extension_image", "browser_extension_video"])).count(),
    }


@router.get("/analyses")
def list_admin_analyses(
    ownership: Literal["all", "owned", "guest", "legacy"] = "all",
    status: str | None = None,
    source: str | None = None,
    media_type: str | None = None,
    prediction: str | None = None,
    owner_email: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(Analysis, User).outerjoin(User, Analysis.owner_user_id == User.id)
    if ownership == "owned": query = query.filter(Analysis.owner_user_id.isnot(None))
    elif ownership == "guest": query = query.filter(Analysis.guest_session_id.isnot(None))
    elif ownership == "legacy": query = query.filter(Analysis.owner_user_id.is_(None), Analysis.guest_session_id.is_(None))
    if status: query = query.filter(Analysis.status == status)
    if source: query = query.filter(Analysis.source == source)
    if media_type: query = query.filter(Analysis.file_type == media_type)
    if prediction: query = query.filter(Analysis.prediction == prediction)
    if owner_email: query = query.filter(User.email.ilike(f"%{owner_email}%"))
    if created_from: query = query.filter(Analysis.created_at >= created_from)
    if created_to: query = query.filter(Analysis.created_at <= created_to)
    total = query.count()
    ordering = Analysis.created_at.desc() if sort == "newest" else Analysis.created_at.asc()
    rows = query.order_by(ordering).offset((page - 1) * page_size).limit(page_size).all()
    AuditService.record(db, admin.id, "admin.analyses_listed", "analysis", details={"ownership": ownership, "page": page, "resultCount": len(rows)})
    db.commit()
    return {
        "items": [{
            "id": analysis.id,
            "createdAt": analysis.created_at,
            "mediaType": analysis.file_type,
            "source": analysis.source or "legacy",
            "prediction": analysis.prediction,
            "confidence": analysis.confidence,
            "status": analysis.status,
            "ownershipType": "owned" if analysis.owner_user_id is not None else "guest" if analysis.guest_session_id is not None else "legacy",
            "owner": user.email if user is not None else None,
            "modelName": analysis.model_name,
        } for analysis, user in rows],
        "page": page, "pageSize": page_size, "total": total,
    }


@router.get("/audit-events")
def audit_events(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    items = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(200).all()
    return [{"id": item.id, "actorUserId": item.actor_user_id, "action": item.action, "targetType": item.target_type, "targetId": item.target_id, "outcome": item.outcome, "details": item.details, "createdAt": item.created_at} for item in items]


@router.get("/model-metrics")
def model_metrics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = db.query(Analysis.model_name, func.count(Analysis.id), func.avg(Analysis.confidence)).group_by(Analysis.model_name).all()
    total = sum(row[1] for row in rows)
    output = []
    for name, count, confidence in rows:
        samples = db.query(Analysis).filter(Analysis.model_name == name, Analysis.verified_result.isnot(None)).all()
        tp = sum(item.prediction == "Fake" and item.verified_result == "Fake" for item in samples); tn = sum(item.prediction == "Real" and item.verified_result == "Real" for item in samples)
        fp = sum(item.prediction == "Fake" and item.verified_result == "Real" for item in samples); fn = sum(item.prediction == "Real" and item.verified_result == "Fake" for item in samples)
        precision = tp/(tp+fp) if tp+fp else None; recall = tp/(tp+fn) if tp+fn else None; specificity = tn/(tn+fp) if tn+fp else None
        f1 = 2*precision*recall/(precision+recall) if precision is not None and recall is not None and precision+recall else None
        output.append({"model": name, "usageCount": count, "usagePercentage": round(count/total*100,2) if total else 0, "averageConfidence": round(confidence or 0,2), "verifiedSamples": len(samples), "accuracy": round((tp+tn)/len(samples)*100,2) if samples else None, "precision": round(precision*100,2) if precision is not None else None, "recall": round(recall*100,2) if recall is not None else None, "f1Score": round(f1*100,2) if f1 is not None else None, "specificity": round(specificity*100,2) if specificity is not None else None, "falsePositiveRate": round((1-specificity)*100,2) if specificity is not None else None, "falseNegativeRate": round((1-recall)*100,2) if recall is not None else None, "rocAuc": None, "testLoss": None, "calibration": None, "confusionMatrix": {"truePositive":tp,"trueNegative":tn,"falsePositive":fp,"falseNegative":fn} if samples else None})
    return output


@router.get("/models")
def deployed_models(_: User = Depends(require_admin)):
    return {"models": [{**item, "metricsStatus": "unavailable", "checksumStatus": "unavailable"} for item in get_model_catalog()], "loadStatus": get_model_load_status()}
