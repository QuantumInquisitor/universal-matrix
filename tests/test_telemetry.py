import unittest
from fastapi.testclient import TestClient
from src.api import app

class TestTelemetry(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_metrics_endpoint(self):
        """Verify GET /metrics returns valid Prometheus exposition data."""
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("matrix_active_nodes_count", response.text)
        self.assertIn("matrix_api_requests_total", response.text)

if __name__ == "__main__":
    unittest.main()
