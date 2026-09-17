import unittest
from src.license_usage_metering import LicenseUsageMeteringEngine, UsageEventPayload

class TestLicenseUsageMeteringEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LicenseUsageMeteringEngine()

    def test_record_usage_and_billing(self):
        payload1 = UsageEventPayload(
            tenant_id="enterprise_licensee_01",
            hardware_resource="CNC_WINDING",
            operation_count=100,
            execution_duration_sec=1800.0  # 0.5 hours
        )
        res1 = self.engine.record_usage_event(payload1)
        self.assertEqual(res1["status"], "USAGE_METERED")
        self.assertIsNotNone(res1["cryptographic_proof_hash"])

        summary = self.engine.get_tenant_billing_summary("enterprise_licensee_01")
        self.assertEqual(summary["total_compute_ops"], 100)
        self.assertEqual(summary["total_machine_hours"], 0.5)
        # Cost: 100 * 0.001 (.10) + 0.5 * .00 (.00) = .10
        self.assertEqual(summary["total_billable_usd"], 5.10)

if __name__ == '__main__':
    unittest.main()
