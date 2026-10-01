"""Real detector checkpoints and custom-model discovery.

FAST / BALANCED / ACCURATE map to released Ultralytics weights.
YOLO26 is preferred. YOLO11 and YOLOv8 remain as fallbacks if a
checkpoint cannot be downloaded. Custom aerial weights dropped into
models/ or custom_models/ are listed separately.
"""

from __future__ import annotations

from pathlib import Path

from utils.paths import CUSTOM_MODELS_DIR, MODELS_DIR

YOLO_PROFILES = {
    "FAST": ["yolo26n.pt", "yolo11n.pt", "yolov8n.pt"],
    "BALANCED": ["yolo26s.pt", "yolo11s.pt", "yolov8s.pt"],
    "ACCURATE": ["yolo26m.pt", "yolo11m.pt", "yolov8m.pt"],
}

YOLO_IMGSZ = {
    "FAST": 640,
    "BALANCED": 960,
    "ACCURATE": 1280,
}

RTDETR_PROFILES = {
    "FAST": ["rtdetr-l.pt"],
    "BALANCED": ["rtdetr-l.pt"],
    "ACCURATE": ["rtdetr-x.pt"],
}

KNOWN_WEIGHTS = {name for names in YOLO_PROFILES.values() for name in names}
KNOWN_WEIGHTS.update(name for names in RTDETR_PROFILES.values() for name in names)

CANONICAL_CLASSES = {
    "car": "CAR",
    "truck": "TRUCK",
    "bus": "BUS",
    "motorcycle": "MOTORCYCLE",
    "motorbike": "MOTORCYCLE",
    "van": "TRUCK",
    "pickup": "TRUCK",
    "suv": "CAR",
}


def canonical_name(raw: str) -> str:
    key = str(raw).strip().lower().replace(" ", "_")
    return CANONICAL_CLASSES.get(key, str(raw).strip().upper() or "OBJECT")


class ModelRegistry:
    def profiles(self, backend: str) -> list[str]:
        if backend == "RT-DETR":
            return ["BALANCED", "ACCURATE"]
        return ["FAST", "BALANCED", "ACCURATE"]

    def candidates(self, backend: str, profile: str) -> list[str]:
        table = RTDETR_PROFILES if backend == "RT-DETR" else YOLO_PROFILES
        if profile not in table:
            profile = "BALANCED" if backend == "RT-DETR" else "FAST"
        return list(table[profile])

    def imgsz(self, backend: str, profile: str) -> int:
        if backend == "RT-DETR":
            return 640
        return YOLO_IMGSZ.get(profile, 960)

    def custom_models(self) -> list[Path]:
        found: list[Path] = []
        seen: set[str] = set()
        for folder in (CUSTOM_MODELS_DIR, MODELS_DIR):
            if not folder.exists():
                continue
            for path in sorted(folder.glob("*.pt")):
                if path.name in KNOWN_WEIGHTS or path.name in seen:
                    continue
                seen.add(path.name)
                found.append(path)
        return found

    def resolve_custom(self, name: str) -> Path | None:
        for path in self.custom_models():
            if path.name == name or str(path) == name:
                return path
        return None
