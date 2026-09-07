from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import cv2
from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.core.paths import VIDEO_UPLOAD_DIR


VIDEO_TYPES = {
    ".mp4": {"video/mp4", "application/mp4"},
    ".mov": {"video/quicktime"},
    ".webm": {"video/webm"},
}


def video_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message})


@dataclass(frozen=True)
class ValidatedVideo:
    path: Path
    original_filename: str
    size_mb: float
    duration_seconds: float
    width: int
    height: int
    fps: float
    total_frames: int
    codec: str


class VideoValidationService:
    @staticmethod
    async def validate_and_store(file: UploadFile, storage_key: str) -> ValidatedVideo:
        maximum = settings.VIDEO_MAX_SIZE_MB * 1024 * 1024
        content = await file.read(maximum + 1)
        if not content:
            raise video_error(422, "VIDEO_INVALID", "The uploaded video is empty.")
        if len(content) > maximum:
            raise video_error(413, "VIDEO_TOO_LARGE", f"Videos must be at most {settings.VIDEO_MAX_SIZE_MB} MB.")
        extension = Path(file.filename or "").suffix.lower()
        if extension not in VIDEO_TYPES or file.content_type not in VIDEO_TYPES[extension]:
            raise video_error(415, "VIDEO_INVALID", "Video extension and MIME type must be MP4, MOV, or WEBM.")
        if extension in {".mp4", ".mov"} and b"ftyp" not in content[:64]:
            raise video_error(415, "VIDEO_INVALID", "The video container signature is invalid.")
        if extension == ".webm" and not content.startswith(b"\x1aE\xdf\xa3"):
            raise video_error(415, "VIDEO_INVALID", "The WebM container signature is invalid.")

        destination_dir = VIDEO_UPLOAD_DIR / storage_key
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{uuid4().hex}{extension}"
        try:
            destination.write_bytes(content)
            capture = cv2.VideoCapture(str(destination))
            if not capture.isOpened():
                raise ValueError("decode")
            fps = float(capture.get(cv2.CAP_PROP_FPS))
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            codec_value = int(capture.get(cv2.CAP_PROP_FOURCC))
            codec = "".join(chr((codec_value >> (8 * index)) & 0xFF) for index in range(4)).strip()
            capture.release()
            if fps <= 0 or total_frames <= 0 or width <= 0 or height <= 0:
                raise ValueError("metadata")
            duration = total_frames / fps
            if duration > settings.VIDEO_MAX_DURATION_SECONDS:
                raise video_error(422, "VIDEO_TOO_LONG", f"Videos must be at most {settings.VIDEO_MAX_DURATION_SECONDS} seconds.")
            if width > settings.VIDEO_MAX_WIDTH or height > settings.VIDEO_MAX_HEIGHT:
                raise video_error(422, "VIDEO_INVALID", "Video dimensions exceed configured limits.")
            if not settings.VIDEO_MIN_FPS <= fps <= settings.VIDEO_MAX_FPS:
                raise video_error(422, "VIDEO_INVALID", "Video frame rate is outside configured limits.")
            return ValidatedVideo(destination, Path(file.filename or "video").name, round(len(content)/(1024*1024), 2), round(duration, 3), width, height, round(fps, 3), total_frames, codec)
        except HTTPException:
            destination.unlink(missing_ok=True)
            raise
        except Exception:
            destination.unlink(missing_ok=True)
            raise video_error(422, "VIDEO_DECODE_FAILED", "The video could not be decoded safely.") from None
