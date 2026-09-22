import time

from src.digital_twin_contract import DigitalTwinSnapshot, measured_value
from src.digital_twin_store import DigitalTwinStore
from src.robot_adapter import (
    InMemoryRobotAdapter,
    RobotCommand,
    RobotCommandKind,
    RobotMode,
)
from src.spatial_protocol import CommandType, command_envelope
from src.xr_robot_bridge import XRRobotBridge


def test_robot_adapter_accepts_position_delta():
    adapter = InMemoryRobotAdapter("robot-1")
    ack = adapter.submit(
        RobotCommand(
            robot_id="robot-1",
            command_id="cmd-1",
            kind=RobotCommandKind.POSITION_DELTA,
            timestamp_ns=time.time_ns(),
            position_delta_m=(0.01, 0.0, 0.0),
        )
    )

    assert ack.accepted
    assert adapter.read_state().position_m == (0.01, 0.0, 0.0)
    assert adapter.read_state().mode is RobotMode.MOVING


def test_robot_adapter_stop_is_explicit():
    adapter = InMemoryRobotAdapter("robot-2")
    ack = adapter.stop("operator requested")
    assert ack.accepted
    assert adapter.read_state().mode is RobotMode.STOPPED


def test_twin_store_keeps_latest_and_bounded_history():
    store = DigitalTwinStore(history_limit=2)

    for i in range(3):
        snapshot = DigitalTwinSnapshot(
            twin_id="twin-1",
            asset_id="robot-3",
            timestamp_ns=i + 1,
            values=(
                measured_value(
                    name="x",
                    value=float(i),
                    unit="m",
                    source="robot-3",
                    timestamp_ns=i + 1,
                ),
            ),
        )
        store.put(snapshot)

    assert store.latest("robot-3").timestamp_ns == 3
    assert [x.timestamp_ns for x in store.history("robot-3")] == [2, 3]


def test_xr_bridge_requires_deadman():
    adapter = InMemoryRobotAdapter("robot-4")
    bridge = XRRobotBridge(adapter)

    envelope = command_envelope(
        session_id="s1",
        source_id="xr-1",
        target_id="robot-4",
        sequence_id=1,
        command_type=CommandType.POSITION_DELTA,
        payload={
            "delta_m": [0.01, 0.0, 0.0],
            "deadman_pressed": False,
        },
        timestamp_ns=time.time_ns(),
    )

    ack = bridge.handle(envelope)
    assert not ack.accepted
    assert ack.status == "DEADMAN_REQUIRED"


def test_xr_bridge_validates_then_submits_bounded_command():
    adapter = InMemoryRobotAdapter("robot-5")
    bridge = XRRobotBridge(adapter)

    envelope = command_envelope(
        session_id="s2",
        source_id="xr-2",
        target_id="robot-5",
        sequence_id=1,
        command_type=CommandType.POSITION_DELTA,
        payload={
            "delta_m": [0.5, 0.0, 0.0],
            "deadman_pressed": True,
        },
        timestamp_ns=time.time_ns(),
    )

    ack = bridge.handle(envelope)
    assert ack.accepted
    # Default safety plane limits a single position delta to 0.10 m.
    assert adapter.read_state().position_m == (0.1, 0.0, 0.0)


def test_xr_emergency_stop_bypasses_motion_but_not_adapter_stop_path():
    adapter = InMemoryRobotAdapter("robot-6")
    bridge = XRRobotBridge(adapter)

    envelope = command_envelope(
        session_id="s3",
        source_id="xr-3",
        target_id="robot-6",
        sequence_id=1,
        command_type=CommandType.EMERGENCY_STOP,
        timestamp_ns=time.time_ns(),
    )

    ack = bridge.handle(envelope)
    assert ack.accepted
    assert adapter.read_state().mode is RobotMode.STOPPED
