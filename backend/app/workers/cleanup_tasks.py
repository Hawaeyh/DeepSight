from app.core.database import SessionLocal
from app.services.cleanup_service import CleanupService
from app.workers.celery_app import celery_app


@celery_app.task(name="deepsight.cleanup_temporary_media")
def cleanup_temporary_media() -> dict:
    db = SessionLocal()
    try:
        return CleanupService.run(db, apply=True)
    finally:
        db.close()
