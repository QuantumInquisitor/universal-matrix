import unittest
from src.sdr_rf_synthesizer import SDRRFSynthesizer, RFSignalConfig

class TestSDRRFSynthesizer(unittest.TestCase):
    def setUp(self):
        self.config = RFSignalConfig(center_freq_hz=432000000.0, tx_gain_db=10.0)
        self.synthesizer = SDRRFSynthesizer(config=self.config, mock_mode=True)

    def test_iq_sample_generation(self):
        iq_samples = self.synthesizer.generate_iq_samples(num_samples=256)
        self.assertEqual(len(iq_samples), 256)
        self.assertIn("i", iq_samples[0])
        self.assertIn("q", iq_samples[0])

    def test_transmission_burst(self):
        result = self.synthesizer.transmit_carrier_burst(num_samples=512)
        self.assertEqual(result["status"], "TRANSMITTED_MOCK")
        self.assertEqual(result["samples_count"], 512)

if __name__ == '__main__':
    unittest.main()
