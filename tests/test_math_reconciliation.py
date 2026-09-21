import unittest
import numpy as np
from src.calculator import UniversalMatrixCalculator, N_CORE, B_BOUNDARY, M_TOTAL

class TestMathReconciliation(unittest.TestCase):

    def setUp(self):
        self.calc = UniversalMatrixCalculator()

    def test_canonical_architecture_aliases(self):
        self.assertEqual(N_CORE, 108)
        self.assertEqual(B_BOUNDARY, 6)
        self.assertEqual(M_TOTAL, 114)

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

    def test_speed_of_light_formula_is_explicitly_calibrated(self):
        calibrated = self.calc.calculate_calibrated_speed_of_light()
        legacy_alias = self.calc.calculate_exact_speed_of_light()
        self.assertAlmostEqual(calibrated, 299792458.0, places=1)
        self.assertEqual(legacy_alias, calibrated)

    def test_coordinate_generator_is_identified_as_helix(self):
        core = self.calc.generate_3d_helical_coordinates()
        legacy = self.calc.generate_3d_toroidal_coordinates()
        self.assertEqual(core.shape, (108, 3))
        self.assertEqual(legacy.shape, (114, 3))
        self.assertTrue(np.all(np.diff(core[:, 2]) > 0))

if __name__ == "__main__":
    unittest.main()
