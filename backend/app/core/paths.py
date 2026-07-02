from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads"

IMAGE_UPLOAD_DIR = UPLOAD_DIR / "images"
VIDEO_UPLOAD_DIR = UPLOAD_DIR / "videos"

IMAGE_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

VIDEO_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)