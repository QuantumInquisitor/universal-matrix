import json

import pytest

from src.digital_twin_contract import (
    DigitalTwinSnapshot,
    QualityLevel,
    TelemetryKind,
    TelemetryValue,
    derived_value,
    measured_value,
    snapshot_from_mapping,
)


def test_measured_value_preserves_calibration_and_uncertainty():
    value = measured_value(
        name="temperature",
        value=42.5,
        unit="degC",
        source="sensor-1",
        quality=QualityLevel.GOOD,
        calibration_id="cal-2026-09",
        uncertainty=0.2,
        timestamp_ns=100,
    )

    assert value.kind is TelemetryKind.MEASURED
    assert value.calibration_id == "cal-2026-09"
    assert value.uncertainty == 0.2


def test_derived_value_is_not_marked_measured():
    value = derived_value(
        name="health_index",
        value=0.87,
        unit="1",
        source="digital-twin-model",
        timestamp_ns=200,
    )

    assert value.kind is TelemetryKind.DERIVED
    assert value.quality is QualityLevel.UNKNOWN


def test_snapshot_separates_measured_and_derived_values():
    measured = measured_value(
        name="vibration",
        value=1.5,
        unit="mm/s",
        source="sensor-a",
        timestamp_ns=300,
    )
    derived = derived_value(
        name="maintenance_score",
        value=0.3,
        unit="1",
        source="model-a",
        timestamp_ns=300,
    )

    snapshot = DigitalTwinSnapshot(
        twin_id="twin-1",
        asset_id="asset-1",
        timestamp_ns=300,
        values=(measured, derived),
    )

    assert snapshot.measured_values == (measured,)
    assert snapshot.derived_values == (derived,)


def test_snapshot_serialization_is_json_safe():
    snapshot = snapshot_from_mapping(
        twin_id="twin-2",
        asset_id="asset-2",
        measured={
            "temperature": (25.0, "degC", "sensor-temp"),
        },
        derived={
            "health_index": (0.95, "1", "health-model"),
        },
        timestamp_ns=400,
    )

    payload = json.loads(snapshot.to_json())
    assert payload["schema_version"] == "0.1"
    assert payload["values"][0]["kind"] == "measured"
    assert payload["values"][1]["kind"] == "derived"


def test_nonfinite_numeric_telemetry_is_rejected():
    with pytest.raises(ValueError):
        TelemetryValue(
            name="bad",
            value=float("inf"),
            unit="1",
            kind=TelemetryKind.MEASURED,
            source="sensor",
            timestamp_ns=500,
        )


def test_negative_uncertainty_is_rejected():
    with pytest.raises(ValueError):
        measured_value(
            name="pressure",
            value=100.0,
            unit="kPa",
            source="sensor",
            uncertainty=-0.1,
            timestamp_ns=600,
        )
