import unittest
from src.hal.anomaly_driver import SpatialAnomalyDriver

class TestPhase88Anomaly(unittest.TestCase):
    def setUp(self):
        self.driver = SpatialAnomalyDriver(drift_tolerance=0.05)

    def test_nominal_alignment(self):
        res = self.driver.evaluate_and_correct([1.0, 1.0, 1.0], [1.0, 1.0, 1.0])
        self.assertFalse(res["drift_detected"])
        self.assertEqual(res["status"], "NOMINAL_ALIGNMENT")

    def test_drift_correction_triggered(self):
        res = self.driver.evaluate_and_correct([1.0, 0.0, 0.0], [0.8, 0.0, 0.0])
        self.assertTrue(res["drift_detected"])
        self.assertEqual(res["status"], "ANOMALY_CORRECTED")
        self.assertAlmostEqual(res["corrected_vector"][0], 1.2)

if __name__ == "__main__":
    unittest.main()
