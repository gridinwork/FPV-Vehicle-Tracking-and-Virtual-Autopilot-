"""Find a track near the predicted target after a short loss."""

from __future__ import annotations

import math

from utils.datatypes import Track


def find_reacquisition(
    tracks: list[Track],
    predicted_xy: tuple[float, float],
    class_name: str,
    locked_id: int | None,
    frame_diag: float,
    min_confidence: float,
    box_size: tuple[float, float] | None,
) -> Track | None:
    px, py = predicted_xy
    limit = max(48.0, frame_diag * 0.08)
    best = None
    best_dist = 1e9
    box_diag = 40.0
    if box_size is not None:
        box_diag = max(16.0, math.hypot(box_size[0], box_size[1]))
    for track in tracks:
        if locked_id is not None and track.track_id == locked_id:
            continue
        if track.time_since_update > 0.2 or track.predicted:
            continue
        if class_name and track.class_name != class_name:
            continue
        if track.confidence < min_confidence:
            continue
        dist = math.hypot(track.cx - px, track.cy - py)
        if dist > limit:
            continue
        established = track.hits > 4 and track.age_sec > 0.6
        if established and dist > max(24.0, box_diag * 0.65):
            continue
        if dist < best_dist:
            best = track
            best_dist = dist
    return best
