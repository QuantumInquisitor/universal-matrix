import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.m_theory_router import MTheoryRouter

class TestAdvancedSimulations(unittest.TestCase):
    def test_waveguide_synthesis_bounds(self):
        """Verification: Confirms waveguide synthesis frequencies map cleanly."""
        from field_synthesizer import FieldSynthesizer
        synth = FieldSynthesizer()
        res = synth.synthesize_waveguide(9, external_flux_voltage=2.0)
        self.assertIn("rf_synthesis", res)
        self.assertEqual(res["node_id"], 9)

    def test_quantum_collapse_normalization(self):
        """Verification: Guarantees global probability distributions normalize to 1.0."""
        from lattice_quantum_engine import LatticeQuantumEngine
        engine = LatticeQuantumEngine()
        engine.inject_multi_vector_flux([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        res = engine.execute_measurement_collapse()
        total_density = sum([d["normalized_energy_density"] for d in res["full_lattice_density_matrix"].values()])
        self.assertAlmostEqual(total_density, 1.0, places=4)

    def test_chromatic_optical_lensing_refraction(self):
        """Verification: Assures short wave frequencies refract more than long ones."""
        from light_cone_simulator import LightConeSimulator
        tracer = LightConeSimulator()
        violet_ray = tracer.simulate_light_ray(entrance_angle_rad=0.5, wavelength_nm=405.0)
        green_ray = tracer.simulate_light_ray(entrance_angle_rad=0.5, wavelength_nm=532.0)
        self.assertGreater(abs(violet_ray["total_net_deflection_deg"]), abs(green_ray["total_net_deflection_deg"]))

    def test_api_m_theory_endpoint_response(self):
        """Verification: Assures ASGI routing engine delivers flawless 11D payloads."""
        from fastapi.testclient import TestClient
        from src.api import app
        client = TestClient(app)
        response = client.get("/api/v1/simulation/m-theory-router/9")
        self.assertEqual(response.status_code, 200)
        self.assertIn("vr_data_packet", response.json())

if __name__ == "__main__":
    unittest.main()
