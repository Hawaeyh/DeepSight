from app.core.config import settings
from pathlib import Path


class FirebaseNotConfiguredError(RuntimeError):
    pass


def firebase_status() -> dict:
    configured = bool(settings.FIREBASE_ADMIN_ENABLED and settings.FIREBASE_PROJECT_ID and (settings.FIREBASE_CREDENTIALS_PATH or (settings.FIREBASE_CLIENT_EMAIL and settings.FIREBASE_PRIVATE_KEY)))
    if not configured:
        return {"status": "not_configured", "projectId": None}
    if settings.FIREBASE_CREDENTIALS_PATH and not Path(settings.FIREBASE_CREDENTIALS_PATH).is_file():
        return {"status": "failed", "projectId": settings.FIREBASE_PROJECT_ID}
    try:
        _firebase_app()
        return {"status": "ok", "projectId": settings.FIREBASE_PROJECT_ID}
    except Exception:
        return {"status": "failed", "projectId": settings.FIREBASE_PROJECT_ID}


def _firebase_app():
    configured = bool(settings.FIREBASE_ADMIN_ENABLED and settings.FIREBASE_PROJECT_ID and (settings.FIREBASE_CREDENTIALS_PATH or (settings.FIREBASE_CLIENT_EMAIL and settings.FIREBASE_PRIVATE_KEY)))
    if not configured: raise FirebaseNotConfiguredError
    import firebase_admin
    from firebase_admin import credentials
    try: return firebase_admin.get_app("deepsight-auth")
    except ValueError: pass
    if settings.FIREBASE_CREDENTIALS_PATH:
        credential = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    else:
        credential = credentials.Certificate({"type": "service_account", "project_id": settings.FIREBASE_PROJECT_ID, "client_email": settings.FIREBASE_CLIENT_EMAIL, "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"), "token_uri": "https://oauth2.googleapis.com/token"})
    return firebase_admin.initialize_app(credential, {"projectId": settings.FIREBASE_PROJECT_ID}, name="deepsight-auth")


def verify_firebase_token(token: str) -> dict:
    from firebase_admin import auth
    return auth.verify_id_token(token, app=_firebase_app(), check_revoked=True)
