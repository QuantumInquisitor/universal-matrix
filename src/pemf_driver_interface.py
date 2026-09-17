import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class PEMFPulseConfig(BaseModel):
    peak_voltage_kv: float = Field(15.0, ge=0.5, le=100.0)
    pulse_width_us: float = Field(2.5, ge=0.1, le=1000.0)
    repetition_rate_hz: float = Field(432.0, ge=1.0)
    tesla_triad_harmonic: int = Field(3, ge=1, le=9)
    so13_phase_angle_rad: float = 0.0

class PEMFDriverInterface:
    """
    Phase 40: Embedded driver interface synthesizing microsecond high-voltage
    pulsed electromagnetic discharge sequences aligned with Tesla triad harmonics.
    """
    def synthesize_pulse_train(self, config: PEMFPulseConfig) -> Dict[str, Any]:
        # Duty cycle calculation (D = Pulse_Width / Period)
        period_us = (1.0 / config.repetition_rate_hz) * 1e6
        duty_cycle_percent = round((config.pulse_width_us / period_us) * 100, 4)

        # Tesla triad modulation scalar (3-6-9 resonance factor)
        triad_scaler = (config.tesla_triad_harmonic / 9.0) * math.cos(config.so13_phase_angle_rad)
        effective_field_energy_mJ = round(0.5 * (config.peak_voltage_kv ** 2) * (config.pulse_width_us * 1e-3) * (1.0 + abs(triad_scaler)), 2)

        return {
            "status": "PEMF_PULSE_SEQUENCE_READY",
            "peak_voltage_kv": config.peak_voltage_kv,
            "period_microseconds": round(period_us, 2),
            "duty_cycle_percent": duty_cycle_percent,
            "effective_field_energy_mJ": effective_field_energy_mJ,
            "discharge_gate_trigger": "SOLID_STATE_MARX_ENABLED",
            "overvoltage_safety_interlock": config.peak_voltage_kv < 90.0
        }
