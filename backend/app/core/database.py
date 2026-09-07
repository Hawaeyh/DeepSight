from collections.abc import Generator
from pathlib import Path

from sqlalchemy import MetaData, create_engine, event, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import BACKEND_DIR, settings


NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))


def normalize_database_url(database_url: str | URL) -> URL:
    url = make_url(database_url)
    if url.drivername == "sqlite" and url.database not in {None, "", ":memory:"}:
        database_path = Path(url.database).expanduser()
        if not database_path.is_absolute():
            database_path = (BACKEND_DIR / database_path).resolve()
        url = url.set(database=str(database_path))
    return url


def database_backend(database_url: str | URL | None = None) -> str:
    url = make_url(database_url or settings.DATABASE_URL)
    return "postgresql" if url.drivername.startswith("postgresql") else "sqlite"


def safe_database_target(database_url: str | URL | None = None) -> str:
    url = make_url(database_url or settings.DATABASE_URL)
    if url.drivername == "sqlite":
        return "SQLite"
    return f"PostgreSQL host {url.host or 'unknown'}:{url.port or 5432}"


def create_database_engine(database_url: str | URL | None = None) -> Engine:
    url = normalize_database_url(database_url or settings.DATABASE_URL)
    options: dict = {"echo": settings.DATABASE_ECHO}

    if url.drivername == "sqlite":
        options["connect_args"] = {
            "check_same_thread": False,
            "timeout": settings.DATABASE_CONNECT_TIMEOUT_SECONDS,
        }
    else:
        options.update(
            pool_pre_ping=True,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_recycle=settings.DATABASE_POOL_RECYCLE_SECONDS,
            connect_args={"connect_timeout": settings.DATABASE_CONNECT_TIMEOUT_SECONDS},
        )

    created_engine = create_engine(url, **options)
    if url.drivername == "sqlite":
        @event.listens_for(created_engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return created_engine


engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_database_connection(target_engine: Engine | None = None) -> bool:
    with (target_engine or engine).connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def dispose_database_engine() -> None:
    engine.dispose()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
