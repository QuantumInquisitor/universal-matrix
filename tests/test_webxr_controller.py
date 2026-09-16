import unittest
from src.webxr_haptic_controller import WebXRHapticController, SpatialXRState, ControllerTransform

class TestWebXRHapticController(unittest.TestCase):
    def setUp(self):
        self.xr_controller = WebXRHapticController()

    def test_spatial_hand_tracking_and_haptics(self):
        state = SpatialXRState(
            left_hand=ControllerTransform(position_xyz=[-0.5, 0.0, 0.0]),
            right_hand=ControllerTransform(position_xyz=[0.5, 0.0, 0.0]),
            toroidal_coherence=0.40  # Below 0.65 threshold -> triggers haptics
        )
        res = self.xr_controller.process_xr_frame(state)
        self.assertAlmostEqual(res["hand_distance_meters"], 1.0)
        self.assertTrue(res["haptic_feedback"]["trigger_haptic"])
        self.assertGreater(res["haptic_feedback"]["intensity"], 0.0)

if __name__ == '__main__':
    unittest.main()
