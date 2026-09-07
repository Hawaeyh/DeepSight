from celery import Celery

from app.core.config import settings


broker = settings.CELERY_BROKER_URL or settings.REDIS_URL or "redis://127.0.0.1:6379/0"
result_backend = settings.CELERY_RESULT_BACKEND or "redis://127.0.0.1:6379/1"
celery_app = Celery("deepsight", broker=broker, backend=result_backend)
celery_app.conf.update(
    task_track_started=True,
    task_time_limit=settings.VIDEO_TASK_TIME_LIMIT_SECONDS,
    task_soft_time_limit=settings.VIDEO_TASK_SOFT_TIME_LIMIT_SECONDS,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    timezone="UTC",
)
celery_app.autodiscover_tasks(["app.workers"])
if settings.CLEANUP_SCHEDULE_ENABLED:
    celery_app.conf.beat_schedule = {"cleanup-temporary-media": {"task": "deepsight.cleanup_temporary_media", "schedule": settings.CLEANUP_SCHEDULE_HOURS * 3600}}
