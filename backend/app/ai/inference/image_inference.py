import time

import torch
from PIL import Image
from torchvision import transforms

from app.ai.face.face_cropper import extract_face
from app.ai.models.model_loader import (
    binary_model,
    multiclass_model,
    CLASS_NAMES,
    DEVICE,
)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def predict(image_path: str):

    start = time.time()

    original = Image.open(image_path).convert("RGB")

    image_width, image_height = original.size

    face = extract_face(image_path)

    if face is None:

        return {

            "success": False,

            "message": "No face detected.",

            "prediction": None,

            "confidence": None,

            "real_probability": None,

            "fake_probability": None,

            "deepfake_type": None,

            "type_confidence": None,

            "risk_level": "Unknown",

            "processing_time": round(time.time() - start, 4),

            "model_name": "EfficientNet-B0",

            "model_version": "Binary V3",

            "device": str(DEVICE),

            "face_detected": False,

            "face_count": 0,

            "image_width": image_width,

            "image_height": image_height,

        }

    image = Image.fromarray(face)

    tensor = (
        transform(image)
        .unsqueeze(0)
        .to(DEVICE)
    )

    with torch.no_grad():

        binary_output = binary_model(tensor)

        binary_probs = torch.softmax(
            binary_output,
            dim=1,
        )

        fake_probability = round(
            binary_probs[0][0].item() * 100,
            2,
        )

        real_probability = round(
            binary_probs[0][1].item() * 100,
            2,
        )

        prediction_index = (
            binary_probs.argmax(1).item()
        )

        confidence = round(
            binary_probs.max().item() * 100,
            2,
        )

        processing_time = round(
            time.time() - start,
            4,
        )

        deepfake_type = None
        type_confidence = None

        if prediction_index == 0:

            multiclass_output = multiclass_model(
                tensor
            )

            multiclass_probs = torch.softmax(
                multiclass_output,
                dim=1,
            )

            type_index = (
                multiclass_probs.argmax(1).item()
            )

            type_confidence = round(
                multiclass_probs.max().item() * 100,
                2,
            )

            deepfake_type = CLASS_NAMES[type_index]

        prediction = (
            "Real"
            if prediction_index == 1
            else "Fake"
        )

        return {

            "success": True,

            "prediction": prediction,

            "confidence": confidence,

            "real_probability": real_probability,

            "fake_probability": fake_probability,

            "deepfake_type": deepfake_type,

            "type_confidence": type_confidence,

            "risk_level": (
                "Low"
                if prediction == "Real"
                else "High"
            ),

            "processing_time": processing_time,

            "model_name": "EfficientNet-B0",

            "model_version": "Binary V3",

            "device": str(DEVICE),

            "face_detected": True,

            "face_count": 1,

            "image_width": image_width,

            "image_height": image_height,

        }