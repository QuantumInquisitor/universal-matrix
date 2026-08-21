import os
import sys
import unittest
import numpy as np

# Bind the source path directory so scripts can locate cross-dependencies instantly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import calculator as mc
import matrix_constants as mat_const

class TestUniversalMatrixFramework(unittest.TestCase):
    def setUp(self):
        """Initializes the execution engine before running validation passes."""
        self.engine = mc.MatrixFieldEngine()

    def test_structural_constants_integrity(self):
        """Asserts that first-principles geometric partition rules hold perfect symmetry."""
        self.assertTrue(mat_const.verify_structural_integrity(), "Structural matrix invariants broken.")
        self.assertEqual(mat_const.TOTAL_NODES, 114)
        self.assertEqual(mat_const.INTERNAL_CORE_NODES, 108)

    def test_vortex_doubling_logic(self):
        """Validates that modular doubling arithmetic tracks exact circuit nodes cleanly."""
        # Test 2n mod 114 arithmetic constraints
        self.assertEqual(self.engine.execute_vortex_doubling_step(3), 6)
        self.assertEqual(self.engine.execute_vortex_doubling_step(57), 0)
        
        # Verify boundary safety checks throw proper exceptions
        with self.assertRaises(ValueError):
            self.engine.execute_vortex_doubling_step(115)

    def test_toroidal_coordinate_generation(self):
        """FIXES THE VR COLLAPSE BUG: Verifies spatial separation across 3D coordinates."""
        coords = self.engine.generate_3d_toroidal_coordinates()
        
        # Verify allocations match matrix coordinate constraints
        self.assertEqual(coords.shape, (114, 3))
        
        # Assert that adjacent nodes possess unique spatial locations (no overlapping zeros)
        distance = float(np.linalg.norm(coords[1] - coords[0]))
        self.assertGreater(distance, 0.1, "Spatial vector collapse detected! Nodes are overlapping in VR space.")

    def test_universal_loop_compression(self):
        """Asserts that the native scaling fraction evaluates cleanly without float drift."""
        expected_alpha = 1.0 / (54.0 * (np.pi ** 2))
        self.assertAlmostEqual(mat_const.ALPHA_GEOMETRIC, expected_alpha, places=9)

if __name__ == "__main__":
    unittest.main()
