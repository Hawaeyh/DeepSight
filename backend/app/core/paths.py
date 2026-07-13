from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BASE_DIR.parent

UPLOAD_DIR = BASE_DIR / "uploads"

IMAGE_UPLOAD_DIR = UPLOAD_DIR / "images"
VIDEO_UPLOAD_DIR = UPLOAD_DIR / "videos"
VIDEO_FRAME_DIR = UPLOAD_DIR / "video_frames"
HARD_EXAMPLE_DIR = PROJECT_DIR / "datasets" / "hard_examples"

IMAGE_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

VIDEO_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

VIDEO_FRAME_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

HARD_EXAMPLE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
