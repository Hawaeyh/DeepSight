from datetime import datetime, timedelta
from pathlib import Path
import shutil
from loguru import logger

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.paths import REPORT_DIR, UPLOAD_DIR, VIDEO_FRAME_DIR
from app.models.analysis import Analysis
from app.models.guest_session import GuestSession
from app.models.video_job import VideoJob
from app.services.protected_file_service import remove_if_contained
from app.models.webcam_session import WebcamSession
from app.services.subscription_service import SubscriptionService


class CleanupService:
    @staticmethod
    def run(db: Session, apply: bool = False) -> dict:
        cutoff = datetime.utcnow() - timedelta(hours=settings.TEMPORARY_MEDIA_RETENTION_HOURS)
        expired_sessions = db.query(GuestSession).filter(GuestSession.expires_at < datetime.utcnow(), GuestSession.transferred_at.is_(None)).all()
        guest_analyses = db.query(Analysis).filter(Analysis.guest_session_id.in_([item.id for item in expired_sessions])).all() if expired_sessions else []
        stale_jobs = db.query(VideoJob).filter(VideoJob.status.in_(["failed", "cancelled"]), VideoJob.created_at < cutoff).all()
        stale_webcam_sessions = db.query(WebcamSession).filter(WebcamSession.status == "active", WebcamSession.started_at < cutoff).all()
        expired_analysis_ids = {item.id for item in guest_analyses}
        stale_jobs = [item for item in stale_jobs if item.analysis_id not in expired_analysis_ids]
        referenced_reports = {f"analysis_{item[0]}.pdf" for item in db.query(Analysis.id).all()}
        orphan_reports = [path for path in REPORT_DIR.glob("analysis_*.pdf") if path.name not in referenced_reports] if REPORT_DIR.exists() else []
        referenced_media = {Path(item[0]).resolve() for item in db.query(Analysis.file_path).all() if item[0]}
        referenced_media.update(Path(item[0]).resolve() for item in db.query(VideoJob.stored_file_key).all() if item[0])
        orphan_media = [path for path in UPLOAD_DIR.rglob("*") if path.is_file() and path.resolve() not in referenced_media and datetime.fromtimestamp(path.stat().st_mtime) < cutoff]
        report = {"mode": "apply" if apply else "dry-run", "expired_guest_sessions": len(expired_sessions), "expired_guest_analyses": len(guest_analyses), "stale_video_jobs": len(stale_jobs), "stale_webcam_sessions": len(stale_webcam_sessions), "orphan_media": len(orphan_media), "orphan_reports": len(orphan_reports), "deleted_files": 0, "errors": 0}
        if not apply:
            return report
        for analysis in guest_analyses:
            if remove_if_contained(analysis.file_path, UPLOAD_DIR): report["deleted_files"] += 1; logger.info("Cleanup removed expired guest media analysis_id={}", analysis.id)
            db.delete(analysis)
        for job in stale_jobs:
            # Failed/cancelled account history is permanent user data. Only its
            # derived temporary frames are eligible for retention cleanup.
            frame_dir = (VIDEO_FRAME_DIR / job.id).resolve()
            if frame_dir.parent == VIDEO_FRAME_DIR.resolve() and frame_dir.exists():
                try: shutil.rmtree(frame_dir); report["deleted_files"] += 1; logger.info("Cleanup removed derived frames job_id={}", job.id)
                except OSError: report["errors"] += 1; logger.exception("Cleanup could not remove derived frames job_id={}", job.id)
        for webcam in stale_webcam_sessions:
            SubscriptionService.release_key(db, webcam.usage_reservation_key); webcam.status = "cancelled"; webcam.ended_at = datetime.utcnow(); logger.info("Cleanup cancelled stale webcam session_id={}", webcam.id)
        for path in orphan_media:
            try:
                if remove_if_contained(str(path), UPLOAD_DIR): report["deleted_files"] += 1; logger.info("Cleanup removed orphan media name={}", path.name)
            except OSError: report["errors"] += 1; logger.exception("Cleanup could not remove orphan media name={}", path.name)
        for session in expired_sessions: db.delete(session)
        for path in orphan_reports:
            if remove_if_contained(str(path), REPORT_DIR): report["deleted_files"] += 1
        db.commit()
        return report
