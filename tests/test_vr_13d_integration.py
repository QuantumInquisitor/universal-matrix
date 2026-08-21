import unittest
import torch
from src.vr_13d_space import VR13DSpatialEngine

class TestVR13DSpatialIntegration(unittest.TestCase):

    def setUp(self):
        self.vr_engine = VR13DSpatialEngine(num_nodes=114, dim=13)

    def test_layer_transform_generation(self):
        """Verify layer transforms return valid gyroscopic tilts and RGB palettes."""
        transform = self.vr_engine.get_layer_spatial_transform(layer_idx=6) # ~Carbon Octave
        self.assertIn("gyroscopic_tilt_deg", transform)
        self.assertIn("resonant_frequency_hz", transform)
        self.assertEqual(len(transform["color_rgb"]), 3)

    def test_13d_to_3d_mesh_projection(self):
        """Verify 13D state tensors project into 114 node VR spatial coordinates."""
        dummy_state = torch.randn(114, 13, dtype=torch.float64)
        mesh_data = self.vr_engine.render_13d_to_vr_mesh(dummy_state)
        self.assertEqual(len(mesh_data), 114)
        self.assertEqual(len(mesh_data[0]["position"]), 3)

if __name__ == "__main__":
    unittest.main()