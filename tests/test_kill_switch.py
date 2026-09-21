import unittest
from src.hardware_kill_switch import SafetyInterlockKernel, HardwareSafetyLimits, TelemetrySnapshot

class TestSafetyInterlockKernel(unittest.TestCase):
    def setUp(self):
        self.kernel = SafetyInterlockKernel(HardwareSafetyLimits(max_coil_temp_c=85.0, max_current_amps=20.0))

    def test_nominal_telemetry(self):
        telemetry = TelemetrySnapshot(coil_temp_c=45.0, current_amps=10.0, chassis_displacement_nm=50.0)
        res = self.kernel.evaluate_safety(telemetry)
        self.assertEqual(res["interlock_status"], "NOMINAL")
        self.assertFalse(res["hardware_power_cut"])

    def test_thermal_and_current_emergency_trip(self):
        telemetry = TelemetrySnapshot(coil_temp_c=92.0, current_amps=25.0, chassis_displacement_nm=10.0)
        res = self.kernel.evaluate_safety(telemetry)
        self.assertEqual(res["interlock_status"], "TRIPPED_SOFTWARE_INTERLOCK")
        self.assertFalse(res["hardware_power_cut"])
        self.assertTrue(res["hardware_power_cut_requested"])
        self.assertEqual(res["emergency_gcode"], "M112 ; Emergency Stop")
        self.assertEqual(len(res["violations"]), 2)

if __name__ == '__main__':
    unittest.main()
