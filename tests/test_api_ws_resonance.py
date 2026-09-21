import json
import unittest

import jwt
from fastapi.testclient import TestClient

from src.api import app
from src.security_config import JWT_ALGORITHM, JWT_SECRET


class TestResonanceWebSocket(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.token = jwt.encode(
            {"sub": "test-reader", "role": "read_only"},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )

    def test_websocket_resonance_stream(self):
        """Verify authenticated legacy visualization streaming."""
        with self.client.websocket_connect(
            f"/ws/resonance/stream?token={self.token}"
        ) as websocket:
            data = websocket.receive_json()
            self.assertEqual(data["status"], "synchronized")
            self.assertIn("phase_coherence", data)
            self.assertIn("resonant_frequency_hz", data)

            websocket.send_text(json.dumps({"base_freq": 528.0}))
            data_updated = websocket.receive_json()
            self.assertIn("resonant_frequency_hz", data_updated)


if __name__ == "__main__":
    unittest.main()
