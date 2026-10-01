"""Virtual command names. These are simulation labels, not actuator outputs."""

HOLD = "HOLD"
LEFT = "LEFT"
RIGHT = "RIGHT"
FORWARD = "FORWARD"
BACK = "BACK"
SPEED_UP = "SPEED UP"
SLOW_DOWN = "SLOW DOWN"
HOLD_SPEED = "HOLD SPEED"


def compose_command(lateral_pct: float, forward_pct: float) -> str:
    parts: list[str] = []
    if forward_pct > 0.5:
        parts.append(FORWARD)
    elif forward_pct < -0.5:
        parts.append(BACK)
    if lateral_pct > 0.5:
        parts.append(RIGHT)
    elif lateral_pct < -0.5:
        parts.append(LEFT)
    if not parts:
        return HOLD
    if len(parts) == 2:
        return f"{parts[0]} + {parts[1]}"
    return parts[0]


def speed_command(distance_trend: str, size_rate: float) -> str:
    if distance_trend == "RECEDING":
        return SPEED_UP
    if distance_trend == "APPROACHING" and size_rate > 0.15:
        return SLOW_DOWN
    return HOLD_SPEED
