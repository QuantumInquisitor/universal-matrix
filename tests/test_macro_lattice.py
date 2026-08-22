import unittest
import torch
from src.macro_lattice_mapper import MacroLatticeMapper

class TestMacroLatticeMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = MacroLatticeMapper(base_freq=432.0)

    def test_chakra_tensor_generation(self):
        """Verify 13D SO(13) vector shapes for primary chakra centers."""
        tensor = self.mapper.get_chakra_torus_tensor("Heart")
        self.assertEqual(tensor.shape, (13,))
        self.assertFalse(torch.isnan(tensor).any())

    def test_full_lattice_mapping(self):
        """Verify export of combined Energetic, Meridian, and Tissue nodes."""
        lattice = self.mapper.map_full_energetic_lattice()
        self.assertEqual(len(lattice), 19)  # 7 Chakras + 12 Meridians
        self.assertEqual(lattice[0]["category"], "Chakra")

if __name__ == "__main__":
    unittest.main()