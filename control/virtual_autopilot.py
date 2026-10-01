"""Virtual autopilot.

The output is a simulated camera-following command derived from image
error. It is not a flight controller and must not be sent to motors,
Pixhawk, PX4, MAVLink, or MAVSDK.
"""

from __future__ import annotations

import math

from control.command_state import compose_command, speed_command
from control.pid_controller import PID_DEFAULTS, PidController
from control.proportional_controller import ProportionalController
from utils.datatypes import ControlOutput


class VirtualAutopilot:
    def __init__(self) -> None:
        self.proportional = ProportionalController()
        self.pid = PidController()
        self.mode = "SIMPLE"
        self._gains = dict(PID_DEFAULTS)

    def configure(self, mode: str, gains: dict | None) -> None:
        mode = (mode or "SIMPLE").upper()
        gains = dict(PID_DEFAULTS if not gains else {**PID_DEFAULTS, **gains})
        if mode != self.mode or gains != self._gains:
            self.pid.reset()
        self.mode = mode
        self._gains = gains
        self.pid.set_gains(gains)

    def reset(self) -> None:
        self.pid.reset()

    def step(
        self,
        aim_point,
        frame_w: int,
        frame_h: int,
        dead_zone: float,
        timestamp: float,
        active: bool,
        distance_trend: str,
        size_rate: float,
    ) -> ControlOutput:
        if not active or aim_point is None or frame_w <= 0 or frame_h <= 0:
            return ControlOutput()
        x_error = float(aim_point[0]) - frame_w * 0.5
        y_error = float(aim_point[1]) - frame_h * 0.5
        x_norm = x_error / (frame_w * 0.5)
        y_norm = y_error / (frame_h * 0.5)
        pid_x = 0.0
        pid_y = 0.0
        if self.mode == "PID":
            lateral, forward, pid_x, pid_y = self.pid.update(x_norm, y_norm, dead_zone, timestamp)
        else:
            lateral, forward = self.proportional.update(x_norm, y_norm, dead_zone)
        centered = abs(lateral) < 0.5 and abs(forward) < 0.5
        return ControlOutput(
            x_error_px=x_error,
            y_error_px=y_error,
            x_norm=x_norm,
            y_norm=y_norm,
            magnitude=math.hypot(x_norm, y_norm) * 100.0,
            centered=centered,
            command=compose_command(lateral, forward),
            lateral_pct=lateral,
            forward_pct=forward,
            speed_command=speed_command(distance_trend, size_rate),
            pid_x=pid_x,
            pid_y=pid_y,
            active=True,
        )
