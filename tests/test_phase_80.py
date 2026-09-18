import unittest
from src.drivers.spacex_driver import SpaceXDriver

class TestPhase80SpaceXDriver(unittest.TestCase):
    def setUp(self):
        self.driver = SpaceXDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "SpaceXDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_telemetry_and_look_angles(self):
        res = self.driver.get_constellation_telemetry(observer_lat=34.0522, observer_lon=-118.2437)
        self.assertIn("status", res)
        self.assertIn("satellites", res)
        self.assertIn("tracking_angles", res["satellites"][0])

    def test_dishy_grpc_query(self):
        res = self.driver.query_dishy_grpc_status()
        self.assertIn("status", res)
        self.assertIn("downlink_mbps", res)

if __name__ == "__main__":
    unittest.main()

