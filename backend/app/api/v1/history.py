from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.history_service import (
    HistoryService,
)

router = APIRouter(
    prefix="/history",
    tags=["History"],
)


@router.get("")
def history(
    db: Session = Depends(get_db),
):

    return HistoryService.get_all(db)


@router.get("/{analysis_id}")
def detail(
    analysis_id: int,
    db: Session = Depends(get_db),
):

    return HistoryService.get_by_id(
        db,
        analysis_id,
    )


@router.delete("/{analysis_id}")
def delete(
    analysis_id: int,
    db: Session = Depends(get_db),
):

    HistoryService.delete(
        db,
        analysis_id,
    )

    return {
        "message": "Deleted successfully."
    }