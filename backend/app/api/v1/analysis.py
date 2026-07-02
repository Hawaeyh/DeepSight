from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisResponse
from app.services.ai_service import AIService
from app.services.analysis_service import AnalysisService
from app.services.file_service import save_uploaded_image

router = APIRouter(
    prefix="/analysis",
    tags=["Image Detection"],
)


@router.post(
    "/image",
    response_model=AnalysisResponse,
    status_code=201,
)
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    saved_path = save_uploaded_image(file)

    result = AIService.analyze_image(
        str(saved_path)
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result["message"],
        )

    file_size = round(
        Path(saved_path).stat().st_size / (1024 * 1024),
        2,
    )

    analysis = AnalysisService.save(

        db=db,

        filename=file.filename,

        file_path=str(saved_path),

        file_type="Image",

        file_extension=Path(file.filename).suffix,

        file_size=file_size,

        prediction=result["prediction"],

        confidence=result["confidence"],

        real_probability=result["real_probability"],

        fake_probability=result["fake_probability"],

        deepfake_type=result["deepfake_type"],

        type_confidence=result["type_confidence"],

        risk_level=result["risk_level"],

        model_name=result["model_name"],

        model_version=result["model_version"],

        device=result["device"],

        processing_time=result["processing_time"],

        face_detected=result["face_detected"],

        face_count=result["face_count"],

        image_width=result["image_width"],

        image_height=result["image_height"],

        video_duration=None,

        frames_analyzed=None,

        fake_frames=None,

        real_frames=None,

    )

    return analysis


@router.get(
    "/history",
    response_model=list[AnalysisResponse],
)
def get_history(
    db: Session = Depends(get_db),
):

    return AnalysisRepository.get_all(db)


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
):

    analysis = AnalysisRepository.get_by_id(
        db,
        analysis_id,
    )

    if analysis is None:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return analysis


@router.delete(
    "/{analysis_id}",
)
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
):

    analysis = AnalysisRepository.delete(
        db,
        analysis_id,
    )

    if analysis is None:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return {

        "message": "Analysis deleted successfully."

    }