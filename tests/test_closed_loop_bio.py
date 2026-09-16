import unittest
from src.biometric_ingestion import BiometricPayload
from src.closed_loop_bio_driver import ClosedLoopBioDriver

class TestClosedLoopBioDriver(unittest.TestCase):
    def setUp(self):
        self.driver = ClosedLoopBioDriver(base_freq_hz=432000000.0)

    def test_adaptive_resonance_feedback(self):
        payload = BiometricPayload(
            hrv_rr_interval_ms=900.0,
            gsr_microsiemens=3.5,
            eeg_alpha_power=18.0,
            eeg_theta_power=12.0,
            eeg_beta_power=5.0
        )
        state = self.driver.process_and_adapt(payload)
        self.assertGreater(state.toroidal_coherence, 0.0)
        self.assertGreater(state.target_rf_freq_hz, 0.0)
        self.assertGreaterEqual(state.visual_pulse_hz, 8.0)

if __name__ == '__main__':
    unittest.main()
