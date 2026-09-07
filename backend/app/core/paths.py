from pathlib import Path

from app.core.config import settings


BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BASE_DIR.parent


def _resolve_backend_path(configured_path: str) -> Path:
    path = Path(configured_path).expanduser()
    return path if path.is_absolute() else BASE_DIR / path


UPLOAD_DIR = _resolve_backend_path(settings.LOCAL_STORAGE_ROOT)
IMAGE_UPLOAD_DIR = UPLOAD_DIR / "images"
VIDEO_UPLOAD_DIR = UPLOAD_DIR / "videos"
VIDEO_FRAME_DIR = UPLOAD_DIR / "video_frames"
REPORT_DIR = _resolve_backend_path(settings.REPORT_ROOT)
HARD_EXAMPLE_DIR = PROJECT_DIR / "datasets" / "hard_examples"


def ensure_runtime_directories() -> list[Path]:
    """Create local runtime directories only when an explicit command needs them."""
    directories = [
        IMAGE_UPLOAD_DIR,
        VIDEO_UPLOAD_DIR,
        VIDEO_FRAME_DIR,
        REPORT_DIR,
        HARD_EXAMPLE_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    return directories
