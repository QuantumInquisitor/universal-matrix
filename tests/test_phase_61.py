import unittest
from unittest.mock import MagicMock, patch

from sdk.python.universal_matrix_sdk import UniversalMatrixClient


class TestPhase61SDK(unittest.TestCase):
    def setUp(self):
        self.client = UniversalMatrixClient(base_url="http://127.0.0.1:8000")

    def tearDown(self):
        self.client.close()

    @patch("requests.Session.get")
    def test_get_health(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "ONLINE"}
        mock_get.return_value = mock_resp

        res = self.client.get_health()

        self.assertEqual(res["status"], "ONLINE")
        mock_resp.raise_for_status.assert_called_once_with()
        mock_get.assert_called_once_with(
            "http://127.0.0.1:8000/health",
            timeout=(3.0, 15.0),
        )

    @patch("requests.Session.post")
    def test_evaluate_agent(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "EVALUATION_COMPLETE"}
        mock_post.return_value = mock_resp

        nodes = [{"node_id": "test_node", "latency_ms": 10.0}]
        res = self.client.evaluate_agent(nodes)

        self.assertEqual(res["status"], "EVALUATION_COMPLETE")
        mock_resp.raise_for_status.assert_called_once_with()
        mock_post.assert_called_once_with(
            "http://127.0.0.1:8000/api/v1/agent/evaluate",
            json={"nodes": nodes},
            timeout=(3.0, 15.0),
        )


if __name__ == "__main__":
    unittest.main()
