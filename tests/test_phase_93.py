import unittest
from src.core.digital_twin import DigitalTwinEngine

class TestPhase93Twin(unittest.TestCase):
    def setUp(self):
        self.engine = DigitalTwinEngine(max_stress_threshold=100.0)

    def test_nominal_twin_sync(self):
        res = self.engine.update_twin_state(30.0, [0.5, 0.5, 0.5])
        self.assertEqual(res["status"], "TWIN_SYNC_COMPLETE")
        self.assertFalse(res["predictive_maintenance_flag"])
        self.assertGreater(res["composite_health_index"], 0.7)

    def test_degradation_alert(self):
        res = self.engine.update_twin_state(120.0, [20.0, 20.0, 20.0])
        self.assertTrue(res["predictive_maintenance_flag"])
        self.assertLess(res["composite_health_index"], 0.3)

if __name__ == "__main__":
    unittest.main()
