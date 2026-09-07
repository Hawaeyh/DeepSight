from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from loguru import logger

from app.api.v1.admin import router as admin_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.guest import router as guest_router
from app.api.v1.firebase import router as firebase_router
from app.api.v1.health import router as health_router
from app.api.v1.history import router as history_router
from app.api.v1.models import router as models_router
from app.api.v1.me import router as me_router
from app.api.v1.protected_media import router as protected_media_router
from app.api.v1.owned_analyses import router as owned_analyses_router
from app.api.v1.reports import router as reports_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.video import router as video_router
from app.api.v1.extension import router as extension_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.webcam import router as webcam_router
from app.core.config import settings
from app.core.database import dispose_database_engine
from app.core.logging import configure_logging
from app.core.rate_limit import RateLimitMiddleware


API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    logger.info(
        "Application starting environment={} version={} model_loading={}",
        settings.APP_ENV,
        settings.APP_VERSION,
        settings.MODEL_LOADING,
    )
    yield
    dispose_database_engine()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in settings.FRONTEND_ORIGINS.split(",")
            if origin.strip()
        ],
        allow_origin_regex=r"chrome-extension://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=[item.strip() for item in settings.TRUSTED_HOSTS.split(",") if item.strip()])
    if settings.HTTPS_REDIRECT_ENABLED:
        application.add_middleware(HTTPSRedirectMiddleware)
    application.add_middleware(RateLimitMiddleware)

    @application.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        start = perf_counter()
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
            elapsed_ms = (perf_counter() - start) * 1000
            logger.info(
                "{} {} completed status={} duration_ms={:.2f}",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=()"
        if settings.APP_ENV in {"staging", "production"} and request.url.path not in {"/docs", "/redoc", "/openapi.json"}:
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        if settings.APP_ENV == "production": response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    for router in (
        health_router,
        auth_router,
        guest_router,
        me_router,
        analysis_router,
        owned_analyses_router,
        dashboard_router,
        video_router,
        extension_router,
        notifications_router,
        webhooks_router,
        webcam_router,
        models_router,
        history_router,
        reports_router,
        protected_media_router,
        firebase_router,
        feedback_router,
        subscriptions_router,
        admin_router,
    ):
        application.include_router(router, prefix=API_V1_PREFIX)

    @application.get("/")
    def root():
        return {"message": "Welcome to the DeepSight System API"}

    return application


app = create_app()
