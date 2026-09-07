from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal
from app.models.video_job import VideoFaceTrack, VideoFrame, VideoJob, VideoSegment
from app.core.config import settings
from app.services.subscription_service import SubscriptionService


_development_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="deepsight-video")


class JobService:
    @staticmethod
    def accessible(db: Session, job_id: str, principal: AnalysisPrincipal) -> VideoJob | None:
        query = db.query(VideoJob).filter(VideoJob.id == job_id)
        if principal.owner_user_id is not None:
            query = query.filter(VideoJob.owner_user_id == principal.owner_user_id)
        else:
            query = query.filter(VideoJob.guest_session_id == principal.guest_session_id)
        return query.first()

    @staticmethod
    def enqueue(db: Session, job: VideoJob) -> None:
        from app.workers.video_tasks import process_video_task

        try:
            if not (settings.CELERY_BROKER_URL or settings.REDIS_URL):
                raise ConnectionError("Celery broker is not configured")
            task = process_video_task.delay(job.id)
        except Exception:
            if settings.APP_ENV == "development" and settings.VIDEO_BACKGROUND_FALLBACK_ENABLED:
                job.task_id = f"local-{uuid4()}"
                job.status = "queued"
                job.current_stage = "Queued (development background executor)"
                job.metadata_json = {**(job.metadata_json or {}), "execution_backend": "development_background_executor"}
                db.commit()
                _development_executor.submit(process_video_task.run, job.id)
                return
            job.status = "failed"
            job.error_code = "WORKER_UNAVAILABLE"
            job.error_message_safe = "The video worker is unavailable."
            db.commit()
            raise HTTPException(status_code=503, detail={"code": "WORKER_UNAVAILABLE", "message": "The video worker is unavailable."}) from None
        job.task_id = task.id
        job.status = "queued"
        job.current_stage = "Queued"
        db.commit()

    @staticmethod
    def serialize(job: VideoJob) -> dict:
        return {
            "job_id": job.id, "analysis_id": job.analysis_id, "status": job.status,
            "progress": min(max(job.progress, 0), 100), "stage": job.current_stage,
            "processed_frames": job.processed_frame_count, "selected_frames": job.selected_frame_count,
            "detected_tracks": job.detected_track_count, "result": job.overall_result,
            "overall_confidence": job.overall_confidence, "primary_track_id": job.primary_track_id,
            "error_code": job.error_code, "error_message": job.error_message_safe,
            "metadata": job.metadata_json, "created_at": job.created_at,
            "started_at": job.started_at, "completed_at": job.completed_at, "cancelled_at": job.cancelled_at,
        }

    @staticmethod
    def request_cancel(db: Session, job: VideoJob) -> None:
        if job.status in {"completed", "failed", "cancelled"}:
            raise HTTPException(status_code=409, detail="The job is no longer cancellable.")
        queued = job.status in {"pending", "queued"}
        job.status = "cancelled" if queued else "cancel_requested"
        job.current_stage = "Cancelled" if queued else "Cancellation requested"
        if queued:
            job.cancelled_at = datetime.utcnow()
            SubscriptionService.release_key(db, (job.metadata_json or {}).get("usage_reservation_key"))
        db.commit()
        if job.task_id:
            try:
                from app.workers.celery_app import celery_app
                celery_app.control.revoke(job.task_id, terminate=False)
            except Exception:
                pass

    @staticmethod
    def frames(db: Session, job_id: str):
        return db.query(VideoFrame).filter(VideoFrame.video_job_id == job_id).order_by(VideoFrame.timestamp_ms).all()

    @staticmethod
    def tracks(db: Session, job_id: str):
        return db.query(VideoFaceTrack).filter(VideoFaceTrack.video_job_id == job_id).order_by(VideoFaceTrack.track_number).all()

    @staticmethod
    def segments(db: Session, job_id: str):
        return db.query(VideoSegment).filter(VideoSegment.video_job_id == job_id).order_by(VideoSegment.start_timestamp_ms).all()
