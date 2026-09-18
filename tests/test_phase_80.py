import unittest
from src.drivers.spacex_driver import SpaceXDriver

class TestPhase80SpaceXDriver(unittest.TestCase):
    def setUp(self):
        self.driver = SpaceXDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "SpaceXDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_telemetry_fetch(self):
        res = self.driver.get_constellation_telemetry(limit=2)
        self.assertIn("status", res)
        self.assertIn("satellites", res)

if __name__ == "__main__":
    unittest.main()

