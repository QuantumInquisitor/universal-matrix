import unittest
from src.hardware_tpm_enclave import TPM2HardwareEnclave, HardwareCommandEnvelope

class TestTPM2HardwareEnclave(unittest.TestCase):
    def setUp(self):
        self.enclave = TPM2HardwareEnclave()

    def test_enclave_signing_and_verification(self):
        envelope = HardwareCommandEnvelope(
            command_payload="G1 X10 Y10 Z0 A15 C30",
            tenant_id="enterprise_licensee_01"
        )
        signed_env = self.enclave.sign_command_payload(envelope)
        self.assertIsNotNone(signed_env.enclave_signature)

        verification = self.enclave.verify_enclave_signature(signed_env)
        self.assertTrue(verification["verified"])
        self.assertEqual(verification["status"], "HARDWARE_EXECUTION_AUTHORIZED")

    def test_tamper_detection(self):
        envelope = HardwareCommandEnvelope(
            command_payload="G1 X10 Y10 Z0 A15 C30",
            tenant_id="enterprise_licensee_01"
        )
        signed_env = self.enclave.sign_command_payload(envelope)
        
        # Modify payload after signing to simulate tampering
        signed_env.command_payload = "G1 X100 Y100 Z10 A15 C30"
        verification = self.enclave.verify_enclave_signature(signed_env)
        self.assertFalse(verification["verified"])
        self.assertEqual(verification["status"], "TAMPERING_DETECTED")

if __name__ == '__main__':
    unittest.main()
