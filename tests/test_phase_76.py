import unittest
from src.drivers.cnc_driver import CNCMotionDriver

class TestPhase76CNCDriver(unittest.TestCase):
    def setUp(self):
        self.driver = CNCMotionDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "CNCMotionDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_gcode_execution(self):
        res = self.driver.execute_gcode_command("G01 X10 Y10")
        self.assertIn("status", res)
        self.assertEqual(res["command"], "G01 X10 Y10")

if __name__ == "__main__":
    unittest.main()

