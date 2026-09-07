from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.services.firebase_service import FirebaseService


def _native_json(value):
    """Convert array/tensor scalar metadata to values accepted by JSON columns."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _native_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_native_json(item) for item in value]
    if hasattr(value, "tolist"):
        return _native_json(value.tolist())
    if hasattr(value, "item"):
        return _native_json(value.item())
    raise TypeError(f"Unsupported analysis metadata type: {type(value).__name__}")


class AnalysisService:

    @staticmethod
    def save(
        db: Session,
        *,
        filename: str,
        file_path: str,
        file_type: str,
        file_extension: str | None = None,
        file_size: float | None = None,

        prediction: str,
        confidence: float,
        real_probability: float | None = None,
        fake_probability: float | None = None,

        deepfake_type: str | None = None,
        type_confidence: float | None = None,

        risk_level: str,

        model_name: str,
        model_version: str,

        device: str,

        processing_time: float,

        face_detected: bool = False,
        face_count: int = 0,

        image_width: int | None = None,
        image_height: int | None = None,

        video_duration: float | None = None,
        frames_analyzed: int | None = None,
        fake_frames: int | None = None,
        real_frames: int | None = None,

        verified_result: str | None = None,
        remarks: str | None = None,

        status: str = "Completed",
        owner_user_id: int | None = None,
        guest_session_id: int | None = None,
        source: str = "web",
        quality_metadata: dict | None = None,
        quality_warnings: list[str] | None = None,
        selected_face_index: int | None = None,
        selected_face_box: list[int] | None = None,
        face_detection_confidence: float | None = None,
    ):

        analysis = Analysis(

            filename=filename,
            file_path=file_path,

            file_type=file_type,
            file_extension=file_extension,
            file_size=float(file_size) if file_size is not None else None,

            prediction=prediction,
            confidence=float(confidence),

            real_probability=float(real_probability) if real_probability is not None else None,
            fake_probability=float(fake_probability) if fake_probability is not None else None,

            deepfake_type=deepfake_type,
            type_confidence=float(type_confidence) if type_confidence is not None else None,

            risk_level=risk_level,

            model_name=model_name,
            model_version=model_version,

            device=device,

            processing_time=float(processing_time),

            face_detected=bool(face_detected),
            face_count=int(face_count),

            image_width=int(image_width) if image_width is not None else None,
            image_height=int(image_height) if image_height is not None else None,

            video_duration=video_duration,
            frames_analyzed=frames_analyzed,
            fake_frames=fake_frames,
            real_frames=real_frames,

            verified_result=verified_result,
            remarks=remarks,

            status=status,
            owner_user_id=owner_user_id,
            guest_session_id=guest_session_id,
            source=source,
            quality_metadata=_native_json(quality_metadata),
            quality_warnings=_native_json(quality_warnings),
            selected_face_index=int(selected_face_index) if selected_face_index is not None else None,
            selected_face_box=_native_json(selected_face_box),
            face_detection_confidence=float(face_detection_confidence) if face_detection_confidence is not None else None,
        )

        saved_analysis = AnalysisRepository.create(
            db,
            analysis,
        )

        FirebaseService.save_analysis(saved_analysis)

        return saved_analysis
