import unittest
from fastapi.testclient import TestClient
from src.api import app

class TestPhase65E2ELiveServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_live_health_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_live_agent_evaluate_endpoint(self):
        payload = {
            "nodes": [
                {"node_id": "live_edge_1", "region": "us-east", "latency_ms": 60.0, "status": "DEGRADED"}
            ]
        }
        response = self.client.post("/api/v1/agent/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "EVALUATION_COMPLETE")

    def test_live_sdk_info_endpoint(self):
        response = self.client.get("/api/v1/sdk/info")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "SDK_CATALOG_AVAILABLE")

if __name__ == "__main__":
    unittest.main()

