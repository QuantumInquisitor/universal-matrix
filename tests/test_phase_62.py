import unittest
from src.hardware_mocks import HardwareIntegrationTestFixture, VirtualCANInterface, VirtualMarxGateArrayMock

class TestPhase62HardwareMocks(unittest.TestCase):
    def setUp(self):
        self.fixture = HardwareIntegrationTestFixture()

    def test_can_mock_transmission(self):
        can_interface = VirtualCANInterface()
        res = can_interface.send_pulse_command(node_id=0x120, pulse_width_us=50.0)
        self.assertTrue(res)
        self.assertEqual(len(can_interface.tx_buffer), 1)

    def test_marx_mock_discharge(self):
        marx_mock = VirtualMarxGateArrayMock()
        res = marx_mock.arm_and_fire(voltage_kv=100.0, pulse_delay_ns=200)
        self.assertEqual(res["status"], "FIRED")
        self.assertAlmostEqual(res["peak_voltage_kv"], 98.0)

    def test_end_to_end_hil_pipeline(self):
        initial_state = [0.5, 1.5, 2.5, 0.1, 0.2, 0.3]
        report = self.fixture.run_end_to_end_loop(initial_state)
        self.assertEqual(report["status"], "HIL_INTEGRATION_SUCCESS")
        self.assertTrue(report["can_bus_tx"])
        self.assertEqual(report["marx_discharge"]["status"], "FIRED")
        self.assertGreaterEqual(report["tx_frames_count"], 1)

if __name__ == "__main__":
    unittest.main()

