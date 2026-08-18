import sys
import os
import unittest
import re

# Ensure the python path routes directly into the local library folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import calculator as mc
from gcode_compiler import GCodeCompiler


class TestGCodeCompiler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Runs once before testing to compile a fresh, uncorrupted G-Code file."""
        cls.compiler = GCodeCompiler()
        cls.output_file = cls.compiler.generate_toroidal_gcode("test_toroid_toolpath.gcode")

    @classmethod
    def tearDownClass(cls):
        """Cleans up the temporary test file after the suite concludes."""
        if os.path.exists(cls.output_file):
            os.remove(cls.output_file)

    def test_gcode_syntax_and_termination(self):
        """Verification: Confirms proper industrial initialization and termination codes."""
        with open(self.output_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        # Ensure critical baseline CNC commands are explicitly present
        self.assertIn("G21 ; Set system units to Millimeters", lines)
        self.assertIn("G90 ; Set machine instruction to Absolute Coordinates", lines)
        self.assertIn("M30             ; End of program loop sequence execution", lines)

    def test_complete_114_node_hardware_coverage(self):
        """Verification: Parses toolpath coordinates to guarantee 100% node coverage."""
        with open(self.output_file, "r", encoding="utf-8") as f:
            gcode_text = f.read()

        # Regular expression to extract target nodes logged inside code comments
        node_matches = re.findall(r"Move to Node (\d+)|External Face Gate \(Node (\d+)\)", gcode_text)
        
        # Flatten regex match tuples and extract integers cleanly
        visited_nodes = set()
        for match in node_matches:
            # Fixed: Safely extract whichever regex capture group caught the string item
            node_id = match[0] if match[0] else match[1]
            visited_nodes.add(int(node_id))

        # Re-include the starting origin point (Node 0)
        if "Material Origin: Node 0" in gcode_text:
            visited_nodes.add(0)

        # Assert that all 114 discrete mathematical positions were written
        total_unique_visited = len(visited_nodes)
        self.assertEqual(
            total_unique_visited, 
            mc.M_TOTAL, 
            f"Manufacturing Gap Detected: G-code toolpath only reached {total_unique_visited}/{mc.M_TOTAL} nodes!"
        )


if __name__ == '__main__':
    unittest.main()
