import unittest
from fastapi.testclient import TestClient
from src.api import app

class TestHUDIntegration(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_contains_resonance_hud(self):
        """Verify GET / serves the dashboard with the Toroidal Field HUD elements."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("TOROIDAL FIELD HUD", response.text)
        self.assertIn("fetchCoherence", response.text)
        self.assertIn("hudCoherence", response.text)

if __name__ == "__main__":
    unittest.main()
