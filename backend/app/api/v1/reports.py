from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.repositories.analysis_repository import (
    AnalysisRepository,
)

from app.services.report_service import (
    ReportService,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/{analysis_id}")

def report(
    analysis_id: int,
    db: Session = Depends(get_db),
):

    analysis = AnalysisRepository.get_by_id(
        db,
        analysis_id,
    )

    pdf = ReportService.create(
        analysis
    )

    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename=pdf.name,
    )