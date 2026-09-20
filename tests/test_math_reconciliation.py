import unittest
import numpy as np

class TestMathReconciliation(unittest.TestCase):

    def test_boundary_vector_modular_arithmetic(self):
        S_down = 987654321
        moduli = [9, 18, 27, 36, 45, 54]
        B_actual = [S_down % m for m in moduli]
        B_expected = [0, 9, 18, 9, 36, 45]
        self.assertEqual(B_actual, B_expected)
        self.assertEqual(sum(B_actual), 117)

    def test_axiom_1_evaluation(self):
        S_up = 123456789
        S_down = 987654321
        delta_S = S_down - S_up
        
        term1 = sum([-(S_down % n) + (S_up % n) for n in range(1, 55)])
        term2 = delta_S % 31
        
        result = term1 - term2 + 18
        self.assertEqual(result, 0)

    def test_scale_factor_exact_derivation(self):
        # ScaleFactor = (2^64 / (114 * 9 * 324)) / (54 * pi^2)
        val = (2**64 / (114 * 9 * 324)) / (54 * (np.pi**2))
        expected_scale = 5.0278923398796e12
        self.assertAlmostEqual(val / 1e12, expected_scale / 1e12, places=5)

if __name__ == "__main__":
    unittest.main()
