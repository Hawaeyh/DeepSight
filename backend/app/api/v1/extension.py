from urllib.parse import urlsplit
from datetime import datetime
from statistics import median
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal, get_current_user
from app.api.v1.analysis import analyze_image
from app.core.database import get_db
from app.models.user import User
from app.models.extension_session import ExtensionVideoSession
from app.ai.model_status import MODEL_SPECS, ModelUnavailableError
from app.core.config import settings
from app.services.ai_service import AIService
from app.services.analysis_service import AnalysisService
from app.services.image_validation_service import ImageValidationService
from app.services.subscription_service import SubscriptionService
from app.services.report_service import ReportService


router = APIRouter(prefix="/extension", tags=["Browser Extension"])


class ExtensionSessionCreate(BaseModel):
    page_domain: str = Field(min_length=1, max_length=253)
    model_id: str = "efficientnet"


def valid_domain(value: str) -> str:
    normalized = value.strip().lower()
    parsed = urlsplit(f"//{normalized}")
    if parsed.hostname != normalized or parsed.port is not None or parsed.username is not None:
        raise HTTPException(status_code=422, detail={"code": "INVALID_PAGE_DOMAIN", "message": "A valid page hostname is required."})
    return normalized


def owned_session(db: Session, session_id: str, user_id: int) -> ExtensionVideoSession:
    item = db.query(ExtensionVideoSession).filter(ExtensionVideoSession.id == session_id, ExtensionVideoSession.owner_user_id == user_id).first()
    if item is None: raise HTTPException(status_code=404, detail="Extension session not found.")
    return item


def serialize_session(item: ExtensionVideoSession) -> dict:
    duration = ((item.completed_at or datetime.utcnow()) - item.started_at).total_seconds()
    return {"sessionId": item.id, "status": item.status, "selectedModelId": item.selected_model_id, "actualModelId": item.actual_model_id, "pageDomain": item.page_domain, "durationSeconds": round(max(0, duration), 1), "framesReceived": item.frames_received, "framesAnalysed": item.frames_analysed, "framesSkipped": item.frames_skipped, "suspiciousFrames": item.suspicious_frames, "overallResult": item.overall_result, "overallConfidence": item.overall_confidence, "analysisId": item.analysis_id, "failureCode": item.failure_code}


