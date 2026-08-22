import unittest
from fastapi.testclient import TestClient
from src.api import app

class TestDashboardIntegration(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_endpoint_serves_html(self):
        """Verify GET / serves the WebGL dashboard HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Micro-to-Macro Reality Engine Dashboard", response.text)
        self.assertIn("loadEnergeticLattice", response.text)

if __name__ == "__main__":
    unittest.main()
