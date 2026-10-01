"""AI Drone Vehicle Tracking & Virtual Autopilot."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from app.main_window import MainWindow
    from utils.logger import get_logger
    from utils.paths import ensure_dirs

    ensure_dirs()
    log = get_logger()
    log.info("Application Start")

    def _excepthook(exc_type, exc, tb):
        log.exception("Unhandled exception", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    code = app.exec()
    log.info("Application exit %s", code)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
