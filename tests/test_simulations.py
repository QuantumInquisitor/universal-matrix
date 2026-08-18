import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from field_synthesizer import FieldSynthesizer
from lattice_quantum_engine import LatticeQuantumEngine
from light_cone_simulator import LightConeSimulator

class TestAdvancedSimulations(unittest.TestCase):
    def test_waveguide_synthesis_bounds(self):
        """Verification: Confirms waveguide synthesis frequencies map cleanly."""
        synth = FieldSynthesizer()
        res = synth.synthesize_waveguide(9, external_flux_voltage=2.0)
        self.assertIn("rf_synthesis", res)
        self.assertEqual(res["node_id"], 9)
        self.assertGreater(res["rf_synthesis"]["frequency_hz"], 0)

    def test_quantum_collapse_normalization(self):
        """Verification: Guarantees global probability distributions normalize to 1.0."""
        engine = LatticeQuantumEngine()
        engine.inject_multi_vector_flux([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        res = engine.execute_measurement_collapse()
        
        total_density = 0.0
        for node_key, node_data in res["full_lattice_density_matrix"].items():
            total_density += node_data["normalized_energy_density"]
            
        # Assert global energy probability maps strictly match 100% distribution mass
        self.assertAlmostEqual(total_density, 1.0, places=4)

    def test_chromatic_optical_lensing_refraction(self):
        """Verification: Assures short wave frequencies refract more than long ones."""
        tracer = LightConeSimulator()
        violet_ray = tracer.simulate_light_ray(entrance_angle_rad=0.5, wavelength_nm=405.0)
        green_ray = tracer.simulate_light_ray(entrance_angle_rad=0.5, wavelength_nm=532.0)
        
        # Shorter wave fields must scatter with a higher net geometric deflection delta
        self.assertGreater(
            abs(violet_ray["total_net_deflection_deg"]), 
            abs(green_ray["total_net_deflection_deg"])
        )

if __name__ == '__main__':
    unittest.main()
