import unittest
from src.drivers.can_driver import CANDriver

class TestPhase71CANDriver(unittest.TestCase):
    def setUp(self):
        self.driver = CANDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "CANDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_send_frame(self):
        res = self.driver.send_telemetry_frame(0x1A0, [0x01, 0x02, 0x03, 0x04])
        self.assertIn("status", res)
        self.assertTrue(res["status"].startswith("SENT_"))

if __name__ == "__main__":
    unittest.main()

