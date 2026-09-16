import unittest
from src.cnc_hardware_controller import CNCGRBLController, MachinePosition

class TestCNCGRBLController(unittest.TestCase):
    def setUp(self):
        self.controller = CNCGRBLController(mock_mode=True)

    def test_mock_gcode_transmission(self):
        res = self.controller.send_gcode_line("G0 X10 Y10 Z0")
        self.assertEqual(res["status"], "OK_MOCK")
        self.assertEqual(res["command"], "G0 X10 Y10 Z0")

    def test_telemetry_polling_structure(self):
        telemetry = self.controller.poll_telemetry()
        self.assertIsInstance(telemetry, MachinePosition)
        self.assertEqual(telemetry.state, "Idle")

if __name__ == '__main__':
    unittest.main()
