from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
):
    return DashboardService.overview(db)


@router.get("/trend")
def trend(
    db: Session = Depends(get_db),
):
    return DashboardService.trend(db)


@router.get("/distribution")
def distribution(
    db: Session = Depends(get_db),
):
    return DashboardService.distribution(db)


@router.get("/recent")
def recent(
    db: Session = Depends(get_db),
):
    return DashboardService.recent(db)


@router.get("/models")
def models(db: Session = Depends(get_db)):
    return DashboardService.models(db)
