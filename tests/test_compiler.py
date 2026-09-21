import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import calculator as mc
import canonical_kernel as ck
from gcode_compiler import GCodeCompiler


class TestCompiler(unittest.TestCase):
    def test_compiler_load(self):
        self.assertIsNotNone(mc.MatrixFieldEngine)

    def test_compiler_uses_canonical_architecture(self):
        compiler = GCodeCompiler()
        self.assertEqual(compiler.total_nodes, 114)
        self.assertEqual(compiler.core_nodes, 108)
        self.assertEqual(compiler.boundary_nodes, 6)
        self.assertEqual(compiler.infinity_step, 21)
        self.assertEqual(compiler.boundary_gate_ids, frozenset(range(108, 114)))

    def test_internal_routing_never_enters_external_gates(self):
        compiler = GCodeCompiler()
        sequence = []
        for phase_offset in range(3):
            current = phase_offset
            for _ in range(compiler.core_nodes // 3):
                sequence.append(current)
                current = (current + compiler.infinity_step) % compiler.core_nodes

        self.assertEqual(len(sequence), 108)
        self.assertEqual(set(sequence), set(range(108)))
        self.assertTrue(all(node not in compiler.boundary_gate_ids for node in sequence))

    def test_each_phase_is_a_36_state_cycle(self):
        compiler = GCodeCompiler()
        for phase in range(3):
            orbit = ck.routing_orbit(phase)
            self.assertEqual(len(orbit), 36)
            self.assertEqual(orbit[-1] + 0, ck.route(phase, 35))
            self.assertEqual(ck.route(orbit[-1]), phase)

    def test_register_projection_comes_from_kernel(self):
        for node in range(108):
            self.assertEqual(ck.register_address(node), (7 * node) % 64)


if __name__ == "__main__":
    unittest.main()
