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
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.services.file_service import save_uploaded_video
from app.services.video_service import VideoService

router = APIRouter(
    prefix="/video",
    tags=["Video Detection"],
)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=201,
)
async def analyze_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    saved_path = save_uploaded_video(file)

    result = VideoService.analyze(
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

        file_type="Video",

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

        face_detected=False,

        face_count=0,

        image_width=None,

        image_height=None,

        video_duration=result["video_duration"],

        frames_analyzed=result["frames_analyzed"],

        fake_frames=result["fake_frames"],

        real_frames=result["real_frames"],

    )

    return analysis