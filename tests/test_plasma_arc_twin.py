import unittest
from src.plasma_arc_twin import PlasmaArcTwinEngine, ArcSimulationPayload

class TestPlasmaArcTwinEngine(unittest.TestCase):
    def setUp(self):
        self.twin = PlasmaArcTwinEngine()

    def test_sub_breakdown_voltage(self):
        payload = ArcSimulationPayload(
            gap_distance_mm=10.0,  # ~1 cm -> ~31.35 kV breakdown
            gas_pressure_torr=760.0,
            applied_voltage_kv=15.0,  # Below breakdown
            magnetic_pinch_field_tesla=0.5
        )
        res = self.twin.simulate_plasma_discharge(payload)
        self.assertEqual(res["status"], "PLASMA_ARC_SIMULATION_COMPLETE")
        self.assertFalse(res["arc_breakdown_triggered"])
        self.assertEqual(res["plasma_electron_temp_ev"], 0.0)

    def test_arc_breakdown_triggered(self):
        payload = ArcSimulationPayload(
            gap_distance_mm=5.0,  # ~0.5 cm -> ~15.5 kV breakdown
            gas_pressure_torr=760.0,
            applied_voltage_kv=25.0,  # Exceeds breakdown
            magnetic_pinch_field_tesla=1.2
        )
        res = self.twin.simulate_plasma_discharge(payload)
        self.assertTrue(res["arc_breakdown_triggered"])
        self.assertGreater(res["plasma_electron_temp_ev"], 0.0)
        self.assertLess(res["channel_magnetic_pinch_ratio"], 1.0)

if __name__ == '__main__':
    unittest.main()
