from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.history_service import (
    HistoryService,
)

router = APIRouter(
    prefix="/history",
    tags=["History"],
)


class VerificationRequest(BaseModel):
    verified_result: Literal["Real", "Fake"]
    remarks: str | None = None


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


@router.patch("/{analysis_id}/verify")
def verify(
    analysis_id: int,
    request: VerificationRequest,
    db: Session = Depends(get_db),
):
    analysis = HistoryService.verify(
        db,
        analysis_id,
        request.verified_result,
        request.remarks,
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis
