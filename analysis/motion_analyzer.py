"""Image-space target motion from velocity in pixels per second."""

from __future__ import annotations

import math


def analyze_motion(vx: float, vy: float, stable_thresh: float = 30.0) -> str:
    if math.hypot(vx, vy) < stable_thresh:
        return "STABLE"
    if abs(vx) >= abs(vy):
        return "MOVING RIGHT" if vx > 0.0 else "MOVING LEFT"
    return "MOVING BACK" if vy > 0.0 else "MOVING FORWARD"
