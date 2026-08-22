import unittest
import torch
from src.toroidal_resonance_engine import ToroidalResonanceEngine

class TestToroidalResonanceEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ToroidalResonanceEngine(base_freq=432.0)

    def test_phase_coherence_identical_vectors(self):
        """Identical vectors should produce maximum phase coherence (1.0)."""
        vec_a = torch.ones(13, dtype=torch.float64)
        vec_b = torch.ones(13, dtype=torch.float64)
        score = self.engine.calculate_phase_coherence(vec_a, vec_b)
        self.assertAlmostEqual(score, 1.0, places=4)

    def test_phase_coherence_orthogonal_vectors(self):
        """Orthogonal vectors should produce neutral phase coherence (0.5)."""
        vec_a = torch.tensor([1.0] + [0.0]*12, dtype=torch.float64)
        vec_b = torch.tensor([0.0, 1.0] + [0.0]*11, dtype=torch.float64)
        score = self.engine.calculate_phase_coherence(vec_a, vec_b)
        self.assertAlmostEqual(score, 0.5, places=4)

    def test_compute_lattice_resonance_field(self):
        """Verify field synthesis metrics across multiple node tensors."""
        tensors = [torch.randn(13, dtype=torch.float64) for _ in range(5)]
        result = self.engine.compute_lattice_resonance_field(tensors)
        self.assertEqual(result["total_nodes"], 5)
        self.assertIn(result["field_stability"], ["Harmonic", "Turbulent"])

if __name__ == "__main__":
    unittest.main()
