from statistics import median

from app.core.config import settings


def semantic(probability: float) -> tuple[str, str]:
    if 45 <= probability <= 55:
        return "inconclusive", "Inconclusive"
    if probability >= settings.VIDEO_SUSPICIOUS_THRESHOLD:
        return "likely_manipulated", "Likely Manipulated"
    return "likely_real", "Likely Real"


def aggregate_frames(frames: list[dict]) -> dict:
    if not frames:
        raise ValueError("No valid face frames were available")
    tracks = {}
    for frame in frames:
        tracks.setdefault(frame["track_id"], []).append(frame)
    track_results = []
    for track_id, items in tracks.items():
        probabilities = [item["fake_probability"] for item in items]
        weights = [max(item.get("quality_score", 0.05), 0.05) for item in items]
        weighted = sum(p*w for p, w in zip(probabilities, weights)) / sum(weights)
        suspicious = sum(p >= settings.VIDEO_SUSPICIOUS_THRESHOLD for p in probabilities)
        score = max(weighted, median(probabilities) * 0.7 + max(probabilities) * 0.3)
        result, label = semantic(score)
        confidence = 100 - score if result == "likely_real" else score
        track_results.append({"track_id": track_id, "frames": len(items), "median_fake_probability": median(probabilities), "maximum_fake_probability": max(probabilities), "weighted_fake_probability": weighted, "suspicious_frames": suspicious, "result": result, "display_label": label, "confidence": confidence})
    primary = max(track_results, key=lambda item: item["weighted_fake_probability"])
    suspicious_frames = sorted((item for item in frames if item["fake_probability"] >= settings.VIDEO_SUSPICIOUS_THRESHOLD), key=lambda item: item["timestamp_ms"])
    segments = []
    for frame in suspicious_frames:
        if not segments or frame["track_id"] != segments[-1]["track_id"] or frame["timestamp_ms"] - segments[-1]["end_timestamp_ms"] > settings.VIDEO_SEGMENT_GAP_SECONDS * 1000:
            segments.append({"track_id": frame["track_id"], "start_timestamp_ms": frame["timestamp_ms"], "end_timestamp_ms": frame["timestamp_ms"], "probabilities": [frame["fake_probability"]]})
        else:
            segments[-1]["end_timestamp_ms"] = frame["timestamp_ms"]
            segments[-1]["probabilities"].append(frame["fake_probability"])
    for segment in segments:
        values = segment.pop("probabilities")
        segment.update({"confidence": max(values), "median_probability": median(values), "frame_count": len(values), "result": "likely_manipulated"})
    return {"result": primary["result"], "display_label": primary["display_label"], "overall_confidence": primary["confidence"], "primary_track_id": primary["track_id"], "tracks": track_results, "segments": segments, "analysed_frames": len(frames), "suspicious_frames": len(suspicious_frames)}
