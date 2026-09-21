"""Versioned spatial operations protocol.

The protocol is intentionally transport-neutral. It can be serialized to JSON
and carried over HTTP, WebSocket, message queues, ROS2 bridges, CAN gateways, or
other customer-specific transports.

This module defines software messages only. It does not authorize physical
hardware execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import json
import math
import time
from typing import Any, Mapping


PROTOCOL_NAME = "universal-matrix-spatial"
PROTOCOL_VERSION = "0.1"


class MessageType(StrEnum):
    COMMAND = "command"
    ACK = "ack"
    TELEMETRY = "telemetry"
    STOP = "stop"
    CAPABILITIES = "capabilities"


class CommandType(StrEnum):
    POSITION_DELTA = "position_delta"
    VELOCITY = "velocity"
    HOLD = "hold"
    EMERGENCY_STOP = "emergency_stop"


class AckStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"


@dataclass(frozen=True)
class SpatialEnvelope:
    message_type: MessageType
    session_id: str
    source_id: str
    target_id: str
    sequence_id: int
    timestamp_ns: int
    payload: Mapping[str, Any]
    protocol_name: str = PROTOCOL_NAME
    protocol_version: str = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        if not self.session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not self.source_id.strip():
            raise ValueError("source_id must be non-empty")
        if not self.target_id.strip():
            raise ValueError("target_id must be non-empty")
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be non-negative")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative")
        if self.protocol_name != PROTOCOL_NAME:
            raise ValueError("unsupported protocol_name")
        if self.protocol_version != PROTOCOL_VERSION:
            raise ValueError("unsupported protocol_version")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["message_type"] = self.message_type.value
        return data

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SpatialEnvelope":
        required = {
            "message_type",
            "session_id",
            "source_id",
            "target_id",
            "sequence_id",
            "timestamp_ns",
            "payload",
        }
        missing = sorted(required.difference(data))
        if missing:
            raise ValueError(
                "missing protocol fields: " + ", ".join(missing)
            )

        return cls(
            message_type=MessageType(str(data["message_type"])),
            session_id=str(data["session_id"]),
            source_id=str(data["source_id"]),
            target_id=str(data["target_id"]),
            sequence_id=int(data["sequence_id"]),
            timestamp_ns=int(data["timestamp_ns"]),
            payload=dict(data["payload"]),
            protocol_name=str(
                data.get("protocol_name", PROTOCOL_NAME)
            ),
            protocol_version=str(
                data.get("protocol_version", PROTOCOL_VERSION)
            ),
        )

    @classmethod
    def from_json(cls, raw: str) -> "SpatialEnvelope":
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("protocol JSON must decode to an object")
        return cls.from_dict(value)


def command_envelope(
    *,
    session_id: str,
    source_id: str,
    target_id: str,
    sequence_id: int,
    command_type: CommandType,
    payload: Mapping[str, Any] | None = None,
    timestamp_ns: int | None = None,
) -> SpatialEnvelope:
    command_payload = dict(payload or {})
    command_payload["command_type"] = command_type.value
    return SpatialEnvelope(
        message_type=(
            MessageType.STOP
            if command_type is CommandType.EMERGENCY_STOP
            else MessageType.COMMAND
        ),
        session_id=session_id,
        source_id=source_id,
        target_id=target_id,
        sequence_id=sequence_id,
        timestamp_ns=(
            time.time_ns()
            if timestamp_ns is None
            else int(timestamp_ns)
        ),
        payload=command_payload,
    )


def acknowledgement_envelope(
    command: SpatialEnvelope,
    *,
    source_id: str,
    status: AckStatus,
    reason: str = "",
    applied_sequence_id: int | None = None,
    timestamp_ns: int | None = None,
) -> SpatialEnvelope:
    if command.message_type not in {
        MessageType.COMMAND,
        MessageType.STOP,
    }:
        raise ValueError("acknowledgements require a command or stop envelope")

    payload = {
        "status": status.value,
        "reason": reason,
        "acknowledged_sequence_id": command.sequence_id,
        "applied_sequence_id": applied_sequence_id,
    }
    return SpatialEnvelope(
        message_type=MessageType.ACK,
        session_id=command.session_id,
        source_id=source_id,
        target_id=command.source_id,
        sequence_id=command.sequence_id,
        timestamp_ns=(
            time.time_ns()
            if timestamp_ns is None
            else int(timestamp_ns)
        ),
        payload=payload,
    )


def telemetry_envelope(
    *,
    session_id: str,
    source_id: str,
    target_id: str,
    sequence_id: int,
    position_m: tuple[float, float, float] | None = None,
    linear_velocity_m_s: tuple[float, float, float] | None = None,
    angular_velocity_rad_s: tuple[float, float, float] | None = None,
    device_state: str = "unknown",
    extras: Mapping[str, Any] | None = None,
    timestamp_ns: int | None = None,
) -> SpatialEnvelope:
    payload: dict[str, Any] = {
        "device_state": device_state,
    }

    def finite_vec(
        value: tuple[float, float, float] | None,
        name: str,
    ) -> list[float] | None:
        if value is None:
            return None
        if len(value) != 3:
            raise ValueError(f"{name} must contain three values")
        converted = [float(x) for x in value]
        if not all(math.isfinite(x) for x in converted):
            raise ValueError(f"{name} must contain finite values")
        return converted

    position = finite_vec(position_m, "position_m")
    linear = finite_vec(
        linear_velocity_m_s,
        "linear_velocity_m_s",
    )
    angular = finite_vec(
        angular_velocity_rad_s,
        "angular_velocity_rad_s",
    )

    if position is not None:
        payload["position_m"] = position
    if linear is not None:
        payload["linear_velocity_m_s"] = linear
    if angular is not None:
        payload["angular_velocity_rad_s"] = angular
    if extras:
        payload["extras"] = dict(extras)

    return SpatialEnvelope(
        message_type=MessageType.TELEMETRY,
        session_id=session_id,
        source_id=source_id,
        target_id=target_id,
        sequence_id=sequence_id,
        timestamp_ns=(
            time.time_ns()
            if timestamp_ns is None
            else int(timestamp_ns)
        ),
        payload=payload,
    )


def capabilities_envelope(
    *,
    session_id: str,
    source_id: str,
    target_id: str,
    sequence_id: int,
    capabilities: list[str],
    timestamp_ns: int | None = None,
) -> SpatialEnvelope:
    return SpatialEnvelope(
        message_type=MessageType.CAPABILITIES,
        session_id=session_id,
        source_id=source_id,
        target_id=target_id,
        sequence_id=sequence_id,
        timestamp_ns=(
            time.time_ns()
            if timestamp_ns is None
            else int(timestamp_ns)
        ),
        payload={
            "capabilities": sorted(set(capabilities)),
        },
    )
