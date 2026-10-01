"""Proportional image-error mapping with a center dead zone."""

from __future__ import annotations


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def axis_percent(norm: float, dead_zone: float) -> float:
    dead = max(0.0, min(0.95, dead_zone))
    magnitude = abs(norm)
    if magnitude <= dead:
        return 0.0
    span = max(1e-6, 1.0 - dead)
    scaled = min(1.0, (magnitude - dead) / span)
    return _clamp(scaled * 100.0 if norm > 0 else -scaled * 100.0, -100.0, 100.0)


class ProportionalController:
    def update(self, x_norm: float, y_norm: float, dead_zone: float) -> tuple[float, float]:
        lateral = axis_percent(x_norm, dead_zone)
        vertical = axis_percent(y_norm, dead_zone)
        forward = _clamp(-vertical, -100.0, 100.0)
        return lateral, forward
