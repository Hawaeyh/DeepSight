from pathlib import Path

from fastapi import APIRouter

from app.ai.model_status import get_model_load_status
from app.core.config import settings
from app.core.database import check_database_connection
from app.core.paths import UPLOAD_DIR
from app.auth.firebase import firebase_status
from app.services.stripe_service import StripeService


router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    try:
        check_database_connection()
        database_status = "ok"
    except Exception:
        database_status = "unavailable"

    return {
        "status": "ok" if database_status == "ok" else "degraded",
        "environment": settings.APP_ENV,
        "database": database_status,
        "models": get_model_load_status(),
        "version": settings.APP_VERSION,
    }


@router.get("/health/models")
def model_health():
    return {"status": "ok", "models": get_model_load_status()}


@router.get("/health/database")
def database_health():
    try: check_database_connection(); return {"status": "ok"}
    except Exception: return {"status": "unavailable"}


@router.get("/health/storage")
def storage_health():
    try:
        root = UPLOAD_DIR.resolve()
        parent = root if root.exists() else root.parent
        status = "ok" if parent.exists() and parent.is_dir() else "unavailable"
    except OSError:
        status = "unavailable"
    return {"status": status}


@router.get("/health/worker")
def worker_health():
    if not (settings.CELERY_BROKER_URL or settings.REDIS_URL):
        return {"status": "not_configured", "development_fallback": settings.APP_ENV == "development" and settings.VIDEO_BACKGROUND_FALLBACK_ENABLED}
    try:
        from app.workers.celery_app import celery_app
        replies = celery_app.control.ping(timeout=0.5)
        return {"status": "ok" if replies else "unavailable"}
    except Exception:
        return {"status": "unavailable"}


@router.get("/health/redis")
def redis_health():
    url = settings.REDIS_URL or settings.CELERY_BROKER_URL
    if not url: return {"status": "not_configured"}
    try:
        from redis import Redis
        return {"status": "ok" if Redis.from_url(url, socket_connect_timeout=0.5, socket_timeout=0.5).ping() else "unavailable"}
    except Exception: return {"status": "unavailable"}


@router.get("/health/payments")
def payment_health():
    return StripeService.status()


@router.get("/health/firebase")
def firebase_health():
    return firebase_status()
