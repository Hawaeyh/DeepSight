import mimetypes
from pathlib import Path

from fastapi import HTTPException

from app.core.paths import REPORT_DIR, UPLOAD_DIR


def contained_file(stored_path: str, root: Path) -> Path:
    try:
        candidate = Path(stored_path).expanduser().resolve(strict=True)
        candidate.relative_to(root.resolve(strict=False))
    except (OSError, RuntimeError, ValueError):
        raise HTTPException(status_code=404, detail="File not found.") from None
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return candidate


def analysis_media_file(stored_path: str) -> Path:
    return contained_file(stored_path, UPLOAD_DIR)


def report_file(analysis_id: int) -> Path:
    return contained_file(str(REPORT_DIR / f"analysis_{analysis_id}.pdf"), REPORT_DIR)


def safe_media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def remove_if_contained(stored_path: str, root: Path) -> bool:
    try:
        candidate = contained_file(stored_path, root)
    except HTTPException:
        return False
    candidate.unlink(missing_ok=True)
    return True
