import unittest
import numpy as np
from src.run_field_simulation import HighDimensionalMatrixEngine

class TestAdvancedMatrixPhysics(unittest.TestCase):

    def setUp(self):
        self.engine = HighDimensionalMatrixEngine(num_nodes=114, dim=13)

    def test_so13_matrix_orthogonality(self):
        """Verify R * R^T = I under high-dimensional Givens transformations."""
        self.engine.compute_so13_givens_rotation(theta=0.1)
        product = np.dot(self.engine.state_matrix, self.engine.state_matrix.T)
        np.testing.assert_allclose(product, np.eye(13), atol=1e-6)

    def test_lightcone_raytracing_bounds(self):
        """Verify spatial-temporal lightcone interval projections."""
        intervals = self.engine.compute_lightcone_raytrace()
        self.assertEqual(len(intervals), 114)

    def test_non_unitary_decoherence_normalization(self):
        """Ensure quantum wavefunction collapse re-normalizes array sum to 1.0."""
        probs = self.engine.apply_quantum_decoherence(dampening_factor=0.95)
        self.assertAlmostEqual(float(np.sum(probs)), 1.0000, places=4)

if __name__ == "__main__":
    unittest.main()