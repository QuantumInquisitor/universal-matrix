"""Commercial-facing spatial operations control plane.

This module provides a small, dependency-light safety boundary between XR,
robotics, digital-twin, and hardware adapters.

It intentionally does NOT perform physical hardware I/O.

Primary goals:
- deterministic validation of spatial teleoperation commands;
- stale-command and replay rejection;
- deadman-switch enforcement;
- workspace and per-command motion limits;
- bounded command generation suitable for downstream ROS2/CAN/CNC adapters;
- explicit emergency-stop request propagation;
- auditable, serializable decisions.

Real hardware execution remains the responsibility of separately armed drivers
and independent physical safety systems.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import time
from typing import Iterable


Vector3 = tuple[float, float, float]


def _vector3(values: Iterable[float], name: str) -> Vector3:
    data = tuple(float(v) for v in values)
    if len(data) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    if not all(math.isfinite(v) for v in data):
        raise ValueError(f"{name} must contain only finite values")
    return data  # type: ignore[return-value]


def _norm3(v: Vector3) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


@dataclass(frozen=True)
class WorkspaceBounds:
    minimum: Vector3 = (-1.0, -1.0, 0.0)
    maximum: Vector3 = (1.0, 1.0, 1.5)

    def __post_init__(self) -> None:
        object.__setattr__(self, "minimum", _vector3(self.minimum, "minimum"))
        object.__setattr__(self, "maximum", _vector3(self.maximum, "maximum"))
        if any(lo >= hi for lo, hi in zip(self.minimum, self.maximum)):
            raise ValueError("each workspace minimum must be below its maximum")

    def contains(self, point: Iterable[float]) -> bool:
        p = _vector3(point, "point")
        return all(
            lo <= value <= hi
            for value, lo, hi in zip(p, self.minimum, self.maximum)
        )


@dataclass(frozen=True)
class MotionLimits:
    max_command_age_ms: float = 250.0
    max_position_delta_m: float = 0.10
    max_linear_speed_m_s: float = 0.25
    max_angular_speed_rad_s: float = 0.75

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{field_name} must be finite and positive")


@dataclass(frozen=True)
class SpatialCommand:
    session_id: str
    operator_id: str
    target_id: str
    sequence_id: int
    timestamp_ns: int
    position_delta_m: Vector3 = (0.0, 0.0, 0.0)
    linear_velocity_m_s: Vector3 = (0.0, 0.0, 0.0)
    angular_velocity_rad_s: Vector3 = (0.0, 0.0, 0.0)
    deadman_pressed: bool = False
    emergency_stop: bool = False

    def __post_init__(self) -> None:
        if not self.session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not self.operator_id.strip():
            raise ValueError("operator_id must be non-empty")
        if not self.target_id.strip():
            raise ValueError("target_id must be non-empty")
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be non-negative")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative")

        object.__setattr__(
            self,
            "position_delta_m",
            _vector3(self.position_delta_m, "position_delta_m"),
        )
        object.__setattr__(
            self,
            "linear_velocity_m_s",
            _vector3(self.linear_velocity_m_s, "linear_velocity_m_s"),
        )
        object.__setattr__(
            self,
            "angular_velocity_rad_s",
            _vector3(self.angular_velocity_rad_s, "angular_velocity_rad_s"),
        )


@dataclass(frozen=True)
class CommandDecision:
    accepted: bool
    status: str
    reason: str
    session_id: str
    target_id: str
    sequence_id: int
    command_age_ms: float
    requested_position_delta_m: Vector3
    bounded_position_delta_m: Vector3
    bounded_linear_velocity_m_s: Vector3
    bounded_angular_velocity_rad_s: Vector3
    requested_stop: bool
    hardware_execution_authorized: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _scale_to_limit(vector: Vector3, limit: float) -> Vector3:
    magnitude = _norm3(vector)
    if magnitude <= limit or magnitude == 0:
        return vector
    scale = limit / magnitude
    return tuple(v * scale for v in vector)  # type: ignore[return-value]


class SpatialOperationsControlPlane:
    """Validate and bound spatial commands without performing hardware I/O."""

    def __init__(
        self,
        workspace: WorkspaceBounds | None = None,
        limits: MotionLimits | None = None,
    ) -> None:
        self.workspace = workspace or WorkspaceBounds()
        self.limits = limits or MotionLimits()
        self._last_sequence_by_session: dict[str, int] = {}

    def reset_session(self, session_id: str) -> None:
        self._last_sequence_by_session.pop(session_id, None)

    def evaluate(
        self,
        command: SpatialCommand,
        current_position_m: Iterable[float],
        now_ns: int | None = None,
    ) -> CommandDecision:
        current = _vector3(current_position_m, "current_position_m")
        if not self.workspace.contains(current):
            return self._decision(
                command,
                status="CURRENT_POSITION_OUTSIDE_WORKSPACE",
                reason="Current robot/tool position is outside configured workspace bounds.",
                accepted=False,
                age_ms=0.0,
                requested_stop=False,
            )

        now = time.time_ns() if now_ns is None else int(now_ns)
        age_ms = max(0.0, (now - command.timestamp_ns) / 1e6)

        if command.emergency_stop:
            self._last_sequence_by_session[command.session_id] = command.sequence_id
            return self._decision(
                command,
                status="EMERGENCY_STOP_REQUESTED",
                reason=(
                    "Emergency stop request accepted for propagation. "
                    "This software does not guarantee physical power removal."
                ),
                accepted=True,
                age_ms=age_ms,
                requested_stop=True,
            )

        last_sequence = self._last_sequence_by_session.get(command.session_id)
        if last_sequence is not None and command.sequence_id <= last_sequence:
            return self._decision(
                command,
                status="REPLAY_REJECTED",
                reason="Sequence number is not newer than the last accepted session command.",
                accepted=False,
                age_ms=age_ms,
                requested_stop=False,
            )

        if age_ms > self.limits.max_command_age_ms:
            return self._decision(
                command,
                status="STALE_COMMAND_REJECTED",
                reason="Command age exceeds the configured teleoperation limit.",
                accepted=False,
                age_ms=age_ms,
                requested_stop=False,
            )

        if not command.deadman_pressed:
            return self._decision(
                command,
                status="DEADMAN_REQUIRED",
                reason="Motion commands require an active deadman control.",
                accepted=False,
                age_ms=age_ms,
                requested_stop=False,
            )

        bounded_delta = _scale_to_limit(
            command.position_delta_m,
            self.limits.max_position_delta_m,
        )
        bounded_linear = _scale_to_limit(
            command.linear_velocity_m_s,
            self.limits.max_linear_speed_m_s,
        )
        bounded_angular = _scale_to_limit(
            command.angular_velocity_rad_s,
            self.limits.max_angular_speed_rad_s,
        )

        target = tuple(
            current_value + delta
            for current_value, delta in zip(current, bounded_delta)
        )

        if not self.workspace.contains(target):
            return self._decision(
                command,
                status="WORKSPACE_LIMIT_REJECTED",
                reason="Bounded command would move the target outside workspace limits.",
                accepted=False,
                age_ms=age_ms,
                requested_stop=False,
                bounded_delta=bounded_delta,
                bounded_linear=bounded_linear,
                bounded_angular=bounded_angular,
            )

        self._last_sequence_by_session[command.session_id] = command.sequence_id
        return self._decision(
            command,
            status="COMMAND_ACCEPTED",
            reason="Command passed temporal, replay, deadman, motion, and workspace checks.",
            accepted=True,
            age_ms=age_ms,
            requested_stop=False,
            bounded_delta=bounded_delta,
            bounded_linear=bounded_linear,
            bounded_angular=bounded_angular,
        )

    def _decision(
        self,
        command: SpatialCommand,
        *,
        status: str,
        reason: str,
        accepted: bool,
        age_ms: float,
        requested_stop: bool,
        bounded_delta: Vector3 = (0.0, 0.0, 0.0),
        bounded_linear: Vector3 = (0.0, 0.0, 0.0),
        bounded_angular: Vector3 = (0.0, 0.0, 0.0),
    ) -> CommandDecision:
        return CommandDecision(
            accepted=accepted,
            status=status,
            reason=reason,
            session_id=command.session_id,
            target_id=command.target_id,
            sequence_id=command.sequence_id,
            command_age_ms=age_ms,
            requested_position_delta_m=command.position_delta_m,
            bounded_position_delta_m=bounded_delta,
            bounded_linear_velocity_m_s=bounded_linear,
            bounded_angular_velocity_rad_s=bounded_angular,
            requested_stop=requested_stop,
            hardware_execution_authorized=False,
        )


def linear_waypoint_plan(
    start_m: Iterable[float],
    target_m: Iterable[float],
    *,
    max_step_m: float = 0.05,
    workspace: WorkspaceBounds | None = None,
) -> list[Vector3]:
    """Generate a deterministic straight-line waypoint plan.

    This is a geometry helper, not a collision-aware robot motion planner.
    """
    if not math.isfinite(max_step_m) or max_step_m <= 0:
        raise ValueError("max_step_m must be finite and positive")

    start = _vector3(start_m, "start_m")
    target = _vector3(target_m, "target_m")
    bounds = workspace or WorkspaceBounds()

    if not bounds.contains(start):
        raise ValueError("start_m lies outside workspace")
    if not bounds.contains(target):
        raise ValueError("target_m lies outside workspace")

    delta = tuple(b - a for a, b in zip(start, target))
    distance = _norm3(delta)
    if distance == 0:
        return [start]

    segments = max(1, math.ceil(distance / max_step_m))
    return [
        tuple(
            a + (i / segments) * d
            for a, d in zip(start, delta)
        )
        for i in range(segments + 1)
    ]  # type: ignore[return-value]
