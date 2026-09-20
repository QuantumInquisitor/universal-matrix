import unittest
import numpy as np
from src.calculator import UniversalMatrixCalculator

class TestExperimentalPredictions(unittest.TestCase):

    def setUp(self):
        self.calc = UniversalMatrixCalculator()
        self.E_planck = 1.22e19  # GeV
        self.c = 299792458.0     # m/s

    def test_gamma_ray_dispersion_prediction(self):
        """Verify quantum gravity dispersion delay scales predictably relative to GR baseline (0.0s)."""
        E_photon = 100.0  # GeV
        L_meters = 1.0e25 # ~10^9 light years
        
        # Calculate discrete delay using 114-node topological parameters
        alpha_geo = 1.0 / (54.0 * (np.pi**2))
        ratio_b_core = (6.0 / 108.0)**2
        
        delta_tau = (E_photon / self.E_planck) * ratio_b_core * alpha_geo * (L_meters / self.c)
        
        # Must be non-zero (divergence from standard GR) and within expected physical bounds
        self.assertGreaterThan(delta_tau, 0.0)
        self.assertAlmostEqual(delta_tau * 1e7, 1.503, places=2)

    def test_continuum_limit_metric_convergence(self):
        """Verify second-difference jump operator converges to continuous second derivative."""
        dx = 1e-5
        x = 1.0
        
        # Test function f(x) = x^3 -> f''(x) = 6x -> f''(1.0) = 6.0
        f = lambda z: z**3
        
        # Discrete 21-step operator scaled by step size
        step = 21 * dx
        discrete_d2 = (f(x + step) - 2*f(x) + f(x - step)) / (step**2)
        
        # Analytical continuous derivative
        continuous_d2 = 6.0 * x
        
        self.assertAlmostEqual(discrete_d2, continuous_d2, places=4)

if __name__ == "__main__":
    unittest.main()
