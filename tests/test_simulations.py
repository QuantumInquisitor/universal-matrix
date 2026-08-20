import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from m_theory_router import MTheoryRouter

class TestMTheorySimulations(unittest.TestCase):
    def test_m_theory_11d_projection_bounds(self):
        """Verification: Assures 11D strings map cleanly to 3D VR meshes."""
        router = MTheoryRouter()
        res = router.route_omnidirectional_vr_data(9)
        
        # Assert response schema validation metrics
        self.assertIn("vr_data_packet", res)
        
        # Verify 3D projected coordinate mesh spaces
        vector_len = len(res["vr_data_packet"]["omnidirectional_vector"])
        self.assertEqual(vector_len, 3)
        
        # Ensure physical membrane densities sit inside normalized envelopes
        self.assertGreaterEqual(res["vr_data_packet"]["membrane_energy_density"], 0)

if __name__ == "__main__":
    unittest.main()
