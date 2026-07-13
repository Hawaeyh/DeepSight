from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import Analysis
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    analysis_id: int
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
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    feedback = FeedbackService.create(
        db,
        analysis,
        is_correct=request.is_correct,
        corrected_prediction=request.corrected_prediction,
        fake_category=request.fake_category,
        manipulation_type=request.manipulation_type,
    )
    return {
        "id": feedback.id,
        "status": feedback.status,
        "hardExamplePath": feedback.hard_example_path,
    }


@router.get("/hard-examples")
def hard_examples(db: Session = Depends(get_db)):
    return FeedbackService.list_hard_examples(db)
