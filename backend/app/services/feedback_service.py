import json
import re
import shutil
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.paths import HARD_EXAMPLE_DIR
from app.models.analysis import Analysis
from app.models.feedback import AnalysisFeedback
from app.services.firebase_service import FirebaseService


class FeedbackService:
    @staticmethod
    def _slug(value: str | None, fallback: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", (value or fallback).lower()).strip("-")
        return normalized or fallback

    @staticmethod
    def create(
        db: Session,
        analysis: Analysis,
        *,
        is_correct: bool,
        corrected_prediction: str | None,
        fake_category: str | None,
        manipulation_type: str | None,
    ) -> AnalysisFeedback:
        verified_result = analysis.prediction if is_correct else corrected_prediction
        analysis.verified_result = verified_result

        hard_example_path = None
        if not is_correct:
            source = Path(analysis.file_path)
            if source.is_file():
                category_label = fake_category if corrected_prediction == "Fake" else "Real"
                manipulation_label = manipulation_type if corrected_prediction == "Fake" else "False positive"
                category = FeedbackService._slug(category_label, "unknown-category")
                manipulation = FeedbackService._slug(manipulation_label, "unknown-manipulation")
                destination_dir = HARD_EXAMPLE_DIR / category / manipulation
                destination_dir.mkdir(parents=True, exist_ok=True)
                destination = destination_dir / f"analysis-{analysis.id}-{uuid4().hex}{source.suffix.lower()}"
                shutil.copy2(source, destination)
                hard_example_path = str(destination)

                manifest = {
                    "analysisId": analysis.id,
                    "sourceFilename": analysis.filename,
                    "sourcePrediction": analysis.prediction,
                    "correctedPrediction": corrected_prediction,
                    "fakeCategory": fake_category,
                    "manipulationType": manipulation_type,
                    "modelName": analysis.model_name,
                    "modelVersion": analysis.model_version,
                    "hardExamplePath": hard_example_path,
                }
                destination.with_suffix(destination.suffix + ".json").write_text(
                    json.dumps(manifest, indent=2),
                    encoding="utf-8",
                )

        feedback = AnalysisFeedback(
            analysis_id=analysis.id,
            is_correct=is_correct,
            corrected_prediction=corrected_prediction,
            fake_category=fake_category,
            manipulation_type=manipulation_type,
            original_file_path=analysis.file_path,
            hard_example_path=hard_example_path,
            status="queued_for_retraining" if not is_correct else "verified",
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        db.refresh(analysis)

        FirebaseService.save_analysis(analysis)
        FirebaseService.save_feedback(feedback)
        return feedback

    @staticmethod
    def list_hard_examples(db: Session):
        return (
            db.query(AnalysisFeedback)
            .filter(AnalysisFeedback.is_correct.is_(False))
            .order_by(AnalysisFeedback.created_at.desc())
            .all()
        )
