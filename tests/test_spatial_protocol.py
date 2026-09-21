import json

import pytest

from src.spatial_protocol import (
    AckStatus,
    CommandType,
    MessageType,
    PROTOCOL_NAME,
    PROTOCOL_VERSION,
    SpatialEnvelope,
    acknowledgement_envelope,
    capabilities_envelope,
    command_envelope,
    telemetry_envelope,
)


def test_command_round_trip_json():
    command = command_envelope(
        session_id="session-1",
        source_id="xr-client",
        target_id="robot-1",
        sequence_id=7,
        command_type=CommandType.POSITION_DELTA,
        payload={"delta_m": [0.01, 0.0, 0.0]},
        timestamp_ns=123456,
    )

    encoded = command.to_json()
    decoded = SpatialEnvelope.from_json(encoded)

    assert decoded == command
    assert decoded.protocol_name == PROTOCOL_NAME
    assert decoded.protocol_version == PROTOCOL_VERSION
    assert decoded.message_type is MessageType.COMMAND


def test_emergency_stop_uses_stop_message_type():
    command = command_envelope(
        session_id="session-2",
        source_id="operator-console",
        target_id="robot-2",
        sequence_id=8,
        command_type=CommandType.EMERGENCY_STOP,
        timestamp_ns=100,
    )
    assert command.message_type is MessageType.STOP
    assert command.payload["command_type"] == "emergency_stop"


def test_acknowledgement_points_back_to_command():
    command = command_envelope(
        session_id="session-3",
        source_id="xr-client",
        target_id="robot-3",
        sequence_id=9,
        command_type=CommandType.HOLD,
        timestamp_ns=200,
    )
    ack = acknowledgement_envelope(
        command,
        source_id="robot-3",
        status=AckStatus.ACCEPTED,
        reason="validated",
        applied_sequence_id=9,
        timestamp_ns=250,
    )

    assert ack.message_type is MessageType.ACK
    assert ack.target_id == "xr-client"
    assert ack.payload["acknowledged_sequence_id"] == 9
    assert ack.payload["applied_sequence_id"] == 9


def test_telemetry_serializes_finite_vectors():
    telemetry = telemetry_envelope(
        session_id="session-4",
        source_id="robot-4",
        target_id="digital-twin",
        sequence_id=10,
        position_m=(0.1, 0.2, 0.3),
        linear_velocity_m_s=(0.0, 0.1, 0.0),
        angular_velocity_rad_s=(0.0, 0.0, 0.2),
        device_state="ready",
        extras={"temperature_c": 42.0},
        timestamp_ns=300,
    )

    data = telemetry.to_dict()
    assert data["message_type"] == "telemetry"
    assert data["payload"]["position_m"] == [0.1, 0.2, 0.3]
    assert data["payload"]["device_state"] == "ready"


def test_telemetry_rejects_nonfinite_vectors():
    with pytest.raises(ValueError):
        telemetry_envelope(
            session_id="session-5",
            source_id="robot-5",
            target_id="digital-twin",
            sequence_id=11,
            position_m=(0.0, float("nan"), 0.0),
        )


def test_capabilities_are_unique_and_sorted():
    envelope = capabilities_envelope(
        session_id="session-6",
        source_id="robot-6",
        target_id="operator-console",
        sequence_id=12,
        capabilities=[
            "robotics.velocity",
            "robotics.stop",
            "robotics.velocity",
        ],
        timestamp_ns=400,
    )

    assert envelope.payload["capabilities"] == [
        "robotics.stop",
        "robotics.velocity",
    ]


def test_unknown_protocol_version_is_rejected():
    data = {
        "message_type": "telemetry",
        "session_id": "s",
        "source_id": "a",
        "target_id": "b",
        "sequence_id": 1,
        "timestamp_ns": 1,
        "payload": {},
        "protocol_name": PROTOCOL_NAME,
        "protocol_version": "999",
    }

    with pytest.raises(ValueError):
        SpatialEnvelope.from_dict(data)


def test_json_must_be_object():
    with pytest.raises(ValueError):
        SpatialEnvelope.from_json(json.dumps([1, 2, 3]))
