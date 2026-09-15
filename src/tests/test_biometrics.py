import unittest
from src.biometric_ingestion import BiometricTelemetryPayload, BiometricLatticeTransformer
from pydantic import ValidationError


class TestBiometricIngestionEngine(unittest.TestCase):

    def setUp(self):
        self.transformer = BiometricLatticeTransformer(base_coherence=1.0)
        self.valid_payload = BiometricTelemetryPayload(
            hrv_rr_interval_ms=850.0,
            gsr_microsiemens=4.2,
            eeg_alpha_power=15.5,
            eeg_theta_power=22.1,
            eeg_beta_power=8.3,
            heart_rate_bpm=72.0
        )

    def test_valid_payload_transformation(self):
        result = self.transformer.compute_coherence_index(self.valid_payload)
        self.assertIn("phase_coherence", result)
        self.assertIn("standing_wave_index", result)
        self.assertGreater(result["phase_coherence"], 0.0)
        self.assertEqual(result["lattice_status"], "PHASE_LOCKED")

    def test_out_of_bounds_hrv_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            BiometricTelemetryPayload(
                hrv_rr_interval_ms=100.0,  # Below 300ms minimum
                gsr_microsiemens=4.2,
                eeg_alpha_power=10.0,
                eeg_theta_power=10.0,
                eeg_beta_power=10.0
            )

    def test_decoherent_state_calculation(self):
        decoherent_payload = BiometricTelemetryPayload(
            hrv_rr_interval_ms=350.0,
            gsr_microsiemens=85.0,  # High stress / electrodermal arousal
            eeg_alpha_power=2.0,
            eeg_theta_power=1.0,
            eeg_beta_power=45.0     # High stress beta dominance
        )
        result = self.transformer.compute_coherence_index(decoherent_payload)
        self.assertEqual(result["lattice_status"], "DECOHERENT")


if __name__ == "__main__":
    unittest.main()
    