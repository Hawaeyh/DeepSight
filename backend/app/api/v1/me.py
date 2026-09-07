import math
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisResponse


router = APIRouter(prefix="/me", tags=["Current User"])


class AnalysisPage(BaseModel):
    items: list[AnalysisResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int


@router.get("/analyses", response_model=AnalysisPage)
def analyses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    media_type: str | None = None,
    result: str | None = None,
    source: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    search: str | None = Query(None, max_length=255),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filters = {
        "media_type": media_type,
        "prediction": result,
        "filename": search,
        "source": source,
        "created_from": created_from,
        "created_to": created_to,
    }
    total = AnalysisRepository.count_owned(db, user.id, **filters)
    items = AnalysisRepository.list_owned(
        db,
        user.id,
        offset=(page - 1) * page_size,
        limit=page_size,
        newest_first=sort == "newest",
        **filters,
    )
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }
