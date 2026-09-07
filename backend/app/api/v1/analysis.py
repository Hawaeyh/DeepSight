from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import AnalysisPrincipal, get_analysis_principal
from app.ai.model_status import ModelUnavailableError
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisResponse
from app.services.ai_service import AIService
from app.services.analysis_service import AnalysisService
from app.services.image_validation_service import ImageValidationService, upload_error
from app.services.firebase_service import FirebaseService
from app.services.subscription_service import SubscriptionService
from app.services.protected_file_service import remove_if_contained
from app.core.paths import REPORT_DIR, UPLOAD_DIR

router = APIRouter(
    prefix="/analysis",
    tags=["Image Detection"],
)


@router.post(
    "/image",
    response_model=AnalysisResponse,
    status_code=200,
)
async def analyze_image(
    file: UploadFile = File(...),
    model: str = Form("efficientnet"),
    authorization: str | None = Header(None),
    x_deepsight_client: str | None = Header(None),
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):

    storage_key = (
        f"user-{principal.owner_user_id}"
        if principal.owner_user_id is not None
        else f"guest-{principal.guest_session_id}"
    )
    validated = await ImageValidationService.validate_and_store(file, storage_key)
    saved_path = validated.path

    try:
        usage = SubscriptionService.reserve(
            db,
            authorization,
            str(principal.guest_session_id) if principal.guest_session_id else None,
            "image",
            x_deepsight_client or "web",
        )
        result = AIService.analyze_image(
            str(saved_path),
            model,
        )
    except HTTPException:
        if "usage" in locals(): SubscriptionService.release(db, usage)
        saved_path.unlink(missing_ok=True)
        raise
    except ValueError as error:
        if "usage" in locals(): SubscriptionService.release(db, usage)
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(error)) from error
    except ModelUnavailableError as error:
        if "usage" in locals(): SubscriptionService.release(db, usage)
        saved_path.unlink(missing_ok=True)
        raise upload_error(503, "MODEL_UNAVAILABLE", "The requested model is unavailable.") from error
    except Exception as error:
        logger.exception(
            "Image analysis inference failed for user_id={} guest_session_id={}",
            principal.owner_user_id,
            principal.guest_session_id,
        )
        if "usage" in locals(): SubscriptionService.release(db, usage)
        saved_path.unlink(missing_ok=True)
        raise upload_error(500, "INFERENCE_FAILED", "Image inference failed safely.") from error

    if not result["success"]:

        SubscriptionService.release(db, usage)
        saved_path.unlink(missing_ok=True)
        raise upload_error(422, "NO_FACE_DETECTED", "No clear face was detected.")

    selected_box = result.get("selected_face_box")
    if selected_box and min(selected_box[2] - selected_box[0], selected_box[3] - selected_box[1]) < settings.IMAGE_MIN_FACE_SIZE:
        SubscriptionService.release(db, usage)
        saved_path.unlink(missing_ok=True)
        raise upload_error(422, "FACE_TOO_SMALL", "The detected face is too small for reliable analysis.")

    file_size = round(
        validated.size_mb,
        2,
    )

    try:
        analysis = AnalysisService.save(

        db=db,

        filename=validated.original_filename,

        file_path=str(saved_path),

        file_type="Image",

        file_extension=validated.extension,

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

        image_width=validated.width,

        image_height=validated.height,

        video_duration=None,

        frames_analyzed=None,

        fake_frames=None,

        real_frames=None,

        owner_user_id=principal.owner_user_id,

        guest_session_id=principal.guest_session_id,

        source={"extension": "browser_extension_image", "extension-pro": "browser_extension_image", "extension-video": "browser_extension_video", "live": "webcam"}.get(x_deepsight_client or "", "web"),

        quality_metadata=validated.quality,

        quality_warnings=(
            validated.warnings
            + (["Multiple faces detected; the largest face was analysed"] if result.get("face_count", 0) > 1 else [])
            + (["Low-resolution face"] if result.get("selected_face_box") and (result["selected_face_box"][2] - result["selected_face_box"][0]) < 96 else [])
        ),

        selected_face_index=result.get("selected_face_index"),

        selected_face_box=result.get("selected_face_box"),

        face_detection_confidence=result.get("face_detection_confidence"),

        )
    except Exception as error:
        logger.exception(
            "Image analysis storage failed for user_id={} guest_session_id={}",
            principal.owner_user_id,
            principal.guest_session_id,
        )
        db.rollback()
        SubscriptionService.release_key(db, usage.reservation_key)
        saved_path.unlink(missing_ok=True)
        raise upload_error(500, "STORAGE_FAILED", "The analysis result could not be stored safely.") from error

    SubscriptionService.complete_key(db, usage.reservation_key)

    if principal.guest_session is not None:
        principal.guest_session.analysis_count += 1
        db.commit()

    return analysis


@router.get(
    "/history",
    response_model=list[AnalysisResponse],
)
def get_history(
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):
    if principal.owner_user_id is None:
        return []
    return AnalysisRepository.list_owned(db, principal.owner_user_id)


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):

    analysis = AnalysisRepository.get_accessible(
        db,
        analysis_id,
        principal,
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
    principal: AnalysisPrincipal = Depends(get_analysis_principal),
):

    analysis = AnalysisRepository.delete_accessible(
        db,
        analysis_id,
        principal,
    )

    if analysis is None:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    FirebaseService.delete_analysis(analysis_id)
    remove_if_contained(analysis.file_path, UPLOAD_DIR)
    remove_if_contained(str(REPORT_DIR / f"analysis_{analysis.id}.pdf"), REPORT_DIR)

    return {

        "message": "Analysis deleted successfully."

    }
