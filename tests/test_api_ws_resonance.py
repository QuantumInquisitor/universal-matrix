import unittest
import json
from fastapi.testclient import TestClient
from src.api import app

class TestResonanceWebSocket(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_websocket_resonance_stream(self):
        """Verify bi-directional streaming over /ws/resonance/stream."""
        with self.client.websocket_connect("/ws/resonance/stream") as websocket:
            data = websocket.receive_json()
            self.assertEqual(data["status"], "synchronized")
            self.assertIn("phase_coherence", data)
            self.assertIn("resonant_frequency_hz", data)

            # Send operator frequency modulation override
            websocket.send_text(json.dumps({"base_freq": 528.0}))
            data_updated = websocket.receive_json()
            self.assertIn("resonant_frequency_hz", data_updated)

if __name__ == "__main__":
    unittest.main()
