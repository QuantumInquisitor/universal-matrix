import unittest
from src.acoustic_resonance_synthesizer import AcousticResonanceSynthesizer, AcousticFieldConfig

class TestAcousticResonanceSynthesizer(unittest.TestCase):
    def setUp(self):
        self.synthesizer = AcousticResonanceSynthesizer()

    def test_ultrasonic_phase_synthesis(self):
        config = AcousticFieldConfig(
            base_frequency_hz=40000.0,
            transducer_count=8,
            so13_phase_angle_rad=0.7854,
            triad_harmonic_index=9
        )
        res = self.synthesizer.synthesize_phase_delays(config)
        self.assertEqual(res["status"], "ACOUSTIC_PHASE_SYNTHESIZED")
        self.assertEqual(len(res["phase_delays_radians"]), 8)
        self.assertAlmostEqual(res["wavelength_meters"], 0.008575, places=5)

if __name__ == '__main__':
    unittest.main()
