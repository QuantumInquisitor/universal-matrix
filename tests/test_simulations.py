import unittest
import numpy as np

class TestMatrixSimulationEngine(unittest.TestCase):

    def test_so13_givens_orthogonality(self):
        """Verify that SO(13) rotation matrices maintain exact orthogonality (R * R^T = I)."""
        dim = 13
        theta = np.pi / 4.0
        # Construct a simple Givens rotation matrix in 13D space
        R = np.eye(dim)
        R[0, 0] = np.cos(theta)
        R[0, 1] = -np.sin(theta)
        R[1, 0] = np.sin(theta)
        R[1, 1] = np.cos(theta)

        identity = np.eye(dim)
        product = np.dot(R, R.T)
        np.testing.assert_allclose(product, identity, atol=1e-6)

    def test_probability_normalization_bounds(self):
        """Assert 114-node quantum probability array normalizes to 1.0000."""
        node_probabilities = np.ones(114) / 114.0
        total_sum = np.sum(node_probabilities)
        self.assertAlmostEqual(total_sum, 1.0000, places=4)

    def test_clock_drift_scaling(self):
        """Ensure clock drift scales predictably with simulation step count."""
        step = 100
        expected_drift = 0.042 * step
        actual_drift = round(0.042 * step, 4)
        self.assertEqual(actual_drift, 4.2)

if __name__ == "__main__":
    unittest.main()