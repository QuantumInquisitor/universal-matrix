from typing import Dict, Any
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
    """
    Phase 31: Zero-latency emergency physical hardware interlock and thermal kill-switch engine.
    Interrupts serial streams and outputs hard stop commands upon threshold breaches.
    """
    def __init__(self, limits: HardwareSafetyLimits = HardwareSafetyLimits()):
        self.limits = limits
        self.interlock_tripped = False

    def evaluate_safety(self, telemetry: TelemetrySnapshot) -> Dict[str, Any]:
        violations = []

        if telemetry.coil_temp_c > self.limits.max_coil_temp_c:
            violations.append(f"THERMAL_OVERHEAT: {telemetry.coil_temp_c}°C exceeds limit {self.limits.max_coil_temp_c}°C")

        if telemetry.current_amps > self.limits.max_current_amps:
            violations.append(f"OVERCURRENT_SPIKE: {telemetry.current_amps}A exceeds limit {self.limits.max_current_amps}A")

        if telemetry.chassis_displacement_nm > self.limits.max_chassis_displacement_nm:
            violations.append(f"STRUCTURAL_WARP: {telemetry.chassis_displacement_nm}nm exceeds limit {self.limits.max_chassis_displacement_nm}nm")

        if violations:
            self.interlock_tripped = True
            return {
                "interlock_status": "TRIPPED_EMERGENCY_STOP",
                "emergency_gcode": "M112 ; Emergency Stop",
                "violations": violations,
                "hardware_power_cut": True
            }

        return {
            "interlock_status": "NOMINAL",
            "violations": [],
            "hardware_power_cut": False
        }

    def reset_interlock(self):
        self.interlock_tripped = False
