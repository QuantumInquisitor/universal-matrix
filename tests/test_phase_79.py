import unittest
from src.drivers.fpga_driver import FPGADriver

class TestPhase79FPGADriver(unittest.TestCase):
    def setUp(self):
        self.driver = FPGADriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "FPGADriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_hdl_flashing(self):
        res = self.driver.compile_and_flash_hdl("module top(); endmodule")
        self.assertIn("status", res)

if __name__ == "__main__":
    unittest.main()

