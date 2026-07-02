from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository


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
    ):

        analysis = Analysis(

            filename=filename,
            file_path=file_path,

            file_type=file_type,
            file_extension=file_extension,
            file_size=file_size,

            prediction=prediction,
            confidence=confidence,

            real_probability=real_probability,
            fake_probability=fake_probability,

            deepfake_type=deepfake_type,
            type_confidence=type_confidence,

            risk_level=risk_level,

            model_name=model_name,
            model_version=model_version,

            device=device,

            processing_time=processing_time,

            face_detected=face_detected,
            face_count=face_count,

            image_width=image_width,
            image_height=image_height,

            video_duration=video_duration,
            frames_analyzed=frames_analyzed,
            fake_frames=fake_frames,
            real_frames=real_frames,

            verified_result=verified_result,
            remarks=remarks,

            status=status,
        )

        return AnalysisRepository.create(
            db,
            analysis,
        )