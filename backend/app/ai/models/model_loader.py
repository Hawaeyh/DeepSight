from pathlib import Path
from threading import Lock

import timm
import torch
from torch import nn

from app.ai.architectures.deepsightnet import DeepSightNet

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "production"

MODEL_SPECS = {
    "deepsightnet": {
        "name": "DeepSightNet",
        "version": "Binary V3",
        "description": "Custom DeepSight residual attention network",
        "checkpoint": MODEL_DIR / "binary" / "best_model_deepsightnet.pth",
    },
    "efficientnet": {
        "name": "EfficientNet-B0",
        "version": "Binary V2",
        "description": "Efficient convolutional deepfake detector",
        "checkpoint": MODEL_DIR / "binary" / "efficientnet_b0_binary_v2_best.pth",
    },
}

CLASS_NAMES = [
    "celebdf",
    "deepfakedetection",
    "deepfakes",
    "face2face",
    "faceshifter",
    "faceswap",
    "neuraltextures",
    "real",
]

_binary_models: dict[str, nn.Module] = {}
_multiclass_model: nn.Module | None = None
_load_lock = Lock()


class ModelUnavailableError(RuntimeError):
    pass


def _create_binary_model(model_key: str) -> nn.Module:
    if model_key == "deepsightnet":
        return DeepSightNet(num_classes=2)
    if model_key == "efficientnet":
        return timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
    raise ValueError(f"Unknown model: {model_key}")


def _load_checkpoint(model: nn.Module, checkpoint_path: Path) -> nn.Module:
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE, weights_only=True)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()
    return model


def get_binary_model(model_key: str) -> tuple[nn.Module, dict]:
    spec = MODEL_SPECS.get(model_key)
    if spec is None:
        raise ValueError(f"Unknown model: {model_key}")
    if not spec["checkpoint"].is_file():
        raise ModelUnavailableError(
            f"{spec['name']} is not available because its trained checkpoint is missing."
        )

    with _load_lock:
        if model_key not in _binary_models:
            _binary_models[model_key] = _load_checkpoint(
                _create_binary_model(model_key),
                spec["checkpoint"],
            )
            print(f"Loaded {spec['name']} on {DEVICE}")

    return _binary_models[model_key], spec


def get_multiclass_model() -> nn.Module:
    global _multiclass_model

    with _load_lock:
        if _multiclass_model is None:
            model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=8)
            checkpoint_path = MODEL_DIR / "multiclass" / "efficientnet_b0_multiclass_best.pth"
            _multiclass_model = _load_checkpoint(model, checkpoint_path)
            print(f"Loaded multiclass model on {DEVICE}")

    return _multiclass_model


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


print(f"Inference device: {DEVICE}")
