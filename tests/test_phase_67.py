import unittest
from src.spatial_viewport import SpatialViewportEngine

class TestPhase67SpatialViewport(unittest.TestCase):
    def setUp(self):
        self.engine = SpatialViewportEngine(1920, 1080)

    def test_pipeline_initialization(self):
        res = self.engine.initialize_webgpu_pipeline()
        self.assertEqual(res["status"], "WEBGPU_PIPELINE_READY")
        self.assertTrue(self.engine.is_webxr_active)

    def test_spatial_frame_rendering(self):
        pose = [1.0, 0.0, 0.5, 0.0, 0.0, 0.0]
        frame_res = self.engine.render_spatial_frame(frame_id=42, camera_pose=pose)
        self.assertEqual(frame_res["status"], "FRAME_RENDERED")
        self.assertEqual(frame_res["frame_id"], 42)
        self.assertEqual(frame_res["camera_pose"], pose)

if __name__ == "__main__":
    unittest.main()

