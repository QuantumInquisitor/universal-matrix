#!/usr/bin/env python3
"""
Automated Test Verification Pipeline: Universal Playing Field
Validates Axioms I through V and ensures the runtime logic of Axiom VI handles input variables.
"""

import unittest
import sys
import os

# Append current directory to ensure local import succeeds smoothly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculator as mc


class TestUniversalPlayingFieldAxioms(unittest.TestCase):

    def test_axiom_1_equilibrium(self):
        """Verify that the counter-rotating vector loops resolve to absolute zero balance."""
        success, balance_val = mc.verify_axiom_1()
        self.assertTrue(success, f"Axiom I Failed. Core balance must be 0, got {balance_val}")
        self.assertEqual(balance_val, 0)

    def test_axiom_2_and_3_weyl_symmetry(self):
        """Verify boundary density resolves precisely to order-48 Weyl group tracking."""
        success, density_val, tensor = mc.verify_axiom_2_and_3()
        self.assertTrue(success, f"Axiom II/III Failed. Boundary density must be 48, got {density_val}")
        self.assertEqual(density_val, 48)
        self.assertEqual(len(tensor), 6)

    def test_axiom_4_scale_factor(self):
        """Verify first-principles calibration resolves to the 1.629037e13 envelope scaling factor."""
        success, scale_val = mc.verify_axiom_4()
        self.assertTrue(success, f"Axiom IV Failed. Derived scale factor drifted: {scale_val}")

    def test_axiom_5_velocity_limit(self):
        """Verify that velocity ceiling returns exact integer speed of light constant (299,792,458 m/s)."""
        success, velocity_val = mc.verify_axiom_5()
        self.assertTrue(success, f"Axiom V Failed. Velocity ceiling was {velocity_val}")
        self.assertEqual(velocity_val, 299792458)

    def test_axiom_6_macro_flux_injection(self):
        """Verify Axiom VI mathematical processing with user-defined dynamic variables."""
        # Test baseline vacuum state (Psi = 0)
        d_stabilized_vacuum, ext_contrib_vacuum = mc.calculate_axiom_6(0.0)
        self.assertEqual(ext_contrib_vacuum, 0.0)
        self.assertEqual(d_stabilized_vacuum, 48.0)  # Core (0) + Boundary (48)

        # Test live atmospheric flux injection parameter (Psi = 13.5)
        d_stabilized_flux, ext_contrib_flux = mc.calculate_axiom_6(13.5)
        # Structural calculation verification: (13.5 * 6) / 9 = 81 / 9 = 9.0
        self.assertEqual(ext_contrib_flux, 9.0)
        self.assertEqual(d_stabilized_flux, 57.0)  # Core (0) + Boundary (48) + Macro-Flux (9)


if __name__ == '__main__':
    unittest.main()
