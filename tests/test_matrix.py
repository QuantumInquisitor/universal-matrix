import sys
import os
import unittest

# Ensure the python path routes directly into the local library folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the functional standalone methods directly from the verified calculator script
import calculator as mc


class TestUniversalMatrix(unittest.TestCase):
    def test_system_equilibrium_gate(self):
        """Axiom I: Verifies that the core fields collapse natively to zero."""
        is_balanced, balance_value = mc.verify_axiom_1()
        
        # Ensure the boolean verification gate passes completely
        self.assertTrue(is_balanced, "Core matrix equilibrium check failed.")
        # Ensure the numerical offset resolves exactly to absolute zero
        self.assertEqual(balance_value, 0, f"Expected equilibrium offset 0, got {balance_value}")

    def test_boundary_symmetry_gate(self):
        """Axiom II/III: Verifies that the hypercube faces yield exactly 48 symmetries."""
        is_symmetric, density_value, tensor_array = mc.verify_axiom_2_and_3()
        
        # Ensure the symmetry condition gate passes completely
        self.assertTrue(is_symmetric, "Hypercube face Weyl symmetry check failed.")
        # Ensure the calculated density matches exactly the order-48 invariant threshold
        self.assertEqual(density_value, 48, f"Expected spatial density 48, got {density_value}")
        # Validate that the active sieve vector workspace contains exactly 6 entry junctions
        self.assertEqual(len(tensor_array), 6, "Boundary layout anomaly: Tensor array must hold exactly 6 junctions.")


if __name__ == '__main__':
    unittest.main()
