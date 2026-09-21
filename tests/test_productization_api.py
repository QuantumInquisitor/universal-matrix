import time
import uuid

from src.api_server import (
    EntitlementEvaluateRequest,
    SpatialCommandRequest,
    evaluate_commercial_entitlement,
    validate_spatial_command,
)


def test_spatial_validation_api_accepts_bounded_command():
    session = f"test-{uuid.uuid4()}"
    req = SpatialCommandRequest(
        session_id=session,
        operator_id="operator-test",
        target_id="robot-test",
        sequence_id=1,
        timestamp_ns=time.time_ns(),
        current_position_m=(0.0, 0.0, 0.5),
        position_delta_m=(0.01, 0.0, 0.0),
        linear_velocity_m_s=(0.05, 0.0, 0.0),
        angular_velocity_rad_s=(0.0, 0.05, 0.0),
        deadman_pressed=True,
    )

    result = validate_spatial_command(
        req,
        client_tier="CI",
    )

    assert result["accepted"] is True
    assert result["status"] == "COMMAND_ACCEPTED"
    assert result["hardware_execution_authorized"] is False


def test_spatial_validation_api_rejects_missing_deadman():
    session = f"test-{uuid.uuid4()}"
    req = SpatialCommandRequest(
        session_id=session,
        operator_id="operator-test",
        target_id="robot-test",
        sequence_id=1,
        timestamp_ns=time.time_ns(),
        current_position_m=(0.0, 0.0, 0.5),
        position_delta_m=(0.01, 0.0, 0.0),
        deadman_pressed=False,
    )

    result = validate_spatial_command(
        req,
        client_tier="CI",
    )

    assert result["accepted"] is False
    assert result["status"] == "DEADMAN_REQUIRED"


def test_entitlement_api_reports_requested_feature():
    req = EntitlementEvaluateRequest(
        tenant_id="enterprise-test",
        families=["spatial", "robotics"],
        requested_feature="robotics.trajectory",
    )

    result = evaluate_commercial_entitlement(
        req,
        client_tier="CI",
    )

    assert result["requested_feature_allowed"] is True
    assert "robotics" in result["families"]


def test_entitlement_api_denies_unlicensed_family_feature():
    req = EntitlementEvaluateRequest(
        tenant_id="enterprise-test",
        families=["spatial"],
        requested_feature="manufacturing.gcode",
    )

    result = evaluate_commercial_entitlement(
        req,
        client_tier="CI",
    )

    assert result["requested_feature_allowed"] is False
