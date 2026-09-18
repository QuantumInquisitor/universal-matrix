import unittest
from src.drivers.marx_driver import MarxGeneratorDriver

class TestPhase77MarxDriver(unittest.TestCase):
    def setUp(self):
        self.driver = MarxGeneratorDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "MarxGeneratorDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_pulse_trigger(self):
        res = self.driver.trigger_discharge_pulse(30.0)
        self.assertIn("status", res)
        self.assertEqual(res["discharge_voltage_kv"], 30.0)

if __name__ == "__main__":
    unittest.main()

