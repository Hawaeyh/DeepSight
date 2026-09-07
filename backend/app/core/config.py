from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_ENV: Literal["development", "testing", "staging", "production"] = "development"
    APP_NAME: str = "DeepSight System API"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DATABASE_POOL_RECYCLE_SECONDS: int = Field(default=1800, ge=0)
    DATABASE_CONNECT_TIMEOUT_SECONDS: int = Field(default=10, ge=1, le=120)
    DATABASE_ECHO: bool = False

    SECRET_KEY: str = Field(min_length=16)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)

    FIREBASE_ENABLED: bool = True
    FIREBASE_ADMIN_ENABLED: bool = False
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIREBASE_PROJECT_ID: str | None = None
    FIREBASE_CLIENT_EMAIL: str | None = None
    FIREBASE_PRIVATE_KEY: str | None = None
    FIREBASE_COLLECTION: str = "analyses"
    GOOGLE_CLIENT_ID: str | None = None
    FRONTEND_ORIGINS: str = "http://127.0.0.1:5173"

    MODEL_LOADING: Literal["lazy", "disabled"] = "lazy"
    LOCAL_STORAGE_ROOT: str = "uploads"
    REPORT_ROOT: str = "reports"
    GUEST_SESSION_COOKIE_NAME: str = "deepsight_guest_session"
    GUEST_SESSION_HOURS: int = Field(default=24, ge=1, le=168)
    IMAGE_MAX_SIZE_MB: int = Field(default=10, ge=1, le=50)
    IMAGE_MIN_WIDTH: int = Field(default=128, ge=32)
    IMAGE_MIN_HEIGHT: int = Field(default=128, ge=32)
    IMAGE_MAX_WIDTH: int = Field(default=8192, ge=512)
    IMAGE_MAX_HEIGHT: int = Field(default=8192, ge=512)
    IMAGE_INCONCLUSIVE_THRESHOLD: float = Field(default=65.0, ge=50, le=99)
    IMAGE_BLUR_VARIANCE_THRESHOLD: float = Field(default=75.0, ge=0)
    IMAGE_MIN_FACE_SIZE: int = Field(default=64, ge=32, le=512)
    VIDEO_MAX_SIZE_MB: int = Field(default=100, ge=1, le=1000)
    VIDEO_MAX_DURATION_SECONDS: int = Field(default=120, ge=1, le=3600)
    VIDEO_MAX_WIDTH: int = Field(default=3840, ge=320)
    VIDEO_MAX_HEIGHT: int = Field(default=2160, ge=240)
    VIDEO_MIN_FPS: float = Field(default=5, ge=1)
    VIDEO_MAX_FPS: float = Field(default=120, ge=5)
    VIDEO_MAX_ANALYSED_FRAMES: int = Field(default=120, ge=1, le=1000)
    VIDEO_UNIFORM_SAMPLE_COUNT: int = Field(default=40, ge=1, le=500)
    VIDEO_DUPLICATE_THRESHOLD: float = Field(default=4.0, ge=0)
    VIDEO_SUSPICIOUS_THRESHOLD: float = Field(default=65.0, ge=50, le=99)
    VIDEO_SEGMENT_GAP_SECONDS: float = Field(default=3.0, ge=0)
    REDIS_URL: str | None = None
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    VIDEO_TASK_TIME_LIMIT_SECONDS: int = Field(default=900, ge=30)
    VIDEO_TASK_SOFT_TIME_LIMIT_SECONDS: int = Field(default=840, ge=30)
    TEMPORARY_MEDIA_RETENTION_HOURS: int = Field(default=24, ge=1)
    VIDEO_BACKGROUND_FALLBACK_ENABLED: bool = True
    STRIPE_ENABLED: bool = False
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_PRICE_BASIC_MONTHLY: str | None = None
    STRIPE_PRICE_BASIC_ANNUAL: str | None = None
    STRIPE_PRICE_LITE_MONTHLY: str | None = None
    STRIPE_PRICE_LITE_ANNUAL: str | None = None
    STRIPE_SUCCESS_URL: str = "http://127.0.0.1:5173/subscription/success"
    STRIPE_CANCEL_URL: str = "http://127.0.0.1:5173/subscription/cancel"
    EXTENSION_VIDEO_MAX_SESSION_SECONDS: int = 300
    EXTENSION_VIDEO_MAX_FRAMES: int = 120
    HTTPS_REDIRECT_ENABLED: bool = False
    TRUSTED_HOSTS: str = "127.0.0.1,localhost,testserver"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_PER_MINUTE: int = Field(default=10, ge=1)
    RATE_LIMIT_GUEST_PER_MINUTE: int = Field(default=20, ge=1)
    RATE_LIMIT_UPLOAD_PER_MINUTE: int = Field(default=30, ge=1)
    RATE_LIMIT_REPORT_PER_MINUTE: int = Field(default=20, ge=1)
    CLEANUP_SCHEDULE_ENABLED: bool = False
    CLEANUP_SCHEDULE_HOURS: int = Field(default=6, ge=1, le=168)

    @field_validator("DATABASE_URL")
    @classmethod
    def database_url_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("DATABASE_URL must not be empty")
        try:
            url = make_url(value)
        except ArgumentError as error:
            raise ValueError("DATABASE_URL is not a valid SQLAlchemy URL") from error

        if url.drivername == "sqlite":
            if not url.database:
                raise ValueError("SQLite DATABASE_URL must identify a file or :memory:")
        elif url.drivername == "postgresql+psycopg":
            if not url.host or not url.username or not url.database:
                raise ValueError(
                    "PostgreSQL DATABASE_URL requires a username, host, and database name"
                )
        else:
            raise ValueError(
                "Unsupported database driver; use sqlite or postgresql+psycopg"
            )
        return value

    @field_validator("LOG_LEVEL")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
        return normalized

    @model_validator(mode="after")
    def validate_deployment_security(self):
        if self.APP_ENV in {"staging", "production"}:
            if len(self.SECRET_KEY) < 32 or "development" in self.SECRET_KEY.lower():
                raise ValueError("Staging and production require a strong non-development SECRET_KEY")
            if "*" in self.FRONTEND_ORIGINS:
                raise ValueError("Wildcard CORS origins are forbidden outside development")
        return self

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
