import unittest
import torch
from src.dna_bio_mapper import DNABioMapper

class TestDNABioMapper(unittest.TestCase):

    def setUp(self):
        self.bio_mapper = DNABioMapper(base_freq=432.0)

    def test_nucleotide_frequency_mapping(self):
        """Verify Adenine (A) returns valid weighted harmonic frequency and bonds."""
        res = self.bio_mapper.map_base_to_frequency('A')
        self.assertEqual(res["base"], "A")
        self.assertEqual(res["hydrogen_bonds"], 2)
        self.assertGreater(res["weighted_frequency_hz"], 400.0)

    def test_sequence_to_13d_tensor_shape(self):
        """Verify DNA sequence converts cleanly to [N, 13] SO(13) state tensor."""
        seq = "ATGCGATCG"
        tensor = self.bio_mapper.sequence_to_13d_tensor(seq)
        self.assertEqual(tensor.shape[0], len(seq))
        self.assertEqual(tensor.shape[1], 13)

if __name__ == "__main__":
    unittest.main()