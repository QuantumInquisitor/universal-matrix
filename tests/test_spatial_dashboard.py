import unittest
from fastapi.testclient import TestClient
from src.api import app

class TestSpatialDashboard(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_spatial_dashboard_endpoint(self):
        """Verify GET / returns valid spatial viewport HTML content."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("<html" in response.text.lower())
        self.assertTrue("hud" in response.text.lower())

if __name__ == "__main__":
    unittest.main()
