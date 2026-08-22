import unittest
from src.vr_13d_integration import VR13DIntegrationEngine

class TestVREnergeticIntegration(unittest.TestCase):

    def setUp(self):
        self.vr_engine = VR13DIntegrationEngine(base_freq=432.0)

    def test_energetic_vr_mesh_generation(self):
        """Verify 13D to 3D VR spatial node projections for Chakras and Meridians."""
        mesh_data = self.vr_engine.generate_energetic_vr_mesh()
        self.assertEqual(mesh_data["node_count"], 19)
        self.assertEqual(len(mesh_data["vr_nodes"]), 19)
        
        # Verify first Chakra node positioning and scaling
        first_node = mesh_data["vr_nodes"][0]
        self.assertEqual(first_node["category"], "Chakra")
        self.assertEqual(len(first_node["position"]), 3)

if __name__ == "__main__":
    unittest.main()
