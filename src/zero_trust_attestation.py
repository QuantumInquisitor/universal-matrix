import hashlib
import time

class ZeroTrustAttestationEngine:
    def __init__(self, expected_pcr_hash: str = "0x8f3c7d1e0b2a4f6e8d0c1b3a5f7e9d2c"):
        self.expected_pcr_hash = expected_pcr_hash.lower()

    def verify_tpm_quote(self, quote_data: dict) -> dict:
        """
        Verifies TPM 2.0 PCRQuote payload for platform integrity attestation.
        Expected quote_data format: {"node_id": str, "pcr_quote_hash": str, "nonce": str}
        """
        node_id = quote_data.get("node_id", "unknown_node")
        pcr_hash = quote_data.get("pcr_quote_hash", "").lower()
        nonce = quote_data.get("nonce", "")

        if not pcr_hash or not nonce:
            return {
                "status": "ATTESTATION_FAILED",
                "is_trusted": False,
                "reason": "Missing PCR hash or nonce."
            }

        is_trusted = (pcr_hash == self.expected_pcr_hash)
        status = "HARDWARE_TRUSTED" if is_trusted else "ATTESTATION_REJECTED"

        attestation_token = "0x" + hashlib.sha256(f"{node_id}:{pcr_hash}:{nonce}:{time.time()}".encode("utf-8")).hexdigest()

        return {
            "status": status,
            "is_trusted": is_trusted,
            "node_id": node_id,
            "attestation_token": attestation_token if is_trusted else None,
            "timestamp": time.time()
        }

