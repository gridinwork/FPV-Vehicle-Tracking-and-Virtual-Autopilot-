"""Image-space speed in pixels per second."""

from __future__ import annotations

import math


def speed_px_per_sec(vx: float, vy: float) -> float:
    return math.hypot(vx, vy)
