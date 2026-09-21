from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HardwareSafetyLimits(BaseModel):
    max_coil_temp_c: float = Field(85.0, ge=0.0)
    max_current_amps: float = Field(20.0, ge=0.0)
    max_chassis_displacement_nm: float = Field(500.0, ge=0.0)


class TelemetrySnapshot(BaseModel):
    coil_temp_c: float
    current_amps: float
    chassis_displacement_nm: float


class SafetyInterlockKernel:
    """Software threshold interlock.

    This object can request an emergency stop but cannot itself guarantee power
    removal. Physical systems require an independent hardware interlock.
    """

    def __init__(self, limits: HardwareSafetyLimits | None = None):
        self.limits = limits or HardwareSafetyLimits()
        self.interlock_tripped = False

    def evaluate_safety(self, telemetry: TelemetrySnapshot) -> dict[str, Any]:
        violations = []

        if telemetry.coil_temp_c > self.limits.max_coil_temp_c:
            violations.append(
                f"THERMAL_OVERHEAT: {telemetry.coil_temp_c} C exceeds "
                f"{self.limits.max_coil_temp_c} C"
            )
        if telemetry.current_amps > self.limits.max_current_amps:
            violations.append(
                f"OVERCURRENT: {telemetry.current_amps} A exceeds "
                f"{self.limits.max_current_amps} A"
            )
        if (
            telemetry.chassis_displacement_nm
            > self.limits.max_chassis_displacement_nm
        ):
            violations.append(
                f"DISPLACEMENT: {telemetry.chassis_displacement_nm} nm exceeds "
                f"{self.limits.max_chassis_displacement_nm} nm"
            )

        if violations:
            self.interlock_tripped = True
            return {
                "interlock_status": "TRIPPED_SOFTWARE_INTERLOCK",
                "emergency_gcode": "M112 ; Emergency Stop",
                "violations": violations,
                "hardware_power_cut": False,
                "hardware_power_cut_requested": True,
                "model_status": "software_request_requires_independent_hardware_interlock",
            }

        return {
            "interlock_status": "NOMINAL",
            "violations": [],
            "hardware_power_cut": False,
            "hardware_power_cut_requested": False,
        }

    def reset_interlock(self) -> None:
        self.interlock_tripped = False
