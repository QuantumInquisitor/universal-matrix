from __future__ import annotations

from pydantic import BaseModel

from src.biometric_ingestion import BiometricIngestionEngine, BiometricPayload


class AdaptiveResonanceState(BaseModel):
    toroidal_coherence: float
    target_rf_freq_hz: float
    visual_pulse_hz: float
    resonance_locked: bool
    model_status: str = "advisory_visualization_only_no_rf_transmission"


class ClosedLoopBioDriver:
    """Legacy-compatible biometric-to-display advisory mapper.

    This class does not transmit RF, prescribe stimulation, or implement a
    validated biomedical feedback law. The historical RF-frequency field is
    retained as an advisory numeric output only.
    """

    def __init__(self, base_freq_hz: float = 432_000_000.0):
        self.base_freq_hz = base_freq_hz
        self.bio_engine = BiometricIngestionEngine()

    def process_and_adapt(self, payload: BiometricPayload) -> AdaptiveResonanceState:
        bio_result = self.bio_engine.process_telemetry(payload)
        score = bio_result["telemetry_feature_score"]

        frequency_shift = (1.0 - score) * 1_000_000.0
        advisory_freq = self.base_freq_hz + frequency_shift
        visual_pulse = 8.0 + score * 5.0

        return AdaptiveResonanceState(
            toroidal_coherence=round(score, 4),
            target_rf_freq_hz=round(advisory_freq, 2),
            visual_pulse_hz=round(visual_pulse, 2),
            resonance_locked=score >= 0.75,
        )
