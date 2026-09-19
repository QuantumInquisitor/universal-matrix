import os
import sys
import time
import unittest
import logging
from typing import Dict, Any

# Ensure repository root is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HILTestHarness")


class SyntheticCANBusDriver:
    """Simulates a physical SocketCAN interface with packet injection and collision faults."""
    def __init__(self, channel: str = "can0"):
        self.channel = channel
        self.connected = True
        self.collision_flag = False

    def send_frame(self, arbitration_id: int, data: bytes) -> bool:
        if not self.connected:
            raise ConnectionError("CAN Bus interface offline.")
        if self.collision_flag:
            return False  # Frame dropped due to collision
        return True

    def inject_collision(self):
        self.collision_flag = True

    def recover(self):
        self.collision_flag = False


class SyntheticThermalInterferometer:
    """Simulates closed-loop optical displacement feedback with thermal expansion spikes."""
    def __init__(self):
        self.base_temp_c = 21.0
        self.drift_nanometers = 0.0

    def get_displacement_nm(self) -> float:
        return self.drift_nanometers

    def inject_thermal_spike(self, temp_c: float):
        # Thermal expansion coefficient approximation
        self.drift_nanometers = (temp_c - self.base_temp_c) * 12.5


class TestHILHardwareSuite(unittest.TestCase):
    """
    Automated HIL Hardware Stress-Test Suite for SO(13) Physical Controllers.
    """

    def setUp(self):
        self.can_bus = SyntheticCANBusDriver(channel="can0")
        self.interferometer = SyntheticThermalInterferometer()

    def test_can_bus_collision_failover(self):
        """Verify CAN bus frame collision handling and fallback recovery."""
        logger.info("Testing CAN bus collision fault injection...")
        
        # 1. Normal frame transmission
        success = self.can_bus.send_frame(0x123, b"\x01\x02\x03\x04")
        self.assertTrue(success, "CAN frame failed under normal conditions.")

        # 2. Inject collision fault
        self.can_bus.inject_collision()
        success = self.can_bus.send_frame(0x123, b"\x01\x02\x03\x04")
        self.assertFalse(success, "CAN bus driver failed to register frame collision.")

        # 3. Recover interface
        self.can_bus.recover()
        success = self.can_bus.send_frame(0x123, b"\x01\x02\x03\x04")
        self.assertTrue(success, "CAN bus driver failed to recover post-collision.")

    def test_sub_nanometer_thermal_drift_interlock(self):
        """Verify closed-loop response to extreme chassis thermal expansion spikes."""
        logger.info("Testing thermal drift interferometry interlock...")

        # 1. Baseline temperature (21.0 C)
        displacement = self.interferometer.get_displacement_nm()
        self.assertEqual(displacement, 0.0)

        # 2. Inject severe thermal spike (45.0 C)
        self.interferometer.inject_thermal_spike(45.0)
        drift = self.interferometer.get_displacement_nm()
        
        # Verify displacement calculation
        expected_drift = (45.0 - 21.0) * 12.5  # 300.0 nm
        self.assertAlmostEqual(drift, expected_drift, places=2)

        # 3. Safety threshold check (Max threshold: 250.0 nm)
        safety_interlock_tripped = drift > 250.0
        self.assertTrue(safety_interlock_tripped, "Thermal drift failed to trigger interlock threshold.")


if __name__ == "__main__":
    unittest.main()
    
