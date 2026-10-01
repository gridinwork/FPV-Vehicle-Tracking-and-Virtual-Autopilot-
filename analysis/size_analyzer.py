"""BBox size history and relative distance trend.

There is no depth sensor. GROWING means the vehicle covers more of the
frame (approaching). SHRINKING means it covers less (receding).
"""

from __future__ import annotations

from collections import deque


class SizeAnalyzer:
    def __init__(self) -> None:
        self.history: deque[tuple[float, float]] = deque(maxlen=120)
        self.last = (0.0, "STABLE", "STABLE", 0.0)

    def reset(self) -> None:
        self.history.clear()
        self.last = (0.0, "STABLE", "STABLE", 0.0)

    def update(self, timestamp: float, bbox, frame_area: float, measured: bool):
        if not measured or bbox is None or frame_area <= 0:
            ratio = self.history[-1][1] if self.history else 0.0
            return ratio, self.last[1], self.last[2], 0.0
        width = max(0.0, bbox[2] - bbox[0])
        height = max(0.0, bbox[3] - bbox[1])
        ratio = (width * height) / frame_area
        self.history.append((timestamp, ratio))
        old_t = timestamp
        old_ratio = ratio
        for sample_t, sample_ratio in self.history:
            if timestamp - sample_t >= 0.45:
                old_t = sample_t
                old_ratio = sample_ratio
                break
        if old_ratio <= 1e-8:
            return ratio, "STABLE", "STABLE", 0.0
        dt = max(0.20, timestamp - old_t)
        change = (ratio - old_ratio) / old_ratio
        rate = change / dt
        if change > 0.06:
            trend = "GROWING"
            distance = "APPROACHING"
        elif change < -0.06:
            trend = "SHRINKING"
            distance = "RECEDING"
        else:
            trend = "STABLE"
            distance = "STABLE"
        self.last = (ratio, trend, distance, rate)
        return self.last
