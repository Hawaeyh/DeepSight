from datetime import date, datetime
from pathlib import Path
from threading import Lock

from loguru import logger

from app.core.config import settings


class FirebaseService:
    _client = None
    _error: str | None = None
    _lock = Lock()

    @classmethod
    def _initialize(cls):
        if not settings.FIREBASE_ENABLED:
            cls._error = "Firebase is disabled in this environment."
            return None

        if cls._client is not None or cls._error is not None:
            return cls._client

        with cls._lock:
            if cls._client is not None or cls._error is not None:
                return cls._client

            credentials_path = settings.FIREBASE_CREDENTIALS_PATH
            project_id = settings.FIREBASE_PROJECT_ID
            if not credentials_path and not project_id:
                cls._error = "Firebase is not configured."
                return None

            try:
                import firebase_admin
                from firebase_admin import credentials, firestore

                if not firebase_admin._apps:
                    options = {"projectId": project_id} if project_id else None
                    if credentials_path:
                        path = Path(credentials_path).expanduser()
                        if not path.is_file():
                            raise FileNotFoundError(f"Firebase credentials not found: {path}")
                        firebase_admin.initialize_app(credentials.Certificate(path), options)
                    else:
                        firebase_admin.initialize_app(options=options)
                cls._client = firestore.client()
            except Exception as error:
                cls._error = str(error)
                logger.warning("Firebase initialization failed: {}", error)

        return cls._client

    @staticmethod
    def _serialize(analysis) -> dict:
        data = {
            column.name: getattr(analysis, column.name)
            for column in analysis.__table__.columns
        }
        return {
            key: value.isoformat() if isinstance(value, (datetime, date)) else value
            for key, value in data.items()
        }

    @classmethod
    def save_analysis(cls, analysis) -> bool:
        client = cls._initialize()
        if client is None:
            return False
        try:
            client.collection(settings.FIREBASE_COLLECTION).document(str(analysis.id)).set(
                cls._serialize(analysis)
            )
            return True
        except Exception as error:
            cls._error = str(error)
            logger.warning("Firebase write failed: {}", error)
            return False

    @classmethod
    def delete_analysis(cls, analysis_id: int) -> bool:
        client = cls._initialize()
        if client is None:
            return False
        try:
            client.collection(settings.FIREBASE_COLLECTION).document(str(analysis_id)).delete()
            return True
        except Exception as error:
            cls._error = str(error)
            logger.warning("Firebase delete failed: {}", error)
            return False

    @classmethod
    def save_feedback(cls, feedback) -> bool:
        client = cls._initialize()
        if client is None:
            return False
        try:
            collection = f"{settings.FIREBASE_COLLECTION}_feedback"
            client.collection(collection).document(str(feedback.id)).set(
                cls._serialize(feedback)
            )
            return True
        except Exception as error:
            cls._error = str(error)
            logger.warning("Firebase feedback write failed: {}", error)
            return False

    @classmethod
    def status(cls) -> dict:
        client = cls._initialize()
        return {
            "configured": bool(settings.FIREBASE_CREDENTIALS_PATH or settings.FIREBASE_PROJECT_ID),
            "connected": client is not None,
            "projectId": settings.FIREBASE_PROJECT_ID,
            "collection": settings.FIREBASE_COLLECTION,
            "error": cls._error,
        }
