import unittest
from src.auth_gateway import HardwareAuthGateway, TenantCredentials

class TestHardwareAuthGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = HardwareAuthGateway()
        self.creds = TenantCredentials(
            tenant_id="enterprise_licensee_01",
            role="admin",
            hardware_access_keys=["SDR", "CNC"]
        )

    def test_token_generation_and_decoding(self):
        token = self.gateway.generate_token(self.creds)
        res = self.gateway.verify_token(token)
        self.assertTrue(res["valid"])
        self.assertEqual(res["payload"]["tenant_id"], "enterprise_licensee_01")

    def test_hardware_authorization(self):
        token = self.gateway.generate_token(self.creds)
        self.assertTrue(self.gateway.authorize_hardware_access(token, "SDR"))
        self.assertFalse(self.gateway.authorize_hardware_access(token, "SWARM"))

if __name__ == '__main__':
    unittest.main()
