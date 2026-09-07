from datetime import datetime
from statistics import median
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai.model_status import ModelUnavailableError
from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.models.webcam_session import WebcamSession
from app.services.ai_service import AIService
from app.services.analysis_service import AnalysisService
from app.services.image_validation_service import ImageValidationService, upload_error
from app.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/webcam/sessions", tags=["Webcam"])


def owned(db: Session, session_id: str, user_id: int) -> WebcamSession:
    item = db.query(WebcamSession).filter(WebcamSession.id == session_id, WebcamSession.owner_user_id == user_id).first()
    if item is None: raise HTTPException(status_code=404, detail="Webcam session not found.")
    return item


@router.post("", status_code=201)
def start_session(authorization: str | None = Header(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    usage = SubscriptionService.reserve(db, authorization, None, "webcam", "live")
    item = WebcamSession(id=str(uuid4()), owner_user_id=user.id, usage_reservation_key=usage.reservation_key, status="active", predictions=[])
    db.add(item); db.commit(); db.refresh(item)
    return {"sessionId": item.id, "status": item.status, "startedAt": item.started_at}


@router.post("/{session_id}/frames")
async def analyze_frame(session_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned(db, session_id, user.id)
    if item.status != "active": raise HTTPException(status_code=409, detail="Webcam session is not active.")
    validated = await ImageValidationService.validate_and_store(file, f"webcam-{item.id}")
    if "Image appears blurry" in validated.warnings:
        validated.path.unlink(missing_ok=True)
        raise upload_error(422, "QUALITY_TOO_LOW", "The webcam frame is too blurry to analyse.")
    try:
        result = AIService.analyze_image(str(validated.path), "efficientnet")
    except ModelUnavailableError: raise upload_error(503, "MODEL_UNAVAILABLE", "The requested model is unavailable.") from None
    except Exception: raise upload_error(500, "INFERENCE_FAILED", "Webcam inference failed safely.") from None
    finally: validated.path.unlink(missing_ok=True)
    if not result.get("success"): raise upload_error(422, "NO_FACE_DETECTED", "No clear face was detected.")
    predictions = list(item.predictions or [])[-8:]
    predictions.append({"prediction": result["prediction"], "fakeProbability": result["fake_probability"], "confidence": result["confidence"], "quality": max(0.1, min(1.0, validated.quality["blur_variance"] / 300))})
    item.predictions = predictions; item.valid_frame_count += 1; db.commit()
    return {"prediction": result["prediction"], "confidence": result["confidence"], "fake_probability": result["fake_probability"], "face_box": result.get("selected_face_box"), "frame_width": validated.width, "frame_height": validated.height, "quality_warnings": validated.warnings, "valid_frames": item.valid_frame_count}


@router.post("/{session_id}/stop")
def stop_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned(db, session_id, user.id)
    if item.status == "completed": return {"sessionId": item.id, "analysisId": item.analysis_id, "result": item.final_result, "confidence": item.final_confidence}
    values = item.predictions or []
    if not values:
        item.status = "cancelled"; item.ended_at = datetime.utcnow(); SubscriptionService.release_key(db, item.usage_reservation_key); db.commit()
        return {"sessionId": item.id, "status": "cancelled", "analysisId": None}
    fake_probability = median(entry["fakeProbability"] for entry in values)
    if 45 <= fake_probability <= 55: result, prediction, confidence = "inconclusive", "Inconclusive", 100 - abs(50 - fake_probability)
    elif fake_probability >= 65: result, prediction, confidence = "likely_manipulated", "Fake", fake_probability
    else: result, prediction, confidence = "likely_real", "Real", 100 - fake_probability
    analysis = AnalysisService.save(db=db, filename=f"Webcam session {item.started_at.isoformat()}", file_path=f"webcam-session/{item.id}", file_type="Webcam", prediction=prediction, confidence=confidence, fake_probability=fake_probability, real_probability=100-fake_probability, risk_level="High" if prediction == "Fake" else "Low" if prediction == "Real" else "Unknown", model_name="EfficientNet-B0", model_version="Binary V2", device="session", processing_time=max(0, (datetime.utcnow()-item.started_at).total_seconds()), status="Completed", face_detected=True, face_count=1, frames_analyzed=item.valid_frame_count, owner_user_id=user.id, source="webcam")
    item.status = "completed"; item.final_result = result; item.final_confidence = confidence; item.analysis_id = analysis.id; item.ended_at = datetime.utcnow(); SubscriptionService.complete_key(db, item.usage_reservation_key); db.commit()
    return {"sessionId": item.id, "status": item.status, "analysisId": item.analysis_id, "result": result, "confidence": confidence}
