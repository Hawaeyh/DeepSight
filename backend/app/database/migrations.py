from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import Engine
from sqlalchemy.engine import URL, make_url

from app.core.config import BACKEND_DIR, settings
from app.core.database import engine


def get_alembic_config(database_url: str | URL | None = None) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    url = make_url(database_url or settings.DATABASE_URL)
    config.set_main_option(
        "sqlalchemy.url",
        url.render_as_string(hide_password=False).replace("%", "%%"),
    )
    return config


def upgrade_database(revision: str = "head", database_url: str | URL | None = None) -> None:
    command.upgrade(get_alembic_config(database_url), revision)


def downgrade_database(revision: str, database_url: str | URL | None = None) -> None:
    command.downgrade(get_alembic_config(database_url), revision)


def stamp_database(revision: str, database_url: str | URL | None = None) -> None:
    command.stamp(get_alembic_config(database_url), revision)


def current_revision(target_engine: Engine | None = None) -> str | None:
    with (target_engine or engine).connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()
