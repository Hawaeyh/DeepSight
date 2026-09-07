from threading import Lock

import cv2
from loguru import logger

from app.ai.model_status import mark_face_detector_loaded
from app.core.config import settings


_face_app = None
_face_app_lock = Lock()


def _get_face_app():
    global _face_app

    if settings.MODEL_LOADING == "disabled":
        raise RuntimeError("Model loading is disabled in this environment.")
    if _face_app is not None:
        return _face_app

    with _face_app_lock:
        if _face_app is None:
            from insightface.app import FaceAnalysis

            logger.info("Loading InsightFace detector with CPUExecutionProvider")
            face_app = FaceAnalysis(providers=["CPUExecutionProvider"])
            face_app.prepare(ctx_id=0, det_size=(640, 640))
            _face_app = face_app
            mark_face_detector_loaded()
            logger.info("InsightFace detector loaded")
    return _face_app


def extract_face(image_path: str):
    details = extract_face_details(image_path)
    return details["crop"] if details else None


def extract_face_details(image_path: str):
    details = extract_all_face_details(image_path)
    if not details:
        return None
    selected = max(details, key=lambda item: (item["selected_face_box"][2] - item["selected_face_box"][0]) * (item["selected_face_box"][3] - item["selected_face_box"][1]))
    return {**selected, "face_count": len(details)}


def extract_all_face_details(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        return []

    faces = _get_face_app().get(image)
    if not faces:
        return []
    height, width = image.shape[:2]
    results = []
    for selected_index, face in enumerate(faces):
        x1, y1, x2, y2 = map(int, face.bbox)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)
        if x2 <= x1 or y2 <= y1:
            continue
        results.append({
            "crop": cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2RGB),
            "selected_face_index": selected_index,
            "selected_face_box": [x1, y1, x2, y2],
            "face_detection_confidence": round(float(getattr(face, "det_score", 0.0)), 4),
        })
    return results
