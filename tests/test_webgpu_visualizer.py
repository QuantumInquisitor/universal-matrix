import unittest
from src.webgpu_spatial_visualizer import WebGPUSpatialVisualizer, SpatialViewportPayload

class TestWebGPUSpatialVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = WebGPUSpatialVisualizer()

    def test_wgsl_pipeline_compilation(self):
        payload = SpatialViewportPayload(
            viewport_resolution_wh=[2560, 1440],
            field_coherence_index=0.92,
            ar_passthrough_enabled=True
        )
        res = self.visualizer.generate_wgsl_pipeline(payload)
        self.assertEqual(res["status"], "WEBGPU_PIPELINE_COMPILED")
        self.assertTrue(res["ar_passthrough_active"])
        self.assertIn("@compute", res["wgsl_code_snippet"])
        self.assertIn("v_flux_buffer", res["wgsl_code_snippet"])

if __name__ == '__main__':
    unittest.main()
