"""Measured and predicted target trails."""

from __future__ import annotations

from collections import deque


class Trajectory:
    def __init__(self, maxlen: int = 60) -> None:
        self.maxlen = maxlen
        self.measured: deque[tuple[float, float]] = deque(maxlen=maxlen)
        self.predicted: deque[tuple[float, float]] = deque(maxlen=maxlen)

    def set_length(self, length: int) -> None:
        length = max(30, min(100, int(length)))
        self.maxlen = length
        self.measured = deque(self.measured, maxlen=length)
        self.predicted = deque(self.predicted, maxlen=length)

    def add_measured(self, point: tuple[float, float]) -> None:
        self.measured.append((float(point[0]), float(point[1])))
        self.predicted.clear()

    def add_predicted(self, point: tuple[float, float]) -> None:
        self.predicted.append((float(point[0]), float(point[1])))

    def predicted_points(self) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        if self.measured:
            points.append(self.measured[-1])
        points.extend(self.predicted)
        return points

    def clear(self) -> None:
        self.measured.clear()
        self.predicted.clear()
