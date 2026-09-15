"""
Biometric Ingestion & Telemetry Mapping Engine (Phase 15)
Maps real-time human biometric signals (HRV, GSR, EEG) onto SO(13)
toroidal field phase-coherence metrics and 19-node energetic lattice states.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import math


class BiometricTelemetryPayload(BaseModel):
    """Pydantic schema for real-time biometric ingestion payload."""
    hrv_rr_interval_ms: float = Field(..., ge=300.0, le=2000.0, description="RR Interval in ms")
    gsr_microsiemens: float = Field(..., ge=0.1, le=100.0, description="Galvanic Skin Response in µS")
    eeg_alpha_power: float = Field(..., ge=0.0, le=100.0, description="Alpha band power (8-12 Hz)")
    eeg_theta_power: float = Field(..., ge=0.0, le=100.0, description="Theta band power (4-8 Hz)")
    eeg_beta_power: float = Field(..., ge=0.0, le=100.0, description="Beta band power (13-30 Hz)")
    heart_rate_bpm: Optional[float] = Field(default=70.0, ge=30.0, le=220.0)

    @field_validator('gsr_microsiemens')
    def validate_gsr(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("GSR signal must be a finite numerical value.")
        return v


class BiometricLatticeTransformer:
    """Translates physiological metrics into SO(13) lattice phase modulations."""

    def __init__(self, base_coherence: float = 1.0):
        self.base_coherence = base_coherence

    def compute_coherence_index(self, payload: BiometricTelemetryPayload) -> Dict[str, Any]:
        """
        Derives phase coherence factor (Phi_T1 / Phi_T0) and standing wave index
        from EEG ratio, HRV variance, and electrodermal arousal.
        """
        # Theta/Beta ratio indicates deep coherence / meditative state
        eeg_coherence_ratio = payload.eeg_theta_power / (payload.eeg_beta_power + 1e-5)
        
        # HRV Coherence factor derived from normalized RR-interval variance
        hrv_factor = math.tanh(payload.hrv_rr_interval_ms / 1000.0)

        # GSR Arousal dampening factor
        gsr_dampening = 1.0 / (1.0 + math.log1p(payload.gsr_microsiemens))

        # Modulated Phase Coherence Factor
        modulated_coherence = (
            self.base_coherence * 
            (0.4 * hrv_factor + 0.4 * math.tanh(eeg_coherence_ratio) + 0.2 * gsr_dampening)
        )

        # Standing Wave Index calculation across 19-node lattice bounds
        standing_wave_index = round(modulated_coherence * 1.61803398875, 6)  # Scaled by Golden Ratio

        return {
            "phase_coherence": round(modulated_coherence, 6),
            "standing_wave_index": standing_wave_index,
            "eeg_coherence_ratio": round(eeg_coherence_ratio, 4),
            "hrv_factor": round(hrv_factor, 4),
            "gsr_dampening": round(gsr_dampening, 4),
            "lattice_status": "PHASE_LOCKED" if modulated_coherence > 0.65 else "DECOHERENT"
        }