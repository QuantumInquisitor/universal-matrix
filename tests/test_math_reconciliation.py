import unittest
import numpy as np
from src.calculator import UniversalMatrixCalculator

class TestMathReconciliation(unittest.TestCase):

    def setUp(self):
        self.calc = UniversalMatrixCalculator()

    def test_boundary_vector_modular_arithmetic(self):
        B_actual = self.calc.compute_boundary_vector()
        B_expected = [0, 9, 18, 9, 36, 45]
        self.assertEqual(B_actual, B_expected)
        self.assertEqual(sum(B_actual), 117)

    def test_axiom_1_evaluation(self):
        result = self.calc.verify_axiom_1()
        self.assertEqual(result, 0.0)

    def test_scale_factor_exact_derivation(self):
        expected_scale = 1.0411992492717533e11
        self.assertAlmostEqual(self.calc.SCALE_FACTOR / 1e11, expected_scale / 1e11, places=5)

    def test_speed_of_light_calibration(self):
        c_calc = self.calc.calculate_exact_speed_of_light()
        self.assertAlmostEqual(c_calc, 299792458.0, places=1)

if __name__ == "__main__":
    unittest.main()
