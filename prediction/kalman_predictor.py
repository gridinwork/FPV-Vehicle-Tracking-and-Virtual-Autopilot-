"""Constant-velocity Kalman predictor for the locked target."""

from __future__ import annotations

import numpy as np


class KalmanPredictor:
    def __init__(self) -> None:
        self.x = None
        self.p = None
        self.last_t = None
        self.h = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])
        self.r = np.eye(2) * 9.0
        self.q_pos = 2.0
        self.q_vel = 25.0

    @property
    def ready(self) -> bool:
        return self.x is not None

    def reset(self, x: float, y: float, timestamp: float) -> None:
        self.x = np.array([x, y, 0.0, 0.0], dtype=float)
        self.p = np.eye(4) * 40.0
        self.p[2:, 2:] *= 20.0
        self.last_t = timestamp

    def predict(self, timestamp: float) -> tuple[float, float]:
        if self.x is None:
            return 0.0, 0.0
        dt = 1.0 / 30.0 if self.last_t is None else max(1e-3, min(0.5, timestamp - self.last_t))
        f = np.eye(4)
        f[0, 2] = dt
        f[1, 3] = dt
        q = np.eye(4)
        q[0, 0] = q[1, 1] = self.q_pos * dt
        q[2, 2] = q[3, 3] = self.q_vel * dt
        self.x = f @ self.x
        self.p = f @ self.p @ f.T + q
        self.last_t = timestamp
        return float(self.x[0]), float(self.x[1])

    def update(self, x: float, y: float, timestamp: float) -> tuple[float, float]:
        if self.x is None:
            self.reset(x, y, timestamp)
            return x, y
        self.predict(timestamp)
        z = np.array([x, y], dtype=float)
        y_res = z - self.h @ self.x
        s = self.h @ self.p @ self.h.T + self.r
        k = self.p @ self.h.T @ np.linalg.inv(s)
        self.x = self.x + k @ y_res
        self.p = (np.eye(4) - k @ self.h) @ self.p
        self.last_t = timestamp
        return float(self.x[0]), float(self.x[1])

    @property
    def position(self) -> tuple[float, float]:
        if self.x is None:
            return 0.0, 0.0
        return float(self.x[0]), float(self.x[1])

    @property
    def velocity(self) -> tuple[float, float]:
        if self.x is None:
            return 0.0, 0.0
        return float(self.x[2]), float(self.x[3])
