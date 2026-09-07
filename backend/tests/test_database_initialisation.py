from sqlalchemy import inspect

from app.core.config import settings
from app.core.database import engine
from app.database.initialization import initialize_test_database


def test_database_schema_is_created_only_by_explicit_initialisation() -> None:
    assert settings.APP_ENV == "testing"
    tables = initialize_test_database()

    assert {"users", "analysis", "analysis_feedback"}.issubset(tables)
    assert set(tables) == set(inspect(engine).get_table_names())
