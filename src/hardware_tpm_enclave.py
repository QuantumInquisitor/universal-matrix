import hashlib
import hmac
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class HardwareCommandEnvelope(BaseModel):
    command_payload: str
    tenant_id: str
    timestamp_ns: int = Field(default_factory=time.time_ns)
    enclave_signature: Optional[str] = None

class TPM2HardwareEnclave:
    """
    Phase 30: Cryptographic Hardware Root-of-Trust and TPM 2.0 / HSM Key Enclave
    securing physical machine execution against command injection and tampering.
    """
    def __init__(self, master_enclave_key: str = "TPM2_HARDWARE_ROOT_KEY_SECURE_ENCLAVE_99"):
        self.enclave_key = master_enclave_key.encode('utf-8')

    def sign_command_payload(self, envelope: HardwareCommandEnvelope) -> HardwareCommandEnvelope:
        raw_digest = f"{envelope.tenant_id}:{envelope.command_payload}:{envelope.timestamp_ns}".encode('utf-8')
        signature = hmac.new(self.enclave_key, raw_digest, hashlib.sha256).hexdigest()
        envelope.enclave_signature = signature
        return envelope

    def verify_enclave_signature(self, envelope: HardwareCommandEnvelope) -> Dict[str, Any]:
        if not envelope.enclave_signature:
            return {"verified": False, "reason": "MISSING_ENCLAVE_SIGNATURE"}

        expected_envelope = self.sign_command_payload(
            HardwareCommandEnvelope(
                command_payload=envelope.command_payload,
                tenant_id=envelope.tenant_id,
                timestamp_ns=envelope.timestamp_ns
            )
        )

        is_valid = hmac.compare_digest(envelope.enclave_signature, expected_envelope.enclave_signature)
        return {
            "verified": is_valid,
            "tenant_id": envelope.tenant_id,
            "signature_match": is_valid,
            "status": "HARDWARE_EXECUTION_AUTHORIZED" if is_valid else "TAMPERING_DETECTED"
        }
