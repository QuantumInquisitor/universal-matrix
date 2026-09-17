import unittest
from src.rl_field_optimizer import RLFieldOptimizer

class TestPhase53RLOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = RLFieldOptimizer(learning_rate=0.001)

    def test_optimization_converging(self):
        telemetry = {
            "current_pose_6dof": [0.0, 1.2, 0.5, 0.0, 45.0, 0.0],
            "field_intensity_feedback": 0.4,
            "target_intensity": 1.0
        }
        res = self.optimizer.optimize_field_trajectory(telemetry)
        self.assertEqual(res["status"], "CONVERGING")
        self.assertLess(res["reward_score"], 0.9)
        self.assertEqual(len(res["optimized_pose_6dof"]), 6)

    def test_optimization_optimal(self):
        telemetry = {
            "current_pose_6dof": [0.0, 1.2, 0.5, 0.0, 45.0, 0.0],
            "field_intensity_feedback": 0.98,
            "target_intensity": 1.0
        }
        res = self.optimizer.optimize_field_trajectory(telemetry)
        self.assertEqual(res["status"], "OPTIMAL")
        self.assertGreaterEqual(res["reward_score"], 0.9)

if __name__ == "__main__":
    unittest.main()

