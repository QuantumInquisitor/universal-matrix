import unittest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from src.api import app, SECRET_KEY, ALGORITHM

class TestAPICoherence(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        payload = {
            "sub": "operator",
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        }
        self.auth_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    def test_coherence_endpoint_success(self):
        """Verify GET /api/v1/resonance/coherence returns valid resonance data."""
        response = self.client.get("/api/v1/resonance/coherence", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("mean_coherence", data["resonance"])

if __name__ == "__main__":
    unittest.main()
