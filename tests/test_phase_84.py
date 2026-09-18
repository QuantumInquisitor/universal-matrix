import unittest
from src.hal.safety_driver import SafetyInterlockDriver

class TestPhase84Safety(unittest.TestCase):
    def setUp(self):
        self.driver = SafetyInterlockDriver()

    def test_nominal_velocity(self):
        res = self.driver.validate_spatial_vector(100.0)
        self.assertEqual(res["status"], "NOMINAL")

    def test_e_stop_trigger(self):
        res = self.driver.validate_spatial_vector(5000.0)
        self.assertEqual(res["status"], "E_STOP_TRIGGERED")

if __name__ == "__main__":
    unittest.main()
