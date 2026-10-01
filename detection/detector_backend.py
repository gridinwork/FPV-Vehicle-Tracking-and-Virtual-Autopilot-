"""Detector interface and Ultralytics YOLO / RT-DETR backends."""

from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from detection.model_registry import ModelRegistry, canonical_name
from utils.datatypes import Detection
from utils.logger import get_logger
from utils.paths import MODELS_DIR

log = get_logger()


class DetectorBackend(ABC):
    name = "base"

    @abstractmethod
    def load(self, candidates: list[str], device: str, imgsz: int) -> str:
        """Load the first checkpoint that works and return its filename."""

    @abstractmethod
    def detect(self, frame, confidence: float, allowed: set[str]) -> list[Detection]:
        """Return vehicle detections for one frame."""

    def class_names(self) -> list[str]:
        return []

    def close(self) -> None:
        return None


class _UltralyticsBackend(DetectorBackend):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.model = None
        self.device = "cpu"
        self.imgsz = 640
        self.names: dict[int, str] = {}
        self.half = False
        self.loaded_file = ""

    def load(self, candidates: list[str], device: str, imgsz: int) -> str:
        self.close()
        self.device = device
        self.imgsz = int(imgsz)
        self.half = device.startswith("cuda")
        errors: list[str] = []
        for candidate in candidates:
            try:
                path = self._materialize(candidate)
                self.model = self._build(path)
                self.names = {int(k): str(v) for k, v in dict(self.model.names).items()}
                self.loaded_file = Path(path).name
                self._warmup()
                log.info("Detector loaded: %s on %s imgsz=%s", self.loaded_file, device, imgsz)
                return self.loaded_file
            except Exception as exc:
                errors.append(f"{candidate}: {exc}")
                log.warning("Detector candidate failed: %s", errors[-1])
                self.model = None
        raise RuntimeError("No detector checkpoint could be loaded. " + " | ".join(errors))

    def _build(self, path: str):
        if self.kind == "RT-DETR":
            from ultralytics import RTDETR

            return RTDETR(path)
        from ultralytics import YOLO

        return YOLO(path)

    def _materialize(self, candidate: str) -> str:
        path = Path(candidate)
        if path.is_file():
            return str(path)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        dest = MODELS_DIR / path.name
        if dest.is_file():
            return str(dest)
        probe = self._build(path.name)
        ckpt = Path(getattr(probe, "ckpt_path", "") or path.name)
        if ckpt.is_file() and ckpt.resolve() != dest.resolve():
            shutil.copy2(ckpt, dest)
            if ckpt.parent.resolve() == Path.cwd().resolve():
                ckpt.unlink(missing_ok=True)
        elif not dest.is_file() and Path(path.name).is_file():
            shutil.move(path.name, dest)
        del probe
        if not dest.is_file():
            raise FileNotFoundError(f"Checkpoint was not saved to {dest}")
        return str(dest)

    def _warmup(self) -> None:
        import numpy as np

        blank = np.zeros((self.imgsz, self.imgsz, 3), dtype=np.uint8)
        self._predict(blank, 0.25)

    def detect(self, frame, confidence: float, allowed: set[str]) -> list[Detection]:
        if self.model is None:
            return []
        low = min(0.10, float(confidence))
        result = self._predict(frame, low)
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return []
        xyxy = boxes.xyxy.detach().cpu().numpy()
        confs = boxes.conf.detach().cpu().numpy()
        classes = boxes.cls.detach().cpu().numpy().astype(int)
        detections: list[Detection] = []
        for box, conf, class_id in zip(xyxy, confs, classes):
            raw = self.names.get(int(class_id), str(class_id))
            name = canonical_name(raw)
            if name not in allowed:
                continue
            x1, y1, x2, y2 = [float(v) for v in box]
            if x2 <= x1 or y2 <= y1:
                continue
            detections.append(
                Detection(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=float(conf),
                    class_id=int(class_id),
                    class_name=name,
                )
            )
        return detections

    def _predict(self, frame, confidence: float):
        kwargs = {
            "conf": confidence,
            "iou": 0.50,
            "imgsz": self.imgsz,
            "device": self.device,
            "verbose": False,
        }
        if self.half:
            kwargs["quantize"] = 16
        try:
            results = self.model.predict(frame, **kwargs)
        except Exception:
            if self.half:
                self.half = False
                kwargs.pop("quantize", None)
                log.warning("FP16 inference failed, switching this model to FP32")
                results = self.model.predict(frame, **kwargs)
            else:
                raise
        return results[0]

    def class_names(self) -> list[str]:
        ordered = []
        seen = set()
        for raw in self.names.values():
            name = canonical_name(raw)
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def close(self) -> None:
        self.model = None


class YoloDetector(_UltralyticsBackend):
    name = "YOLO"

    def __init__(self) -> None:
        super().__init__("YOLO")


class RtDetrDetector(_UltralyticsBackend):
    name = "RT-DETR"

    def __init__(self) -> None:
        super().__init__("RT-DETR")


def create_backend(name: str) -> DetectorBackend:
    if name == "RT-DETR":
        return RtDetrDetector()
    return YoloDetector()


def resolve_backend_name(detector: str, device: str) -> str:
    choice = (detector or "AUTO").upper()
    if choice == "RT-DETR":
        return "RT-DETR"
    return "YOLO"


def resolve_profile(detector: str, model: str, device: str) -> str:
    profile = (model or "BALANCED").upper()
    if detector == "AUTO":
        return "FAST" if device == "cpu" else "BALANCED"
    if resolve_backend_name(detector, device) == "RT-DETR" and profile == "FAST":
        return "BALANCED"
    if profile not in {"FAST", "BALANCED", "ACCURATE"}:
        return profile
    return profile
