import sys
import os
import unittest

# Ensure the python path routes directly into the local library folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from calculator import UniversalMatrixEngine

class TestUniversalMatrix(unittest.TestCase):
    def test_system_equilibrium_gate(self):
        """Verifies that the core fields collapse natively to zero."""
        engine = UniversalMatrixEngine()
        self.assertEqual(engine.verify_vector_inversion_equilibrium(), 0)

    def test_boundary_symmetry_gate(self):
        """Verifies that the hypercube faces yield exactly 48 symmetries."""
        engine = UniversalMatrixEngine()
        _, density = engine.compute_hypercube_boundary_tensor()
        self.assertEqual(density, 48)
