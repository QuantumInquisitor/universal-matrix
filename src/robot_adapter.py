"""Common robot adapter contract for Universal Matrix commercial integrations.

The contract standardizes state, command, acknowledgement, stop, and capability
semantics across ROS2, CAN, CNC, simulated robots, digital twins, and future OEM
drivers.

This module defines interfaces and reference in-memory behavior only. It does
not perform real hardware I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import time
from typing import Protocol


Vector3 = tuple[float, float, float]


class RobotMode(StrEnum):
    DISCONNECTED = "disconnected"
    IDLE = "idle"
    READY = "ready"
    MOVING = "moving"
    HOLD = "hold"
    STOPPED = "stopped"
    FAULT = "fault"


class RobotCommandKind(StrEnum):
    POSITION_DELTA = "position_delta"
    VELOCITY = "velocity"
    HOLD = "hold"
    STOP = "stop"


@dataclass(frozen=True)
class RobotState:
    robot_id: str
    mode: RobotMode
    timestamp_ns: int
    position_m: Vector3 = (0.0, 0.0, 0.0)
    linear_velocity_m_s: Vector3 = (0.0, 0.0, 0.0)
    angular_velocity_rad_s: Vector3 = (0.0, 0.0, 0.0)
    fault_code: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RobotCommand:
    robot_id: str
    command_id: str
    kind: RobotCommandKind
    timestamp_ns: int
    position_delta_m: Vector3 = (0.0, 0.0, 0.0)
    linear_velocity_m_s: Vector3 = (0.0, 0.0, 0.0)
    angular_velocity_rad_s: Vector3 = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class RobotAck:
    robot_id: str
    command_id: str
    accepted: bool
    status: str
    timestamp_ns: int
    detail: str = ""


@dataclass(frozen=True)
class RobotCapabilities:
    robot_id: str
    capabilities: frozenset[str]


class RobotAdapter(Protocol):
    def capabilities(self) -> RobotCapabilities:
        ...

    def read_state(self) -> RobotState:
        ...

    def submit(self, command: RobotCommand) -> RobotAck:
        ...

    def stop(self, reason: str = "") -> RobotAck:
        ...


class InMemoryRobotAdapter:
    """Reference adapter for integration tests and product demos."""

    def __init__(self, robot_id: str = "robot-demo") -> None:
        self.robot_id = robot_id
        self._state = RobotState(
            robot_id=robot_id,
            mode=RobotMode.READY,
            timestamp_ns=time.time_ns(),
        )

    def capabilities(self) -> RobotCapabilities:
        return RobotCapabilities(
            robot_id=self.robot_id,
            capabilities=frozenset(
                {
                    "robotics.position_delta",
                    "robotics.velocity",
                    "robotics.hold",
                    "robotics.stop",
                    "robotics.telemetry",
                }
            ),
        )

    def read_state(self) -> RobotState:
        return self._state

    def submit(self, command: RobotCommand) -> RobotAck:
        now = time.time_ns()
        if command.robot_id != self.robot_id:
            return RobotAck(
                robot_id=self.robot_id,
                command_id=command.command_id,
                accepted=False,
                status="TARGET_MISMATCH",
                timestamp_ns=now,
                detail="Command target does not match this adapter.",
            )

        if command.kind is RobotCommandKind.STOP:
            return self.stop("commanded stop")

        if self._state.mode in {RobotMode.FAULT, RobotMode.STOPPED}:
            return RobotAck(
                robot_id=self.robot_id,
                command_id=command.command_id,
                accepted=False,
                status="NOT_READY",
                timestamp_ns=now,
                detail=f"Robot mode is {self._state.mode.value}.",
            )

        position = self._state.position_m
        mode = self._state.mode

        if command.kind is RobotCommandKind.POSITION_DELTA:
            position = tuple(
                a + b for a, b in zip(position, command.position_delta_m)
            )
            mode = RobotMode.MOVING
        elif command.kind is RobotCommandKind.VELOCITY:
            mode = RobotMode.MOVING
        elif command.kind is RobotCommandKind.HOLD:
            mode = RobotMode.HOLD

        self._state = RobotState(
            robot_id=self.robot_id,
            mode=mode,
            timestamp_ns=now,
            position_m=position,
            linear_velocity_m_s=command.linear_velocity_m_s,
            angular_velocity_rad_s=command.angular_velocity_rad_s,
        )

        return RobotAck(
            robot_id=self.robot_id,
            command_id=command.command_id,
            accepted=True,
            status="ACCEPTED",
            timestamp_ns=now,
        )

    def stop(self, reason: str = "") -> RobotAck:
        now = time.time_ns()
        self._state = RobotState(
            robot_id=self.robot_id,
            mode=RobotMode.STOPPED,
            timestamp_ns=now,
            position_m=self._state.position_m,
        )
        return RobotAck(
            robot_id=self.robot_id,
            command_id=f"stop-{now}",
            accepted=True,
            status="STOPPED",
            timestamp_ns=now,
            detail=reason,
        )
