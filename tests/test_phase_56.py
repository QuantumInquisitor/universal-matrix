import unittest
from src.evm_contract_bridge import EVMContractBridge

class TestPhase56EVMBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = EVMContractBridge(royalty_rate_pct=2.5)

    def test_royalty_proof_generation(self):
        execution_data = {
            "licensee_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "compute_units_used": 1000,
            "unit_price_wei": 1000000000
        }
        res = self.bridge.generate_royalty_proof_payload(execution_data)
        self.assertEqual(res["status"], "PROOF_GENERATED")
        self.assertEqual(res["gross_fee_wei"], 1000000000000)
        self.assertEqual(res["royalty_fee_wei"], 25000000000)
        self.assertTrue(res["tx_proof_hash"].startswith("0x"))

if __name__ == "__main__":
    unittest.main()

