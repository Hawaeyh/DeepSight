from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal, get_current_user
from app.core.database import get_db
from app.core.paths import REPORT_DIR, UPLOAD_DIR
from app.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisResponse
from app.services.firebase_service import FirebaseService
from app.services.protected_file_service import remove_if_contained


router = APIRouter(prefix="/history", tags=["History"])


class VerificationRequest(BaseModel):
    verified_result: Literal["Real", "Fake"]
    remarks: str | None = None


@router.get("", response_model=list[AnalysisResponse])
def history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return AnalysisRepository.list_owned(db, user.id)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    analysis = AnalysisRepository.get_owned(db, analysis_id, user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@router.delete("/{analysis_id}")
def delete(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    principal = AnalysisPrincipal(user=user)
    analysis = AnalysisRepository.delete_accessible(db, analysis_id, principal)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    FirebaseService.delete_analysis(analysis_id)
    remove_if_contained(analysis.file_path, UPLOAD_DIR)
    remove_if_contained(str(REPORT_DIR / f"analysis_{analysis.id}.pdf"), REPORT_DIR)
    return {"message": "Deleted successfully."}


@router.patch("/{analysis_id}/verify", response_model=AnalysisResponse)
def verify(
    analysis_id: int,
    request: VerificationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    analysis = AnalysisRepository.get_owned(db, analysis_id, user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    analysis.verified_result = request.verified_result
    analysis.remarks = request.remarks
    db.commit()
    db.refresh(analysis)
    FirebaseService.save_analysis(analysis)
    return analysis
