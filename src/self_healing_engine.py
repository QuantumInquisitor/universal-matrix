from typing import Dict, Any
from pydantic import BaseModel, Field

class EnvironmentalStressTelemetry(BaseModel):
    chassis_displacement_nm: float = Field(0.0, ge=0.0)
    coil_temp_c: float = Field(20.0, ge=-273.15)
    acoustic_cavitation_index: float = Field(0.1, ge=0.0, le=1.0)
    rf_carrier_drift_hz: float = 0.0

class SelfHealingEngine:
    """
    Phase 41: Closed-loop self-healing engine calculating real-time corrective actions
    for acoustic phase offsets, RF carrier frequencies, and coolant flow rates.
    """
    def compute_healing_adjustments(self, telemetry: EnvironmentalStressTelemetry) -> Dict[str, Any]:
        adjustments = {}
        
        # Thermal & displacement mitigation -> adjust coolant pump flow rate
        if telemetry.coil_temp_c > 45.0 or telemetry.chassis_displacement_nm > 100.0:
            coolant_flow_l_min = round(2.0 + (telemetry.coil_temp_c - 45.0) * 0.1, 2)
            adjustments["coolant_pump_rate_l_min"] = max(2.0, min(15.0, coolant_flow_l_min))
        else:
            adjustments["coolant_pump_rate_l_min"] = 1.0

        # Cavitation mitigation -> shift acoustic phase delay
        if telemetry.acoustic_cavitation_index > 0.4:
            adjustments["acoustic_phase_shift_rad"] = round((1.0 - telemetry.acoustic_cavitation_index) * 0.5, 4)
            adjustments["damping_active"] = True
        else:
            adjustments["acoustic_phase_shift_rad"] = 0.0
            adjustments["damping_active"] = False

        # RF carrier drift compensation
        adjustments["rf_frequency_correction_hz"] = -telemetry.rf_carrier_drift_hz

        has_active_correction = (
            adjustments["coolant_pump_rate_l_min"] > 1.0 or 
            adjustments["damping_active"] or 
            abs(telemetry.rf_carrier_drift_hz) > 0.0
        )

        return {
            "status": "SELF_HEALING_ACTIVE" if has_active_correction else "SYSTEM_NOMINAL",
            "telemetry_evaluated": telemetry.model_dump(),
            "corrective_actions": adjustments,
            "auto_recovery_engaged": has_active_correction
        }
