from pathlib import Path
from threading import Lock

from app.core.config import settings


MODEL_ROOT = Path(__file__).resolve().parents[1] / "models" / "production"
MODEL_SPECS = {
    "deepsightnet": {
        "name": "DeepSightNet",
        "version": "Binary V3",
        "description": "Custom DeepSight residual attention network",
        "checkpoint": MODEL_ROOT / "binary" / "best_model_deepsightnet.pth",
    },
    "efficientnet": {
        "name": "EfficientNet-B0",
        "version": "Binary V2",
        "description": "Efficient convolutional deepfake detector",
        "checkpoint": MODEL_ROOT / "binary" / "efficientnet_b0_binary_v2_best.pth",
    },
}

_state_lock = Lock()
_binary_models_loaded: set[str] = set()
_multiclass_loaded = False
_face_detector_loaded = False
_device: str | None = None


class ModelUnavailableError(RuntimeError):
    pass


def mark_device(device: str) -> None:
    global _device
    with _state_lock:
        _device = device


def mark_binary_loaded(model_key: str) -> None:
    with _state_lock:
        _binary_models_loaded.add(model_key)


def mark_multiclass_loaded() -> None:
    global _multiclass_loaded
    with _state_lock:
        _multiclass_loaded = True


def mark_face_detector_loaded() -> None:
    global _face_detector_loaded
    with _state_lock:
        _face_detector_loaded = True


def get_model_catalog() -> list[dict]:
    return [
        {
            "key": key,
            "name": spec["name"],
            "version": spec["version"],
            "description": spec["description"],
            "available": spec["checkpoint"].is_file(),
        }
        for key, spec in MODEL_SPECS.items()
    ]


def get_inference_device() -> str:
    return _device or "not_initialized"


def get_model_load_status() -> dict[str, str]:
    if settings.MODEL_LOADING == "disabled":
        return {"binary": "disabled", "multiclass": "disabled", "face_detector": "disabled"}
    return {
        "binary": "loaded" if _binary_models_loaded else "not_loaded",
        "multiclass": "loaded" if _multiclass_loaded else "not_loaded",
        "face_detector": "loaded" if _face_detector_loaded else "not_loaded",
    }
