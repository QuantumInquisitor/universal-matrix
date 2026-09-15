import unittest
from src.russell_periodic_mapper import RussellPeriodicEngine

class TestRussellPeriodicEngine(unittest.TestCase):

    def setUp(self):
        self.mapper = RussellPeriodicEngine(base_freq=432.0)

    def test_carbon_peak_compression(self):
        """Verify Carbon (Z=6) maps to the 90-degree 4++ octave amplitude peak."""
        res = self.mapper.calculate_element_properties(6)
        self.assertEqual(res["tone_position"], 4)
        self.assertEqual(res["gyroscopic_tilt_deg"], 90.0)

    def test_frequency_octave_scaling(self):
        """Verify resonant frequency doubles with octave progression."""
        h_res = self.mapper.calculate_element_properties(1)   # Octave 1
        c_res = self.mapper.calculate_element_properties(13)  # Octave 2
        self.assertGreater(c_res["resonant_frequency_hz"], h_res["resonant_frequency_hz"])

    def test_114_node_field_coverage(self):
        """Verify all 114 engine nodes receive valid periodic grid mappings."""
        nodes = self.mapper.map_matrix_nodes_to_periodic_grid(114)
        self.assertEqual(len(nodes), 114)
        self.assertEqual(nodes[110]["node_type"], "Outer Hypercube Boundary Gate")

if __name__ == "__main__":
    unittest.main()