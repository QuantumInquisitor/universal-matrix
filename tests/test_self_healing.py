import unittest
from src.self_healing_engine import SelfHealingEngine, EnvironmentalStressTelemetry

class TestSelfHealingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SelfHealingEngine()

    def test_nominal_telemetry_no_healing_needed(self):
        telemetry = EnvironmentalStressTelemetry(
            chassis_displacement_nm=10.0,
            coil_temp_c=30.0,
            acoustic_cavitation_index=0.1,
            rf_carrier_drift_hz=0.0
        )
        res = self.engine.compute_healing_adjustments(telemetry)
        self.assertEqual(res["status"], "SYSTEM_NOMINAL")
        self.assertFalse(res["auto_recovery_engaged"])

    def test_active_self_healing_trigger(self):
        telemetry = EnvironmentalStressTelemetry(
            chassis_displacement_nm=150.0,
            coil_temp_c=65.0,
            acoustic_cavitation_index=0.6,
            rf_carrier_drift_hz=12.5
        )
        res = self.engine.compute_healing_adjustments(telemetry)
        self.assertEqual(res["status"], "SELF_HEALING_ACTIVE")
        self.assertTrue(res["auto_recovery_engaged"])
        self.assertGreater(res["corrective_actions"]["coolant_pump_rate_l_min"], 2.0)
        self.assertTrue(res["corrective_actions"]["damping_active"])
        self.assertEqual(res["corrective_actions"]["rf_frequency_correction_hz"], -12.5)

if __name__ == '__main__':
    unittest.main()
