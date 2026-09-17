import hashlib
import time

class EVMContractBridge:
    def __init__(self, contract_address: str = "0x3540C6285a21D71960249F5734A29A6b2F6469C3", royalty_rate_pct: float = 2.5):
        self.contract_address = contract_address
        self.royalty_rate_pct = royalty_rate_pct

    def generate_royalty_proof_payload(self, execution_data: dict) -> dict:
        """
        Compiles execution proof metrics into an EVM transaction payload for smart contract royalty execution.
        """
        compute_units = execution_data.get("compute_units_used", 0)
        unit_price_wei = execution_data.get("unit_price_wei", 1000000000000) # Default 1000 Gwei
        licensee = execution_data.get("licensee_address", "0x0000000000000000000000000000000000000000")

        gross_fee_wei = compute_units * unit_price_wei
        royalty_fee_wei = int(gross_fee_wei * (self.royalty_rate_pct / 100.0))

        raw_payload = f"{licensee}:{self.contract_address}:{compute_units}:{royalty_fee_wei}:{time.time()}"
        tx_proof_hash = "0x" + hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        return {
            "status": "PROOF_GENERATED",
            "contract_address": self.contract_address,
            "licensee_address": licensee,
            "compute_units_used": compute_units,
            "gross_fee_wei": gross_fee_wei,
            "royalty_fee_wei": royalty_fee_wei,
            "tx_proof_hash": tx_proof_hash
        }

