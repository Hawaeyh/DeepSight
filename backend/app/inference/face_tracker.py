def intersection_over_union(first: list[int], second: list[int]) -> float:
    x1, y1 = max(first[0], second[0]), max(first[1], second[1])
    x2, y2 = min(first[2], second[2]), min(first[3], second[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area_first = max(0, first[2] - first[0]) * max(0, first[3] - first[1])
    area_second = max(0, second[2] - second[0]) * max(0, second[3] - second[1])
    union = area_first + area_second - intersection
    return intersection / union if union else 0.0


class IoUFaceTracker:
    def __init__(self, threshold: float = 0.3, maximum_gap: int = 5):
        self.threshold = threshold
        self.maximum_gap = maximum_gap
        self.tracks: dict[int, tuple[list[int], int]] = {}
        self.next_track = 1

    def assign(self, boxes: list[list[int]], frame_index: int) -> list[int]:
        assignments = []
        used = set()
        for box in boxes:
            matches = [
                (intersection_over_union(box, previous), track_id)
                for track_id, (previous, last_frame) in self.tracks.items()
                if frame_index - last_frame <= self.maximum_gap and track_id not in used
            ]
            score, track_id = max(matches, default=(0.0, 0))
            if score < self.threshold:
                track_id = self.next_track
                self.next_track += 1
            self.tracks[track_id] = (box, frame_index)
            used.add(track_id)
            assignments.append(track_id)
        return assignments
