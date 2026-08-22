import unittest
import torch
from src.scalar_harmonics import ScalarHarmonicsSynthesizer

class TestScalarHarmonics(unittest.TestCase):

    def setUp(self):
        self.synthesizer = ScalarHarmonicsSynthesizer(base_freq=432.0)

    def test_compute_octave_scalar(self):
        """Verify harmonic octave scale calculation."""
        scale = self.synthesizer.compute_octave_scalar(864.0)  # Exactly 1 octave up
        self.assertAlmostEqual(scale, 1.0, places=4)

    def test_apply_scalar_transformation(self):
        """Verify 13D tensor shape integrity after scalar transformation."""
        vec = torch.ones(13, dtype=torch.float64)
        transformed = self.synthesizer.Apply_scalar_transformation(vec, scale_factor=0.5)
        self.assertEqual(transformed.shape, (13,))
        self.assertFalse(torch.isnan(transformed).any())

if __name__ == "__main__":
    unittest.main()
