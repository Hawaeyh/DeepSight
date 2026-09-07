from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal, get_analysis_principal, get_current_user
from app.api.v1.feedback import FeedbackRequest
from app.core.database import get_db
from app.core.paths import REPORT_DIR, UPLOAD_DIR
from app.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisResponse
from app.services.feedback_service import FeedbackService
from app.services.firebase_service import FirebaseService
from app.services.protected_file_service import remove_if_contained
from app.services.report_service import ReportService


router = APIRouter(prefix="/analyses", tags=["Owned Analyses"])


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    analysis = AnalysisRepository.get_accessible(db, analysis_id, principal)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@router.delete("/{analysis_id}")
def delete(
    analysis_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    analysis = AnalysisRepository.delete_accessible(db, analysis_id, principal)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    FirebaseService.delete_analysis(analysis_id)
    remove_if_contained(analysis.file_path, UPLOAD_DIR)
    remove_if_contained(str(REPORT_DIR / f"analysis_{analysis.id}.pdf"), REPORT_DIR)
    return {"message": "Analysis deleted successfully."}


@router.post("/{analysis_id}/feedback")
def feedback(
    analysis_id: int,
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    analysis = AnalysisRepository.get_owned(db, analysis_id, user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    created = FeedbackService.create(
        db,
        analysis,
        is_correct=request.is_correct,
        corrected_prediction=request.corrected_prediction,
        fake_category=request.fake_category,
        manipulation_type=request.manipulation_type,
        owner_user_id=user.id,
    )
    return {"id": created.id, "status": created.status}


@router.api_route("/{analysis_id}/report", methods=["GET", "POST"])
def report(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    analysis = AnalysisRepository.get_owned(db, analysis_id, user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    path = ReportService.create(analysis)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"deepsight-analysis-{analysis.id}.pdf",
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"},
    )
