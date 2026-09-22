"""XR-to-robot command bridge.

The bridge connects versioned spatial protocol messages to the bounded spatial
operations control plane and a RobotAdapter. It never bypasses command
validation and never enables real hardware by itself.
"""

from __future__ import annotations

import time
import uuid

from .robot_adapter import RobotAdapter, RobotCommand, RobotCommandKind, RobotAck
from .spatial_operations_control import SpatialCommand, SpatialOperationsControlPlane
from .spatial_protocol import CommandType, MessageType, SpatialEnvelope


class XRRobotBridge:
    def __init__(
        self,
        adapter: RobotAdapter,
        control_plane: SpatialOperationsControlPlane | None = None,
    ) -> None:
        self.adapter = adapter
        self.control_plane = control_plane or SpatialOperationsControlPlane()

    def handle(self, envelope: SpatialEnvelope) -> RobotAck:
        if envelope.message_type not in {MessageType.COMMAND, MessageType.STOP}:
            raise ValueError("XR bridge accepts command or stop envelopes only")

        command_type = CommandType(str(envelope.payload.get("command_type")))

        state = self.adapter.read_state()

        if command_type is CommandType.EMERGENCY_STOP:
            return self.adapter.stop("XR emergency-stop request")

        spatial = SpatialCommand(
            session_id=envelope.session_id,
            operator_id=envelope.source_id,
            target_id=envelope.target_id,
            sequence_id=envelope.sequence_id,
            timestamp_ns=envelope.timestamp_ns,
            position_delta_m=tuple(envelope.payload.get("delta_m", (0.0, 0.0, 0.0))),
            linear_velocity_m_s=tuple(
                envelope.payload.get("linear_velocity_m_s", (0.0, 0.0, 0.0))
            ),
            angular_velocity_rad_s=tuple(
                envelope.payload.get("angular_velocity_rad_s", (0.0, 0.0, 0.0))
            ),
            deadman_pressed=bool(envelope.payload.get("deadman_pressed", False)),
        )

        decision = self.control_plane.evaluate(
            spatial,
            current_position_m=state.position_m,
            now_ns=time.time_ns(),
        )

        if not decision.accepted:
            return RobotAck(
                robot_id=state.robot_id,
                command_id=f"reject-{envelope.sequence_id}",
                accepted=False,
                status=decision.status,
                timestamp_ns=time.time_ns(),
                detail=decision.reason,
            )

        if command_type is CommandType.POSITION_DELTA:
            kind = RobotCommandKind.POSITION_DELTA
        elif command_type is CommandType.VELOCITY:
            kind = RobotCommandKind.VELOCITY
        elif command_type is CommandType.HOLD:
            kind = RobotCommandKind.HOLD
        else:
            raise ValueError(f"unsupported command type: {command_type}")

        robot_command = RobotCommand(
            robot_id=envelope.target_id,
            command_id=str(uuid.uuid4()),
            kind=kind,
            timestamp_ns=time.time_ns(),
            position_delta_m=decision.bounded_position_delta_m,
            linear_velocity_m_s=decision.bounded_linear_velocity_m_s,
            angular_velocity_rad_s=decision.bounded_angular_velocity_rad_s,
        )
        return self.adapter.submit(robot_command)
