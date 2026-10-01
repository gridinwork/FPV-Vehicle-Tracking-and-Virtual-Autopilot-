"""Timed detector call used by the pipeline thread."""

from __future__ import annotations

import time

from detection.detector_manager import DetectorManager


class DetectorWorker:
    def __init__(self, manager: DetectorManager | None = None) -> None:
        self.manager = manager or DetectorManager()
        self.last_ms = 0.0

    def load(self, detector: str, model: str, device_pref: str) -> dict:
        started = time.perf_counter()
        info = self.manager.load(detector, model, device_pref)
        self.last_ms = (time.perf_counter() - started) * 1000.0
        return info

    def infer(self, frame, confidence: float, allowed: set[str]):
        started = time.perf_counter()
        detections = self.manager.detect(frame, confidence, allowed)
        self.last_ms = (time.perf_counter() - started) * 1000.0
        return detections
