from io import BytesIO

import pytest
from fastapi import UploadFile
from PIL import Image

from app.inference.face_tracker import IoUFaceTracker
from app.inference.video_aggregator import aggregate_frames
from app.services.image_validation_service import ImageValidationService


def image_bytes(format_name="PNG", size=(160, 160)):
    output = BytesIO()
    Image.new("RGB", size, (90, 120, 150)).save(output, format=format_name)
    return output.getvalue()


@pytest.mark.asyncio
async def test_image_validation_accepts_real_png_and_uses_generated_name(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.image_validation_service.IMAGE_UPLOAD_DIR", tmp_path)
    upload = UploadFile(filename="../../unsafe.png", file=BytesIO(image_bytes()), headers={"content-type": "image/png"})
    result = await ImageValidationService.validate_and_store(upload, "user-1")
    assert result.width == result.height == 160
    assert result.path.parent == tmp_path / "user-1"
    assert result.path.name != "unsafe.png"


@pytest.mark.asyncio
async def test_image_validation_rejects_mime_signature_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.image_validation_service.IMAGE_UPLOAD_DIR", tmp_path)
    upload = UploadFile(filename="fake.png", file=BytesIO(image_bytes("JPEG")), headers={"content-type": "image/png"})
    with pytest.raises(Exception) as caught:
        await ImageValidationService.validate_and_store(upload, "user-1")
    assert caught.value.status_code == 415
    assert not list(tmp_path.rglob("*.*"))


def test_iou_tracker_keeps_overlapping_face_and_splits_distant_face():
    tracker = IoUFaceTracker()
    first = tracker.assign([[10, 10, 100, 100]], 0)[0]
    assert tracker.assign([[15, 12, 102, 101]], 1)[0] == first
    assert tracker.assign([[300, 300, 390, 390]], 2)[0] != first


def test_video_aggregation_builds_suspicious_segment_and_real_confidence():
    manipulated = aggregate_frames([
        {"track_id": 1, "timestamp_ms": 0, "fake_probability": 80.0, "quality_score": 1.0},
        {"track_id": 1, "timestamp_ms": 1000, "fake_probability": 90.0, "quality_score": 1.0},
    ])
    assert manipulated["result"] == "likely_manipulated"
    assert manipulated["segments"][0]["frame_count"] == 2
    real = aggregate_frames([
        {"track_id": 1, "timestamp_ms": 0, "fake_probability": 10.0, "quality_score": 1.0},
        {"track_id": 1, "timestamp_ms": 1000, "fake_probability": 20.0, "quality_score": 1.0},
    ])
    assert real["result"] == "likely_real"
    assert real["overall_confidence"] > 70


def test_real_binary_checkpoint_loads_and_returns_two_logits(monkeypatch):
    import torch
    from app.ai.model_status import MODEL_SPECS
    from app.ai.models import model_loader

    checkpoint = MODEL_SPECS["efficientnet"]["checkpoint"]
    if not checkpoint.is_file():
        pytest.skip("Configured EfficientNet checkpoint is genuinely unavailable")
    monkeypatch.setattr(model_loader.settings, "MODEL_LOADING", "lazy")
    model, _ = model_loader.get_binary_model("efficientnet")
    with torch.no_grad():
        output = model(torch.zeros(1, 3, 224, 224, device=model_loader.DEVICE))
    assert tuple(output.shape) == (1, 2)
    assert torch.isfinite(output).all()
