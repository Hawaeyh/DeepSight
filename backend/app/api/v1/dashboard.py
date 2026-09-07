from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DashboardService.overview(db, user.id)


@router.get("/trend")
def trend(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DashboardService.trend(db, user.id)


@router.get("/distribution")
def distribution(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DashboardService.distribution(db, user.id)


@router.get("/recent")
def recent(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DashboardService.recent(db, user.id)


@router.get("/models")
def models(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DashboardService.models(db, user.id)
