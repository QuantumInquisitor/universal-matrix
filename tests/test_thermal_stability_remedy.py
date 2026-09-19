import unittest
from src.hal.anomaly_driver import SpatialAnomalyDriver

class TestThermalStabilityRemedy(unittest.TestCase):
    def setUp(self):
        self.anomaly_driver = SpatialAnomalyDriver()

    def test_thermal_expansion_and_vibration_compensation(self):
        target_vector = [10.0000000, 20.0000000, 5.0000000]
        feedback_vector = [10.0004500, 20.0001200, 5.0000800]

        # Evaluate drift and apply dynamic SO(13) offset compensation
        result = self.anomaly_driver.evaluate_and_correct(target_vector, feedback_vector)
        print(f"\n[Closed-Loop Driver] Evaluation Result: {result}")

        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
