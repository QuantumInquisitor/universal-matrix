from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BiometricTelemetryPayload(BaseModel):
    hrv_rr_interval_ms: float = Field(800.0, ge=300.0, le=2000.0)
    gsr_microsiemens: float = Field(5.0, ge=0.1, le=100.0)
    eeg_alpha_power: float = Field(10.0, ge=0.0)
    eeg_theta_power: float = Field(15.0, ge=0.0)
    eeg_beta_power: float = Field(10.0, ge=0.0)


BiometricPayload = BiometricTelemetryPayload


class BiometricLatticeTransformer:
    """Experimental normalized telemetry score.

    The returned score is a software feature constructed from alpha/beta ratio
    and an HRV term. It is not a clinical biomarker, diagnosis, treatment
    metric, or validated measure of biological coherence.
    """

    def process_telemetry(
        self,
        payload: BiometricTelemetryPayload,
    ) -> dict[str, Any]:
        alpha_beta_ratio = payload.eeg_alpha_power / max(
            1.0,
            payload.eeg_beta_power,
        )
        hrv_factor = min(1.0, payload.hrv_rr_interval_ms / 1000.0)
        score = min(
            1.0,
            max(0.0, (alpha_beta_ratio * 0.4) + (hrv_factor * 0.6)),
        )
        score = round(score, 4)

        return {
            "hrv_rr_interval_ms": payload.hrv_rr_interval_ms,
            "gsr_microsiemens": payload.gsr_microsiemens,
            "telemetry_feature_score": score,
            "so13_coherence_index": score,
            "status": "INGESTED",
            "model_status": "experimental_feature_not_clinical_metric",
        }

    def compute_coherence_index(
        self,
        payload: BiometricTelemetryPayload,
    ) -> dict[str, Any]:
        return self.process_telemetry(payload)


BiometricIngestionEngine = BiometricLatticeTransformer
