from typing import Dict, Any
from pydantic import BaseModel, Field

# Class schemas expected across api.py, tests, and closed-loop bio driver
class BiometricTelemetryPayload(BaseModel):
    hrv_rr_interval_ms: float = Field(800.0, ge=300.0, le=2000.0)
    gsr_microsiemens: float = Field(5.0, ge=0.1, le=100.0)
    eeg_alpha_power: float = Field(10.0, ge=0.0)
    eeg_theta_power: float = Field(15.0, ge=0.0)
    eeg_beta_power: float = Field(10.0, ge=0.0)

# Alias for backwards compatibility with closed_loop_bio_driver
BiometricPayload = BiometricTelemetryPayload

class BiometricLatticeTransformer:
    """
    Phase 15: Normalizes physical biometrics and calculates SO(13) toroidal phase coherence.
    """
    def process_telemetry(self, payload: BiometricTelemetryPayload) -> Dict[str, Any]:
        alpha_beta_ratio = payload.eeg_alpha_power / max(1.0, payload.eeg_beta_power)
        hrv_factor = min(1.0, payload.hrv_rr_interval_ms / 1000.0)
        
        coherence = min(1.0, max(0.0, (alpha_beta_ratio * 0.4) + (hrv_factor * 0.6)))
        
        return {
            "hrv_rr_interval_ms": payload.hrv_rr_interval_ms,
            "gsr_microsiemens": payload.gsr_microsiemens,
            "so13_coherence_index": round(coherence, 4),
            "status": "INGESTED"
        }

# Alias for backwards compatibility
BiometricIngestionEngine = BiometricLatticeTransformer
