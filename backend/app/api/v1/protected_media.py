from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import AnalysisPrincipal, get_analysis_principal, get_current_user
from app.core.database import get_db
from app.core.paths import VIDEO_FRAME_DIR
from app.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.services.protected_file_service import contained_file, analysis_media_file, safe_media_type
from app.services.report_service import ReportService


router = APIRouter(tags=["Protected Media"])


def private_file(path: Path, filename: str) -> FileResponse:
    return FileResponse(
        path,
        media_type=safe_media_type(path),
        filename=Path(filename).name,
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"},
    )


@router.get("/analyses/{analysis_id}/media/original")
def original_media(
    analysis_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    analysis = AnalysisRepository.get_accessible(db, analysis_id, principal)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return private_file(analysis_media_file(analysis.file_path), analysis.filename)


@router.get("/analyses/{analysis_id}/media/thumbnail")
def thumbnail(
    analysis_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    analysis = AnalysisRepository.get_accessible(db, analysis_id, principal)
    if analysis is None or analysis.file_type.lower() != "image":
        raise HTTPException(status_code=404, detail="Thumbnail not found.")
    return private_file(analysis_media_file(analysis.file_path), analysis.filename)


@router.get("/analyses/{analysis_id}/report/download")
def download_report(
    analysis_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    analysis = AnalysisRepository.get_owned(db, analysis_id, user.id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    path = ReportService.create(analysis)
    return private_file(path, f"deepsight-analysis-{analysis.id}.pdf")


@router.get("/videos/{analysis_id}/frames/{frame_id}")
def video_frame(
    analysis_id: int,
    frame_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    analysis = AnalysisRepository.get_accessible(db, analysis_id, principal)
    if analysis is None or analysis.file_type.lower() != "video" or frame_id < 0:
        raise HTTPException(status_code=404, detail="Frame not found.")
    frame_directory = VIDEO_FRAME_DIR / Path(analysis.file_path).stem
    matches = sorted(frame_directory.glob("*.jpg"), key=lambda item: item.name)
    if frame_id >= len(matches):
        raise HTTPException(status_code=404, detail="Frame not found.")
    frame = contained_file(str(matches[frame_id]), VIDEO_FRAME_DIR)
    return private_file(frame, f"analysis-{analysis.id}-frame-{frame_id}.jpg")
