from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import uuid4
import warnings

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.paths import IMAGE_UPLOAD_DIR


FORMAT_RULES = {
    "JPEG": {"mime": "image/jpeg", "extensions": {".jpg", ".jpeg"}},
    "PNG": {"mime": "image/png", "extensions": {".png"}},
    "WEBP": {"mime": "image/webp", "extensions": {".webp"}},
}


def upload_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message})


@dataclass(frozen=True)
class ValidatedImage:
    path: Path
    original_filename: str
    extension: str
    size_mb: float
    width: int
    height: int
    quality: dict
    warnings: list[str]


class ImageValidationService:
    @staticmethod
    async def validate_and_store(file: UploadFile, storage_key: str) -> ValidatedImage:
        maximum = settings.IMAGE_MAX_SIZE_MB * 1024 * 1024
        content = await file.read(maximum + 1)
        if not content:
            raise upload_error(422, "INVALID_FILE_TYPE", "The uploaded image is empty.")
        if len(content) > maximum:
            raise upload_error(413, "FILE_TOO_LARGE", f"Images must be at most {settings.IMAGE_MAX_SIZE_MB} MB.")

        extension = Path(file.filename or "").suffix.lower()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(content)) as probe:
                    detected_format = probe.format
                    probe.verify()
                with Image.open(BytesIO(content)) as decoded:
                    decoded.load()
                    width, height = decoded.size
                    rgb = decoded.convert("RGB")
                    pixel_data = np.asarray(rgb)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise upload_error(422, "IMAGE_DECODE_FAILED", "The image is corrupted or unsafe.") from None

        rule = FORMAT_RULES.get(detected_format or "")
        if rule is None or extension not in rule["extensions"]:
            raise upload_error(415, "INVALID_FILE_TYPE", "Only JPEG, PNG, and WEBP images are supported.")
        if file.content_type != rule["mime"]:
            raise upload_error(415, "INVALID_FILE_TYPE", "The declared image type does not match its content.")
        if not (
            settings.IMAGE_MIN_WIDTH <= width <= settings.IMAGE_MAX_WIDTH
            and settings.IMAGE_MIN_HEIGHT <= height <= settings.IMAGE_MAX_HEIGHT
        ):
            raise upload_error(422, "IMAGE_DIMENSIONS_INVALID", "Image dimensions are outside the configured limits.")

        gray = cv2.cvtColor(pixel_data, cv2.COLOR_RGB2GRAY)
        blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        contrast = float(gray.std())
        aspect_ratio = width / height
        quality_warnings = []
        if blur_variance < settings.IMAGE_BLUR_VARIANCE_THRESHOLD:
            quality_warnings.append("Image appears blurry")
        if brightness < 45 or brightness > 220:
            quality_warnings.append("Lighting may reduce reliability")
        if contrast < 25:
            quality_warnings.append("Image has low contrast")
        if aspect_ratio > 4 or aspect_ratio < 0.25:
            quality_warnings.append("Extreme aspect ratio may reduce reliability")

        destination_dir = IMAGE_UPLOAD_DIR / storage_key
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{uuid4().hex}{next(iter(sorted(rule['extensions'])))}"
        try:
            destination.write_bytes(content)
        except OSError:
            destination.unlink(missing_ok=True)
            raise upload_error(500, "STORAGE_FAILED", "The image could not be stored safely.") from None
        return ValidatedImage(
            path=destination,
            original_filename=Path(file.filename or "image").name,
            extension=extension,
            size_mb=round(len(content) / (1024 * 1024), 2),
            width=width,
            height=height,
            quality={
                "blur_variance": round(blur_variance, 2),
                "brightness": round(brightness, 2),
                "contrast": round(contrast, 2),
                "aspect_ratio": round(aspect_ratio, 3),
                "width": width,
                "height": height,
            },
            warnings=quality_warnings,
        )
