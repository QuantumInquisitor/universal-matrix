from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import math


class BiometricTelemetryPayload(BaseModel):
    hrv_rr_interval_ms: float = Field(..., ge=300.0, le=2000.0)
    gsr_microsiemens: float = Field(..., ge=0.1, le=100.0)
    eeg_alpha_power: float = Field(..., ge=0.0, le=100.0)
    eeg_theta_power: float = Field(..., ge=0.0, le=100.0)
    eeg_beta_power: float = Field(..., ge=0.0, le=100.0)
    heart_rate_bpm: Optional[float] = Field(default=70.0, ge=30.0, le=220.0)

    @field_validator('gsr_microsiemens')
    def validate_gsr(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("GSR signal must be a finite numerical value.")
        return v


class BiometricLatticeTransformer:
    def __init__(self, base_coherence: float = 1.0):
        self.base_coherence = base_coherence

    def compute_coherence_index(self, payload: BiometricTelemetryPayload) -> Dict[str, Any]:
        eeg_coherence_ratio = payload.eeg_theta_power / (payload.eeg_beta_power + 1e-5)
        hrv_factor = math.tanh(payload.hrv_rr_interval_ms / 1000.0)
        gsr_dampening = 1.0 / (1.0 + math.log1p(payload.gsr_microsiemens))

        modulated_coherence = (
            self.base_coherence * 
            (0.4 * hrv_factor + 0.4 * math.tanh(eeg_coherence_ratio) + 0.2 * gsr_dampening)
        )
        standing_wave_index = round(modulated_coherence * 1.61803398875, 6)

        return {
            "phase_coherence": round(modulated_coherence, 6),
            "standing_wave_index": standing_wave_index,
            "eeg_coherence_ratio": round(eeg_coherence_ratio, 4),
            "hrv_factor": round(hrv_factor, 4),
            "gsr_dampening": round(gsr_dampening, 4),
            "lattice_status": "PHASE_LOCKED" if modulated_coherence > 0.65 else "DECOHERENT"
        }
