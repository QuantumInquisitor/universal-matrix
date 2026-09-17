import math
from typing import Dict, Any
from pydantic import BaseModel, Field

class ArcSimulationPayload(BaseModel):
    gap_distance_mm: float = Field(5.0, ge=0.1, le=100.0)
    gas_pressure_torr: float = Field(760.0, ge=1.0) # Baseline 1 atm = 760 Torr
    applied_voltage_kv: float = Field(20.0, ge=0.1)
    magnetic_pinch_field_tesla: float = Field(0.5, ge=0.0)

class PlasmaArcTwinEngine:
    """
    Phase 42: Non-linear plasma breakdown simulator predicting spark-gap arc formation,
    ionization threshold voltages (Paschen's Law), and magnetic pinch dynamics.
    """
    def simulate_plasma_discharge(self, payload: ArcSimulationPayload) -> Dict[str, Any]:
        # Paschen's Law breakdown voltage approximation for Air: V_b = (B * p * d) / ln(A * p * d / ln(1 + 1/gamma))
        pd = (payload.gas_pressure_torr / 760.0) * (payload.gap_distance_mm / 10.0)  # pressure * distance product (atm*cm)
        breakdown_voltage_kv = round(30.0 * pd + 1.35 * math.sqrt(pd), 2)  # Approx ~30 kV/cm for air at 1 atm

        arc_triggered = payload.applied_voltage_kv >= breakdown_voltage_kv
        
        # Plasma channel electron temperature (eV) and magnetic pinch radius contraction
        electron_temp_ev = round(1.5 + (payload.applied_voltage_kv / max(1.0, breakdown_voltage_kv)) * 3.5, 2) if arc_triggered else 0.0
        pinch_ratio = round(1.0 / (1.0 + payload.magnetic_pinch_field_tesla * 0.8), 3) if arc_triggered else 1.0

        return {
            "status": "PLASMA_ARC_SIMULATION_COMPLETE",
            "calculated_breakdown_voltage_kv": breakdown_voltage_kv,
            "arc_breakdown_triggered": arc_triggered,
            "plasma_electron_temp_ev": electron_temp_ev,
            "channel_magnetic_pinch_ratio": pinch_ratio,
            "arc_stability_index": round(min(1.0, (payload.magnetic_pinch_field_tesla + 0.1) / 2.0), 2) if arc_triggered else 0.0
        }
