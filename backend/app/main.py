from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.video import router as video_router

# Uncomment these only if the files actually exist
# from app.api.v1.history import router as history_router
# from app.api.v1.reports import router as reports_router

from app.core.config import settings
from app.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)
app.include_router(video_router)

# Uncomment when ready
# app.include_router(history_router)
# app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to ML7-VIDS DeepSight API"
    }