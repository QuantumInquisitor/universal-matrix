import time

import pytest

from src.spatial_operations_control import (
    MotionLimits,
    SpatialCommand,
    SpatialOperationsControlPlane,
    WorkspaceBounds,
    linear_waypoint_plan,
)


def _command(**overrides):
    base = dict(
        session_id="session-1",
        operator_id="operator-1",
        target_id="robot-1",
        sequence_id=1,
        timestamp_ns=time.time_ns(),
        position_delta_m=(0.02, 0.0, 0.0),
        linear_velocity_m_s=(0.1, 0.0, 0.0),
        angular_velocity_rad_s=(0.0, 0.1, 0.0),
        deadman_pressed=True,
        emergency_stop=False,
    )
    base.update(overrides)
    return SpatialCommand(**base)


def test_nominal_command_is_accepted():
    plane = SpatialOperationsControlPlane()
    result = plane.evaluate(_command(), current_position_m=(0.0, 0.0, 0.5))
    assert result.accepted
    assert result.status == "COMMAND_ACCEPTED"
    assert result.hardware_execution_authorized is False


def test_replay_is_rejected():
    plane = SpatialOperationsControlPlane()
    cmd = _command(sequence_id=10)
    assert plane.evaluate(cmd, (0.0, 0.0, 0.5)).accepted

    replay = _command(sequence_id=10)
    result = plane.evaluate(replay, (0.0, 0.0, 0.5))
    assert not result.accepted
    assert result.status == "REPLAY_REJECTED"


def test_stale_command_is_rejected():
    plane = SpatialOperationsControlPlane(
        limits=MotionLimits(max_command_age_ms=10.0)
    )
    stale = _command(
        timestamp_ns=time.time_ns() - 50_000_000,
    )
    result = plane.evaluate(stale, (0.0, 0.0, 0.5))
    assert not result.accepted
    assert result.status == "STALE_COMMAND_REJECTED"


def test_deadman_is_required():
    plane = SpatialOperationsControlPlane()
    result = plane.evaluate(
        _command(deadman_pressed=False),
        (0.0, 0.0, 0.5),
    )
    assert not result.accepted
    assert result.status == "DEADMAN_REQUIRED"


def test_motion_vectors_are_bounded():
    plane = SpatialOperationsControlPlane(
        limits=MotionLimits(
            max_position_delta_m=0.05,
            max_linear_speed_m_s=0.2,
            max_angular_speed_rad_s=0.3,
        )
    )
    result = plane.evaluate(
        _command(
            position_delta_m=(1.0, 0.0, 0.0),
            linear_velocity_m_s=(1.0, 0.0, 0.0),
            angular_velocity_rad_s=(0.0, 2.0, 0.0),
        ),
        (0.0, 0.0, 0.5),
    )
    assert result.accepted
    assert result.bounded_position_delta_m == pytest.approx((0.05, 0.0, 0.0))
    assert result.bounded_linear_velocity_m_s == pytest.approx((0.2, 0.0, 0.0))
    assert result.bounded_angular_velocity_rad_s == pytest.approx((0.0, 0.3, 0.0))


def test_workspace_violation_is_rejected():
    plane = SpatialOperationsControlPlane(
        workspace=WorkspaceBounds(
            minimum=(-0.5, -0.5, 0.0),
            maximum=(0.5, 0.5, 1.0),
        )
    )
    result = plane.evaluate(
        _command(position_delta_m=(0.2, 0.0, 0.0)),
        current_position_m=(0.45, 0.0, 0.5),
    )
    assert not result.accepted
    assert result.status == "WORKSPACE_LIMIT_REJECTED"


def test_emergency_stop_can_propagate_without_deadman():
    plane = SpatialOperationsControlPlane()
    result = plane.evaluate(
        _command(
            deadman_pressed=False,
            emergency_stop=True,
        ),
        (0.0, 0.0, 0.5),
    )
    assert result.accepted
    assert result.requested_stop
    assert result.status == "EMERGENCY_STOP_REQUESTED"
    assert result.hardware_execution_authorized is False


def test_linear_waypoint_plan_respects_step_limit():
    points = linear_waypoint_plan(
        (0.0, 0.0, 0.5),
        (0.2, 0.0, 0.5),
        max_step_m=0.05,
    )
    assert points[0] == pytest.approx((0.0, 0.0, 0.5))
    assert points[-1] == pytest.approx((0.2, 0.0, 0.5))
    assert len(points) == 5


def test_linear_waypoint_plan_rejects_out_of_bounds_target():
    with pytest.raises(ValueError):
        linear_waypoint_plan(
            (0.0, 0.0, 0.5),
            (5.0, 0.0, 0.5),
        )
