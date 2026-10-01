"""Two-axis PID used only to shape the virtual control output."""

from __future__ import annotations

PID_DEFAULTS = {
    "h_kp": 80.0,
    "h_ki": 0.0,
    "h_kd": 5.0,
    "v_kp": 80.0,
    "v_ki": 0.0,
    "v_kd": 5.0,
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class _Axis:
    def __init__(self, kp: float, ki: float, kd: float) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_t: float | None = None

    def set_gains(self, kp: float, ki: float, kd: float) -> None:
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)

    def reset(self) -> None:
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_t = None

    def update(self, error: float, timestamp: float) -> float:
        if self.prev_t is None:
            dt = 1.0 / 30.0
        else:
            dt = _clamp(timestamp - self.prev_t, 1e-3, 0.5)
        self.integral = _clamp(self.integral + error * dt, -1.5, 1.5)
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        self.prev_t = timestamp
        return self.kp * error + self.ki * self.integral + self.kd * derivative


class PidController:
    def __init__(self) -> None:
        self.horizontal = _Axis(**{k: PID_DEFAULTS[f"h_{k}"] for k in ("kp", "ki", "kd")})
        self.vertical = _Axis(**{k: PID_DEFAULTS[f"v_{k}"] for k in ("kp", "ki", "kd")})

    def set_gains(self, gains: dict) -> None:
        base = dict(PID_DEFAULTS)
        base.update(gains or {})
        self.horizontal.set_gains(base["h_kp"], base["h_ki"], base["h_kd"])
        self.vertical.set_gains(base["v_kp"], base["v_ki"], base["v_kd"])

    def reset(self) -> None:
        self.horizontal.reset()
        self.vertical.reset()

    def update(self, x_norm: float, y_norm: float, dead_zone: float, timestamp: float):
        raw_x = self.horizontal.update(x_norm, timestamp)
        raw_y = self.vertical.update(y_norm, timestamp)
        dead = max(0.0, min(0.95, dead_zone))
        if abs(x_norm) <= dead:
            self.horizontal.integral *= 0.5
            lateral = 0.0
        else:
            lateral = _clamp(raw_x, -100.0, 100.0)
        if abs(y_norm) <= dead:
            self.vertical.integral *= 0.5
            forward = 0.0
        else:
            forward = _clamp(-raw_y, -100.0, 100.0)
        return lateral, forward, raw_x, raw_y
