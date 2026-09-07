from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal, get_analysis_principal
from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.subscription import AccountEntitlement, SubscriptionPlan
from app.repositories.analysis_repository import AnalysisRepository
from app.services.notification_service import AuditService
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{analysis_id}")
def report(
    analysis_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    analysis = AnalysisRepository.get_accessible(db, analysis_id, principal)
    if analysis is None and principal.user is not None and principal.user.role == "admin":
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis is not None:
            AuditService.record(db, principal.user.id, "admin.report_downloaded", "analysis", str(analysis.id))
            db.commit()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if principal.guest_session is not None:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == "guest").first()
    elif principal.user is not None and principal.user.role != "admin":
        entitlement = db.query(AccountEntitlement).filter(AccountEntitlement.user_id == principal.user.id).first()
        plan_code = entitlement.plan if entitlement else "starter"
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == plan_code).first()
    else:
        plan = None
    if plan is not None and not plan.report_enabled:
        raise HTTPException(status_code=403, detail={"code": "REPORT_PLAN_REQUIRED", "message": "Your current plan does not include report downloads."})
    pdf = ReportService.create(analysis, db)
    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename=f"deepsight-analysis-{analysis.id}.pdf",
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"},
    )
