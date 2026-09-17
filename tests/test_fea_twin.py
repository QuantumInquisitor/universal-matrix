import unittest
from src.fea_stress_twin import FEAStressTwinEngine, FEAToolpathPayload

class TestFEAStressTwinEngine(unittest.TestCase):
    def setUp(self):
        self.twin = FEAStressTwinEngine()

    def test_nominal_toolpath_simulation(self):
        payload = FEAToolpathPayload(toolpath_length_mm=200.0, current_load_amps=5.0)
        res = self.twin.simulate_toolpath_stress(payload)
        self.assertGreater(res["safety_factor"], 1.5)
        self.assertFalse(res["structural_failure_risk"])
        self.assertTrue(res["execution_approved"])

    def test_overstress_toolpath_simulation(self):
        payload = FEAToolpathPayload(toolpath_length_mm=5000.0, current_load_amps=40.0)
        res = self.twin.simulate_toolpath_stress(payload)
        self.assertLess(res["safety_factor"], 1.5)
        self.assertTrue(res["structural_failure_risk"])
        self.assertFalse(res["execution_approved"])

if __name__ == '__main__':
    unittest.main()
