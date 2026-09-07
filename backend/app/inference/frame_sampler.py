from dataclasses import dataclass

import cv2
import numpy as np

from app.core.config import settings


@dataclass
class SampledFrame:
    frame_number: int
    timestamp_ms: int
    image: np.ndarray
    reason: str
    quality_score: float


def sample_video(path: str) -> list[SampledFrame]:
    capture = cv2.VideoCapture(path)
    if not capture.isOpened():
        raise ValueError("Video decode failed")
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    desired = min(settings.VIDEO_UNIFORM_SAMPLE_COUNT, settings.VIDEO_MAX_ANALYSED_FRAMES, total)
    uniform = set(np.linspace(0, max(total - 1, 0), desired, dtype=int).tolist())
    candidates: list[tuple[int, int, np.ndarray, str]] = []
    previous_small = None
    stride = max(1, int(fps))
    index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            reason = "uniform" if index in uniform else None
            if index % stride == 0:
                small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (64, 36))
                if previous_small is not None and float(cv2.absdiff(small, previous_small).mean()) >= 18:
                    reason = "scene_change"
                previous_small = small
            if reason:
                # Decoder timestamps remain accurate for variable-frame-rate media,
                # where frame_number / nominal_fps can drift substantially.
                timestamp_ms = max(0, int(round(capture.get(cv2.CAP_PROP_POS_MSEC))))
                candidates.append((index, timestamp_ms, frame.copy(), reason))
            index += 1
    finally:
        capture.release()

    selected: list[SampledFrame] = []
    last_hash = None
    for frame_number, timestamp_ms, frame, reason in sorted(candidates, key=lambda item: item[0]):
        gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (32, 18))
        if last_hash is not None and float(cv2.absdiff(gray, last_hash).mean()) < settings.VIDEO_DUPLICATE_THRESHOLD:
            continue
        last_hash = gray
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        quality = max(0.05, min(1.0, sharpness / 250.0))
        selected.append(SampledFrame(frame_number, timestamp_ms, frame, reason, quality))
        if len(selected) >= settings.VIDEO_MAX_ANALYSED_FRAMES:
            break
    return selected
