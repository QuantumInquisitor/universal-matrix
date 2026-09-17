import unittest
from src.natural_units_converter import NaturalUnitsConverter
from src.grid_power_manager import GridPowerManager

class TestPhase46And49(unittest.TestCase):
    def test_natural_units_converter(self):
        conv = NaturalUnitsConverter(node_count=114)
        res = conv.si_to_natural_energy(1.602176634e-19)
        self.assertAlmostEqual(res["energy_ev"], 1.0, places=4)
        
        wave_res = conv.frequency_to_wavelength_natural(432000000.0)
        self.assertGreater(wave_res["wavelength_m"], 0.0)
        self.assertEqual(wave_res["nodes"], 114)

    def test_grid_power_manager_nominal(self):
        mgr = GridPowerManager(max_bus_voltage_v=48.0, max_current_amps=50.0)
        res = mgr.evaluate_power_state({"bus_voltage_v": 24.0, "bus_current_amps": 10.0, "battery_temp_c": 35.0})
        self.assertEqual(res["status"], "NOMINAL")
        self.assertEqual(res["duty_cycle_limit"], 1.0)

    def test_grid_power_manager_thermal_throttle(self):
        mgr = GridPowerManager(max_bus_voltage_v=48.0, max_current_amps=50.0)
        res = mgr.evaluate_power_state({"bus_voltage_v": 24.0, "bus_current_amps": 10.0, "battery_temp_c": 70.0})
        self.assertEqual(res["status"], "THERMAL_THROTTLED")
        self.assertEqual(res["duty_cycle_limit"], 0.5)

if __name__ == "__main__":
    unittest.main()

