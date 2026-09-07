from sqlalchemy import Engine, inspect

from app.core.config import settings
from app.core.database import Base, engine


def register_models() -> None:
    """Import every current ORM module into the shared migration metadata."""
    from app.models import analysis, extension_session, feedback, guest_session, notification, subscription, user, video_job, webcam_session  # noqa: F401


def initialize_test_database(target_engine: Engine | None = None) -> list[str]:
    """Create schema directly only for isolated tests; development uses Alembic."""
    if settings.APP_ENV != "testing":
        raise RuntimeError("Direct schema creation is restricted to APP_ENV=testing.")
    selected_engine = target_engine or engine
    register_models()
    Base.metadata.create_all(bind=selected_engine)
    return sorted(inspect(selected_engine).get_table_names())
