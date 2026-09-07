import time

import torch
from PIL import Image
from torchvision import transforms

from app.ai.face.face_cropper import extract_all_face_details, extract_face_details
from app.core.config import settings
from app.ai.models.model_loader import (
    CLASS_NAMES,
    DEVICE,
    get_binary_model,
    get_multiclass_model,
)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def predict_faces(image_path: str, model_key: str = "efficientnet") -> list[dict]:
    """Run one cached binary-model batch for every detected face in a frame."""
    binary_model, model_spec = get_binary_model(model_key)
    faces = extract_all_face_details(image_path)
    if not faces:
        return []
    batch = torch.stack([transform(Image.fromarray(face["crop"])) for face in faces]).to(DEVICE)
    with torch.no_grad():
        probabilities = torch.softmax(binary_model(batch), dim=1)
    results = []
    for face, values in zip(faces, probabilities):
        fake = round(values[0].item() * 100, 2)
        real = round(values[1].item() * 100, 2)
        prediction = "Fake" if fake >= real else "Real"
        results.append({
            **{key: value for key, value in face.items() if key != "crop"},
            "prediction": prediction, "fake_probability": fake, "real_probability": real,
            "confidence": max(fake, real), "model_name": model_spec["name"], "model_version": model_spec["version"],
        })
    return results


def predict(image_path: str, model_key: str = "efficientnet"):

    start = time.time()

    binary_model, model_spec = get_binary_model(model_key)

    original = Image.open(image_path).convert("RGB")

    image_width, image_height = original.size

    face_details = extract_face_details(image_path)

    if face_details is None:

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

            "model_name": model_spec["name"],

            "model_version": model_spec["version"],

            "device": str(DEVICE),

            "face_detected": False,

            "face_count": 0,

            "image_width": image_width,

            "image_height": image_height,

        }

    image = Image.fromarray(face_details["crop"])

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

            multiclass_model = get_multiclass_model()

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

        display_result = (
            "inconclusive"
            if confidence < settings.IMAGE_INCONCLUSIVE_THRESHOLD
            else "likely_real" if prediction == "Real" else "likely_manipulated"
        )
        display_label = {
            "likely_real": "Likely Real",
            "likely_manipulated": "Likely Manipulated",
            "inconclusive": "Inconclusive",
        }[display_result]

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

            "model_name": model_spec["name"],

            "model_version": model_spec["version"],

            "device": str(DEVICE),

            "face_detected": True,
            "face_count": face_details["face_count"],
            "selected_face_index": face_details["selected_face_index"],
            "selected_face_box": face_details["selected_face_box"],
            "face_detection_confidence": face_details["face_detection_confidence"],
            "result": display_result,
            "display_label": display_label,

            "image_width": image_width,

            "image_height": image_height,

        }