@router.post("/video-sessions", status_code=201)
def create_video_session(request: ExtensionSessionCreate, authorization: str | None = Header(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    spec = MODEL_SPECS.get(request.model_id)
    if spec is None or not spec["checkpoint"].is_file(): raise HTTPException(status_code=503, detail={"code": "MODEL_UNAVAILABLE", "message": "The selected model is currently unavailable."})
    usage = SubscriptionService.reserve(db, authorization, None, "extension", "extension-video")
    item = ExtensionVideoSession(id=str(uuid4()), owner_user_id=user.id, usage_reservation_key=usage.reservation_key, selected_model_id=request.model_id, actual_model_id=request.model_id, page_domain=valid_domain(request.page_domain), status="analysing", predictions=[])
    db.add(item); db.commit(); db.refresh(item)
    return serialize_session(item)


@router.post("/video-sessions/{session_id}/frames")
async def session_frame(session_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_session(db, session_id, user.id)
    if item.status != "analysing": raise HTTPException(status_code=409, detail={"code": "SESSION_NOT_ACTIVE", "message": "The extension session is not actively analysing."})
    if (datetime.utcnow() - item.started_at).total_seconds() > settings.EXTENSION_VIDEO_MAX_SESSION_SECONDS or item.frames_received >= settings.EXTENSION_VIDEO_MAX_FRAMES:
        raise HTTPException(status_code=409, detail={"code": "SESSION_LIMIT_REACHED", "message": "The continuous detection session reached its configured limit."})
    item.frames_received += 1
    validated = await ImageValidationService.validate_and_store(file, f"extension-session-{item.id}")
    try:
        result = AIService.analyze_image(str(validated.path), item.selected_model_id)
    except ModelUnavailableError:
        raise HTTPException(status_code=503, detail={"code": "MODEL_UNAVAILABLE", "message": "The selected model is currently unavailable."}) from None
    except Exception:
        raise HTTPException(status_code=500, detail={"code": "INFERENCE_FAILED", "message": "The sampled frame could not be analysed."}) from None
    finally:
        validated.path.unlink(missing_ok=True)
    if not result.get("success"):
        item.frames_skipped += 1; db.commit(); return {"status": "skipped", "reason": "NO_FACE_DETECTED", **serialize_session(item)}
    predictions = list(item.predictions or [])
    predictions.append({"timestampMs": int((datetime.utcnow() - item.started_at).total_seconds() * 1000), "prediction": result["prediction"], "fakeProbability": float(result["fake_probability"]), "confidence": float(result["confidence"]), "quality": validated.quality})
    item.predictions = predictions[-settings.EXTENSION_VIDEO_MAX_FRAMES:]
    item.frames_analysed += 1
    item.suspicious_frames = sum(entry["fakeProbability"] >= 55 for entry in item.predictions)
    probabilities = [entry["fakeProbability"] for entry in item.predictions[-9:]]
    fake_probability = median(probabilities)
    item.overall_result = "analysing" if len(probabilities) < 3 else "likely_manipulated" if fake_probability >= 60 else "likely_real" if fake_probability <= 40 else "inconclusive"
    item.overall_confidence = None if item.overall_result == "analysing" else round(max(fake_probability, 100 - fake_probability), 2)
    db.commit()
    return {"status": "analysed", "prediction": result["prediction"], "confidence": result["confidence"], "fakeProbability": result["fake_probability"], **serialize_session(item)}


@router.get("/video-sessions/{session_id}")
def get_video_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return serialize_session(owned_session(db, session_id, user.id))


@router.post("/video-sessions/{session_id}/pause")
def pause_video_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_session(db, session_id, user.id)
    if item.status == "analysing": item.status = "paused"; db.commit()
    return serialize_session(item)


@router.post("/video-sessions/{session_id}/resume")
def resume_video_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_session(db, session_id, user.id)
    if item.status != "paused": raise HTTPException(status_code=409, detail="Only a paused session can resume.")
    item.status = "analysing"; db.commit(); return serialize_session(item)


@router.post("/video-sessions/{session_id}/complete")
def complete_video_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_session(db, session_id, user.id)
    if item.status == "completed": return serialize_session(item)
    if not item.predictions:
        item.status = "cancelled"; item.completed_at = datetime.utcnow(); SubscriptionService.release_key(db, item.usage_reservation_key); db.commit(); return serialize_session(item)
    fake_probability = median(entry["fakeProbability"] for entry in item.predictions)
    prediction = "Fake" if fake_probability >= 55 else "Real"
    confidence = max(fake_probability, 100 - fake_probability)
    analysis = AnalysisService.save(db=db, filename=f"Extension video session on {item.page_domain}", file_path=f"extension-session/{item.id}", file_type="Video", prediction=prediction, confidence=confidence, real_probability=100-fake_probability, fake_probability=fake_probability, risk_level="High" if prediction == "Fake" else "Low", model_name=MODEL_SPECS[item.actual_model_id]["name"], model_version=MODEL_SPECS[item.actual_model_id]["version"], device="extension-session", processing_time=(datetime.utcnow()-item.started_at).total_seconds(), face_detected=True, face_count=1, frames_analyzed=item.frames_analysed, fake_frames=item.suspicious_frames, real_frames=item.frames_analysed-item.suspicious_frames, owner_user_id=user.id, source="browser_extension_video", remarks=f"Sampled continuous detection session for {item.page_domain}")
    item.analysis_id = analysis.id; item.status = "completed"; item.completed_at = datetime.utcnow(); item.overall_result = analysis.result; item.overall_confidence = confidence
    SubscriptionService.complete_key(db, item.usage_reservation_key); db.commit(); return serialize_session(item)


@router.post("/video-sessions/{session_id}/cancel")
def cancel_video_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_session(db, session_id, user.id)
    if item.status not in {"completed", "cancelled"}: item.status = "cancelled"; item.completed_at = datetime.utcnow(); SubscriptionService.release_key(db, item.usage_reservation_key); db.commit()
    return serialize_session(item)


@router.get("/video-sessions/{session_id}/report")
def extension_session_report(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = owned_session(db, session_id, user.id)
    if item.status != "completed" or not item.analysis_id: raise HTTPException(status_code=409, detail={"code": "REPORT_NOT_READY", "message": "Complete the session before downloading its report."})
    from app.models.analysis import Analysis
    analysis = db.query(Analysis).filter(Analysis.id == item.analysis_id).one()
    pdf = ReportService.create(analysis, db)
    return FileResponse(pdf, media_type="application/pdf", filename=f"deepsight-extension-session-{item.id}.pdf", headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/video-sessions")
def recent_video_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [serialize_session(item) for item in db.query(ExtensionVideoSession).filter(ExtensionVideoSession.owner_user_id == user.id).order_by(ExtensionVideoSession.started_at.desc()).limit(5).all()]


@router.post("/videos/frames", status_code=201)
async def analyze_video_frame(
    file: UploadFile = File(...),
    page_domain: str = Form(..., min_length=1, max_length=253),
    model: str = Form("efficientnet"),
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Accept a hostname, never an arbitrary full private browsing URL.
    parsed = urlsplit(f"//{page_domain}")
    if parsed.hostname != page_domain.lower() or parsed.port is not None or parsed.username is not None:
        raise HTTPException(status_code=422, detail={"code": "INVALID_PAGE_DOMAIN", "message": "A valid page hostname is required."})
    result = await analyze_image(
        file=file,
        model=model,
        authorization=authorization,
        x_deepsight_client="extension-video",
        db=db,
        principal=AnalysisPrincipal(user=user),
    )
    result.source = "browser_extension_video"
    result.remarks = f"Sampled webpage video frame from {page_domain.lower()}"
    db.commit()
    db.refresh(result)
    return result
