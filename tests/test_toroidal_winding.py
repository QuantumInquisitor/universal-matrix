import unittest
from src.toroidal_winding_engine import ToroidalWindingEngine, WindingParameters

class TestToroidalWindingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ToroidalWindingEngine()

    def test_5axis_gcode_synthesis(self):
        params = WindingParameters(
            major_radius_mm=60.0,
            minor_radius_mm=20.0,
            total_turns=108,
            so13_tilt_deg=15.0
        )
        res = self.engine.generate_5axis_gcode(params)
        self.assertEqual(res["total_turns"], 108)
        self.assertGreater(res["generated_lines_count"], 100)
        self.assertIn("G1 X", res["full_gcode_stream"])
        self.assertIn("A", res["full_gcode_stream"])
        self.assertIn("C", res["full_gcode_stream"])

if __name__ == '__main__':
    unittest.main()
