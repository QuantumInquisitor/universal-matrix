import unittest
from src.hal.orchestrator import UniversalHALOrchestrator

class TestPhase81Orchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = UniversalHALOrchestrator()

    def test_system_wide_status(self):
        res = self.orchestrator.get_system_wide_status()
        self.assertEqual(res["total_registered_drivers"], 10)
        self.assertEqual(res["system_health"], "ALL_SYSTEMS_OPERATIONAL")
        self.assertIn("can", res["driver_statuses"])
        self.assertIn("spacex", res["driver_statuses"])

if __name__ == "__main__":
    unittest.main()

