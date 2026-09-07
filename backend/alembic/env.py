from logging.config import fileConfig

from alembic import context

from app.core.config import settings
from app.core.database import create_database_engine
from app.database.initialization import register_models


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

register_models()
from app.core.database import Base  # noqa: E402

target_metadata = Base.metadata
database_url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL


def configuration_options(connection=None) -> dict:
    options = {
        "target_metadata": target_metadata,
        "compare_type": True,
        "compare_server_default": True,
    }
    dialect_name = connection.dialect.name if connection is not None else None
    if dialect_name == "sqlite" or (
        connection is None and database_url.startswith("sqlite")
    ):
        options["render_as_batch"] = True
    return options


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **configuration_options(),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    migration_engine = create_database_engine(database_url)
    try:
        with migration_engine.connect() as connection:
            context.configure(connection=connection, **configuration_options(connection))
            with context.begin_transaction():
                context.run_migrations()
    finally:
        migration_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
