import unittest
import os
from src.config import SystemConfig
from src.hal.factory import HALFactory

class TestPhase70HAL(unittest.TestCase):
    def test_default_config_is_mock(self):
        cfg = SystemConfig()
        self.assertIn(cfg.SYSTEM_MODE, ["MOCK", "REAL"])

    def test_hal_factory_mode(self):
        mode = HALFactory.get_driver_mode()
        self.assertTrue(mode in ["REAL_WORLD_BARE_METAL", "SIMULATED_MOCK_HIL"])

if __name__ == "__main__":
    unittest.main()

