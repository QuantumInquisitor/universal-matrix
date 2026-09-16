from typing import Dict, Any, List
from pydantic import BaseModel, Field

class SensorTelemetryPayload(BaseModel):
    magnetometer_uT: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0]) # [Bx, By, Bz] in microteslas
    hall_effect_voltage_v: float = Field(2.5, ge=0.0, le=5.0)
    clock_drift_nanoseconds: float = 0.0

class PhysicalFieldCorrector:
    """
    Phase 21: Ingests live hardware sensor feeds and calculates real-time
    SO(13) matrix compensation parameters for physical field drift.
    """
    def __init__(self, baseline_field_uT: float = 45.0):
        self.baseline_field_uT = baseline_field_uT

    def process_sensor_feed(self, payload: SensorTelemetryPayload) -> Dict[str, Any]:
        # Compute magnetic magnitude vector
        bx, by, bz = payload.magnetometer_uT
        magnitude = (bx**2 + by**2 + bz**2) ** 0.5

        # Field deviation delta from baseline Earth magnetic field
        field_delta = magnitude - self.baseline_field_uT

        # Calculate SO(13) compensation angle shift (radians)
        compensation_angle_rad = round((field_delta / 100.0) + (payload.clock_drift_nanoseconds * 1e-9), 6)

        return {
            "magnetic_magnitude_uT": round(magnitude, 4),
            "field_delta_uT": round(field_delta, 4),
            "clock_drift_ns": payload.clock_drift_nanoseconds,
            "so13_compensation_angle_rad": compensation_angle_rad,
            "correction_applied": abs(compensation_angle_rad) > 0.000001
        }
