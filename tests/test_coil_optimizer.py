import unittest
from src.coil_geometry_optimizer import CoilGeometryOptimizer, OptimizationTargetPayload

class TestCoilGeometryOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = CoilGeometryOptimizer()

    def test_optimization_convergence(self):
        payload = OptimizationTargetPayload(
            target_frequency_hz=432000000.0,
            max_major_radius_mm=80.0,
            max_turns=200,
            iterations=20
        )
        res = self.optimizer.optimize_geometry(payload)
        self.assertEqual(res["status"], "OPTIMIZATION_CONVERGED")
        self.assertEqual(res["iterations_evaluated"], 20)
        self.assertIn("optimal_major_radius_mm", res["optimal_topology"])
        self.assertGreater(res["optimal_topology"]["achieved_q_factor"], 0.0)

if __name__ == '__main__':
    unittest.main()
