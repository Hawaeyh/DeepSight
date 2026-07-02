from pathlib import Path

import torch
import timm

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

ROOT = Path(__file__).resolve().parents[2]

# ------------------------------------------------
# Binary Model
# ------------------------------------------------

binary_model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=2,
)

binary_model.load_state_dict(
    torch.load(
        ROOT
        / "models"
        / "production"
        / "binary"
        / "efficientnet_b0_binary_v3_best.pth",
        map_location=DEVICE,
        weights_only=True,
    )
)

binary_model.to(DEVICE)
binary_model.eval()

# ------------------------------------------------
# Multiclass Model
# ------------------------------------------------

multiclass_model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=8,
)

multiclass_model.load_state_dict(
    torch.load(
        ROOT
        / "models"
        / "production"
        / "multiclass"
        / "efficientnet_b0_multiclass_best.pth",
        map_location=DEVICE,
        weights_only=True,
    )
)

multiclass_model.to(DEVICE)
multiclass_model.eval()

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

print(f"✅ Device : {DEVICE}")
print("✅ Binary Model Loaded")
print("✅ Multiclass Model Loaded")