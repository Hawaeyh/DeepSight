from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.analysis import router as analysis_router
from app.core.config import settings
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(analysis_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to ML7-VIDS DeepSight API"
    }