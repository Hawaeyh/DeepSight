from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    analysis_id: int | None = None
    is_correct: bool
    corrected_prediction: Literal["Real", "Fake"] | None = None
    fake_category: Literal["AI-generated", "Deepfake"] | None = None
    manipulation_type: str | None = None

    @model_validator(mode="after")
    def validate_correction(self):
        if not self.is_correct and self.corrected_prediction is None:
            raise ValueError("A corrected prediction is required for an incorrect result.")
        if self.corrected_prediction == "Fake" and not self.fake_category:
            raise ValueError("Choose AI-generated or Deepfake for a corrected fake result.")
        return self


@router.post("")
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    analysis = AnalysisRepository.get_owned(db, request.analysis_id, user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    feedback = FeedbackService.create(
        db,
        analysis,
        is_correct=request.is_correct,
        corrected_prediction=request.corrected_prediction,
        fake_category=request.fake_category,
        manipulation_type=request.manipulation_type,
        owner_user_id=user.id,
    )
    return {
        "id": feedback.id,
        "status": feedback.status,
        "hardExamplePath": feedback.hard_example_path,
    }


@router.get("/hard-examples")
def hard_examples(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return [
        {
            "id": item.id,
            "analysis_id": item.analysis_id,
            "corrected_prediction": item.corrected_prediction,
            "fake_category": item.fake_category,
            "manipulation_type": item.manipulation_type,
            "status": item.status,
            "created_at": item.created_at,
        }
        for item in FeedbackService.list_hard_examples(db)
    ]
