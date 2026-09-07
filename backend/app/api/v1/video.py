from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal, get_analysis_principal
from app.core.database import get_db
from app.core.paths import VIDEO_FRAME_DIR, VIDEO_UPLOAD_DIR
from app.models.analysis import Analysis
from app.models.video_job import VideoJob
from app.repositories.analysis_repository import AnalysisRepository
from app.services.analysis_service import AnalysisService
from app.services.job_service import JobService
from app.services.protected_file_service import contained_file, remove_if_contained, safe_media_type
from app.services.subscription_service import SubscriptionService
from app.services.video_validation_service import VideoValidationService


router = APIRouter(prefix="/videos", tags=["Video Jobs"])


@router.post("", status_code=202)
async def create_video_job(
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    storage_key = f"user-{principal.owner_user_id}" if principal.owner_user_id else f"guest-{principal.guest_session_id}"
    validated = await VideoValidationService.validate_and_store(file, storage_key)
    try:
        usage = SubscriptionService.reserve(db, authorization, str(principal.guest_session_id) if principal.guest_session_id else None, "video")
    except HTTPException:
        validated.path.unlink(missing_ok=True)
        raise
    analysis = AnalysisService.save(
        db=db, filename=validated.original_filename, file_path=str(validated.path), file_type="Video",
        file_extension=validated.path.suffix, file_size=validated.size_mb, prediction="Inconclusive", confidence=0,
        risk_level="Unknown", model_name="EfficientNet-B0", model_version="pending", device="worker",
        processing_time=0, status="Queued", video_duration=validated.duration_seconds, frames_analyzed=0,
        fake_frames=0, real_frames=0, owner_user_id=principal.owner_user_id,
        guest_session_id=principal.guest_session_id, source="web",
    )
    job = VideoJob(
        id=str(uuid4()), analysis_id=analysis.id, owner_user_id=principal.owner_user_id,
        guest_session_id=principal.guest_session_id, status="pending", progress=0,
        current_stage="Validating video", original_filename=validated.original_filename,
        stored_file_key=str(validated.path), duration_seconds=validated.duration_seconds,
        width=validated.width, height=validated.height, fps=validated.fps, total_frames=validated.total_frames,
        metadata_json={"codec": validated.codec, "usage_reservation_key": usage.reservation_key},
    )
    db.add(job); db.commit(); db.refresh(job)
    try:
        JobService.enqueue(db, job)
    except HTTPException:
        SubscriptionService.release_key(db, usage.reservation_key)
        raise
    return JobService.serialize(job)


def owned_job(job_id: str, db: Session, principal: AnalysisPrincipal) -> VideoJob:
    job = JobService.accessible(db, job_id, principal)
    if job is None:
        raise HTTPException(status_code=404, detail="Video job not found.")
    return job


@router.get("/{job_id}")
@router.get("/{job_id}/status")
def job_status(job_id: str, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    return JobService.serialize(owned_job(job_id, db, principal))


@router.get("/{job_id}/frames")
def frames(job_id: str, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    job = owned_job(job_id, db, principal)
    return [{"id": item.id, "timestamp_ms": item.timestamp_ms, "frame_number": item.frame_number, "track_id": item.track_id, "quality_score": item.quality_score, "prediction": item.prediction, "fake_probability": item.fake_probability, "confidence": item.confidence, "sampling_reason": item.sampling_reason, "thumbnail_url": f"/videos/{job.id}/frames/{item.id}/thumbnail"} for item in JobService.frames(db, job.id)]


@router.get("/{job_id}/frames/{frame_id}/thumbnail")
def frame_thumbnail(job_id: str, frame_id: int, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    job = owned_job(job_id, db, principal)
    frame = next((item for item in JobService.frames(db, job.id) if item.id == frame_id), None)
    if frame is None or not frame.thumbnail_key:
        raise HTTPException(status_code=404, detail="Frame not found.")
    path = contained_file(frame.thumbnail_key, VIDEO_FRAME_DIR)
    return FileResponse(path, media_type=safe_media_type(path), filename=f"frame-{frame.id}.jpg", headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/{job_id}/tracks")
def tracks(job_id: str, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    job = owned_job(job_id, db, principal)
    return JobService.tracks(db, job.id)


@router.get("/{job_id}/segments")
def segments(job_id: str, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    job = owned_job(job_id, db, principal)
    return [{"id": item.id, "track_id": item.track_id, "start_timestamp_ms": item.start_timestamp_ms, "end_timestamp_ms": item.end_timestamp_ms, "result": item.result, "confidence": item.confidence, "frame_count": item.frame_count} for item in JobService.segments(db, job.id)]


@router.post("/{job_id}/cancel")
def cancel(job_id: str, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    job = owned_job(job_id, db, principal); JobService.request_cancel(db, job)
    return JobService.serialize(job)


@router.delete("/{job_id}")
def delete(job_id: str, db: Session = Depends(get_db), principal: AnalysisPrincipal = Depends(get_analysis_principal)):
    job = owned_job(job_id, db, principal)
    if job.status not in {"completed", "failed", "cancelled"}:
        raise HTTPException(status_code=409, detail="Cancel the active job before deleting it.")
    analysis = AnalysisRepository.get_accessible(db, job.analysis_id, principal)
    source = job.stored_file_key
    if analysis: db.delete(analysis)
    else: db.delete(job)
    db.commit()
    remove_if_contained(source, VIDEO_UPLOAD_DIR)
    frame_dir = (VIDEO_FRAME_DIR / job.id).resolve()
    if frame_dir.parent == VIDEO_FRAME_DIR.resolve(): shutil.rmtree(frame_dir, ignore_errors=True)
    return {"message": "Video job deleted."}
