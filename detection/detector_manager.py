"""Loads and swaps detector backends."""

from __future__ import annotations

from pathlib import Path

from detection.detector_backend import (
    create_backend,
    resolve_backend_name,
    resolve_profile,
)
from detection.model_registry import ModelRegistry
from utils.datatypes import Detection
from utils.gpu_info import select_device


class DetectorManager:
    def __init__(self) -> None:
        self.registry = ModelRegistry()
        self.backend = None
        self.backend_name = ""
        self.profile = ""
        self.device = "cpu"
        self.checkpoint = ""
        self.imgsz = 640

    def load(self, detector: str, model: str, device_pref: str) -> dict:
        device = select_device(device_pref)
        custom = self.registry.resolve_custom(model)
        if custom is not None:
            backend_name = "YOLO"
            profile = custom.name
            candidates = [str(custom)]
            imgsz = 960
        else:
            backend_name = resolve_backend_name(detector, device)
            profile = resolve_profile(detector, model, device)
            if profile not in {"FAST", "BALANCED", "ACCURATE"}:
                profile = "BALANCED" if backend_name == "RT-DETR" else "FAST"
            candidates = self.registry.candidates(backend_name, profile)
            imgsz = self.registry.imgsz(backend_name, profile)
        if self.backend is not None:
            self.backend.close()
        backend = create_backend(backend_name)
        checkpoint = backend.load(candidates, device, imgsz)
        self.backend = backend
        self.backend_name = backend_name
        self.profile = profile
        self.device = device
        self.checkpoint = checkpoint
        self.imgsz = imgsz
        return {
            "backend": backend_name,
            "profile": profile,
            "device": device,
            "checkpoint": checkpoint,
            "imgsz": imgsz,
            "classes": backend.class_names(),
        }

    def detect(self, frame, confidence: float, allowed: set[str]) -> list[Detection]:
        if self.backend is None:
            return []
        return self.backend.detect(frame, confidence, allowed)

    @property
    def ready(self) -> bool:
        return self.backend is not None and self.backend.model is not None

    def custom_names(self) -> list[str]:
        return [path.name for path in self.registry.custom_models()]
