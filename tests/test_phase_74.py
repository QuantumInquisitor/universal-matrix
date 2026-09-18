import unittest
from src.drivers.k8s_driver import KubernetesDriver

class TestPhase74KubernetesDriver(unittest.TestCase):
    def setUp(self):
        self.driver = KubernetesDriver()

    def test_driver_initialization(self):
        status = self.driver.get_status()
        self.assertEqual(status["driver"], "KubernetesDriver")
        self.assertIn(status["active_mode"], ["MOCK", "MOCK_FALLBACK", "REAL"])

    def test_pod_status_query(self):
        res = self.driver.get_cluster_pod_status("default")
        self.assertIn("status", res)
        self.assertIn("pod_count", res)

if __name__ == "__main__":
    unittest.main()

