from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile

from app.core.paths import (
    IMAGE_UPLOAD_DIR,
    VIDEO_UPLOAD_DIR,
)


def save_uploaded_image(file: UploadFile):

    extension = Path(file.filename).suffix

    filename = f"{uuid4()}{extension}"

    destination = IMAGE_UPLOAD_DIR / filename

    destination.parent.mkdir(parents=True, exist_ok=True)

    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return destination


def save_uploaded_video(file: UploadFile):

    extension = Path(file.filename).suffix

    filename = f"{uuid4()}{extension}"

    destination = VIDEO_UPLOAD_DIR / filename

    destination.parent.mkdir(parents=True, exist_ok=True)

    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return destination
