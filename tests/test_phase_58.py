import unittest
from src.zero_trust_attestation import ZeroTrustAttestationEngine

class TestPhase58Attestation(unittest.TestCase):
    def setUp(self):
        self.engine = ZeroTrustAttestationEngine(expected_pcr_hash="0x8f3c7d1e0b2a4f6e8d0c1b3a5f7e9d2c")

    def test_attestation_success(self):
        quote = {
            "node_id": "edge_node_01",
            "pcr_quote_hash": "0x8f3c7d1e0b2a4f6e8d0c1b3a5f7e9d2c",
            "nonce": "session_nonce_99"
        }
        res = self.engine.verify_tpm_quote(quote)
        self.assertEqual(res["status"], "HARDWARE_TRUSTED")
        self.assertTrue(res["is_trusted"])
        self.assertIsNotNone(res["attestation_token"])

    def test_attestation_rejected(self):
        quote = {
            "node_id": "tampered_node_02",
            "pcr_quote_hash": "0xINVALIDHASH",
            "nonce": "session_nonce_99"
        }
        res = self.engine.verify_tpm_quote(quote)
        self.assertEqual(res["status"], "ATTESTATION_REJECTED")
        self.assertFalse(res["is_trusted"])

if __name__ == "__main__":
    unittest.main()

