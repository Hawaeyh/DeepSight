import time
from pathlib import Path

import cv2
import torch
from PIL import Image
from torchvision import transforms

from app.ai.models.model_loader import (
    DEVICE,
    get_binary_model,
)
from app.core.paths import VIDEO_FRAME_DIR

MODEL_NAME = "EfficientNet-B0"
MODEL_VERSION = "Binary V2"

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def extract_frames(video_path: str, output_dir: Path):

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for frame in output_dir.glob("*.jpg"):
        frame.unlink()

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    interval = int(fps)

    frame_index = 0
    saved = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        if frame_index % interval == 0:

            cv2.imwrite(
                str(output_dir / f"frame_{saved}.jpg"),
                frame,
            )

            saved += 1

        frame_index += 1

    cap.release()

    return saved


def predict_video(video_path: str):

    start = time.time()

    binary_model, _ = get_binary_model("efficientnet")

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration = (
        frame_count / fps
        if fps > 0
        else 0
    )

    cap.release()

    frame_dir = VIDEO_FRAME_DIR / Path(video_path).stem

    total = extract_frames(
        video_path,
        frame_dir,
    )

    if total == 0:

        return {

            "success": False,

            "message": "No frames extracted.",

            "prediction": None,

            "confidence": None,

            "real_probability": None,

            "fake_probability": None,

            "deepfake_type": None,

            "type_confidence": None,

            "risk_level": "Unknown",

            "processing_time": round(
                time.time() - start,
                4,
            ),

            "device": str(DEVICE),

            "model_name": MODEL_NAME,

            "model_version": MODEL_VERSION,

            "frames_analyzed": 0,

            "fake_frames": 0,

            "real_frames": 0,

            "video_duration": duration,
        }

    fake_frames = 0
    real_frames = 0

    fake_scores = []
    real_scores = []
    frame_results = []

    for index, frame in enumerate(sorted(frame_dir.glob("*.jpg"), key=lambda item: int(item.stem.split("_")[-1]))):

        image = Image.open(frame).convert("RGB")

        tensor = (
            transform(image)
            .unsqueeze(0)
            .to(DEVICE)
        )

        with torch.no_grad():

            output = binary_model(tensor)

            probs = torch.softmax(
                output,
                dim=1,
            )

        fake_probability = probs[0][0].item() * 100

        real_probability = probs[0][1].item() * 100

        fake_scores.append(fake_probability)

        real_scores.append(real_probability)

        prediction = probs.argmax(1).item()

        if prediction == 0:

            fake_frames += 1

        else:

            real_frames += 1

        frame_confidence = max(fake_probability, real_probability)
        frame_results.append({
            "index": index,
            "timestamp": round(index * 1.0, 2),
            "prediction": "Fake" if prediction == 0 else "Real",
            "confidence": round(frame_confidence, 2),
            "real_probability": round(real_probability, 2),
            "fake_probability": round(fake_probability, 2),
            "thumbnail_url": "",
        })

    prediction = (
        "Fake"
        if fake_frames > real_frames
        else "Real"
    )

    confidence = round(
        (
            max(fake_frames, real_frames)
            / total
        ) * 100,
        2,
    )

    processing_time = round(
        time.time() - start,
        4,
    )

    fake_ratio = fake_frames / total * 100
    return {

        "success": True,

        "prediction": prediction,

        "confidence": confidence,

        "real_probability": round(
            sum(real_scores) / len(real_scores),
            2,
        ),

        "fake_probability": round(
            sum(fake_scores) / len(fake_scores),
            2,
        ),

        "deepfake_type": None,

        "type_confidence": None,

        "risk_level": (
            "High"
            if prediction == "Fake"
            else "Low"
        ),

        "processing_time": processing_time,

        "device": str(DEVICE),

        "model_name": MODEL_NAME,

        "model_version": MODEL_VERSION,

        "frames_analyzed": total,

        "fake_frames": fake_frames,

        "real_frames": real_frames,

        "video_duration": round(
            duration,
            2,
        ),
        "frame_results": frame_results,
        "summary": (
            f"{fake_frames} of {total} sampled frames ({fake_ratio:.1f}%) were classified as fake. "
            f"The overall video decision is {prediction} with {confidence:.1f}% frame agreement."
        ),
    }
