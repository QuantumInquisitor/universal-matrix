import unittest
from src.vr_13d_space import VR13DSpatialEngine

class TestVRDNAIntegration(unittest.TestCase):

    def setUp(self):
        self.vr_engine = VR13DSpatialEngine(num_nodes=114, dim=13)

    def test_dna_double_helix_vr_mesh_generation(self):
        """Verify VR engine renders valid 3D double-helix mesh nodes for Layer 8."""
        seq = "ATGCGATCG"
        mesh_data = self.vr_engine.render_dna_sequence_mesh(seq)
        
        self.assertEqual(mesh_data["active_layer"], 8)
        self.assertEqual(mesh_data["sequence_length"], len(seq))
        self.assertEqual(len(mesh_data["mesh_nodes"]), len(seq))
        
        # Verify first node position and bond color attribution
        first_node = mesh_data["mesh_nodes"][0]
        self.assertEqual(len(first_node["position"]), 3)
        self.assertEqual(first_node["base"], "A")
        self.assertEqual(first_node["hydrogen_bonds"], 2)

if __name__ == "__main__":
    unittest.main()