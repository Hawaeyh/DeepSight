from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.core.database import Base
from app.database.initialization import register_models


def test_migrated_schema_matches_registered_models(migrated_database):
    _, engine = migrated_database
    register_models()
    with engine.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    assert differences == []
