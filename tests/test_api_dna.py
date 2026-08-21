import unittest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from src.api import app, SECRET_KEY, ALGORITHM

class TestAPIDNAMapping(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        # Generate valid test token using src.api configuration
        payload = {
            "sub": "operator",
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        }
        self.auth_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    def test_dna_map_endpoint_success(self):
        """Verify POST /api/v1/dna/map returns valid 13D tensor shapes and metrics."""
        payload = {"sequence": "ATGCGATCG"}
        response = self.client.post("/api/v1/dna/map", json=payload, headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["length"], 9)
        self.assertEqual(data["torus_target_layer"], 8)
        self.assertEqual(len(data["base_metrics"]), 9)

    def test_dna_map_endpoint_invalid_base(self):
        """Verify invalid nucleotide bases return 400 Bad Request."""
        payload = {"sequence": "ATGXGATCG"}  # 'X' is invalid
        response = self.client.post("/api/v1/dna/map", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()