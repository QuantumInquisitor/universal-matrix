import unittest
from src.topology_calibrator import TopologyCalibratorEngine

class TestPhase69TopologyCalibrator(unittest.TestCase):
    def setUp(self):
        self.calibrator = TopologyCalibratorEngine()

    def test_calibration_idle_state(self):
        self.assertEqual(self.calibrator.calibration_state, "IDLE")

    def test_field_calibration(self):
        telemetry = [1.02, 0.98, 1.05, 1.01]
        res = self.calibrator.calibrate_field_topology(telemetry)
        self.assertEqual(res["status"], "TOPOLOGY_CALIBRATED")
        self.assertEqual(res["calibration_state"], "CALIBRATED")
        self.assertIn("compensation_factor", res)
        self.assertIn("phase_drift_hz", res)

if __name__ == "__main__":
    unittest.main()

