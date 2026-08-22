import unittest
import asyncio
from src.cluster_sync import ClusterSyncManager

class TestClusterSync(unittest.TestCase):

    def setUp(self):
        self.sync_manager = ClusterSyncManager()

    def test_broadcast_and_subscribe(self):
        """Verify state payload delivery across cluster listeners."""
        received_data = []

        async def mock_callback(payload):
            received_data.append(payload)

        self.sync_manager.subscribe(mock_callback)
        
        test_payload = {"node_id": "cluster-1", "frequency": 432.0, "coherence": 0.98}
        asyncio.run(self.sync_manager.broadcast_state(test_payload))

        self.assertEqual(len(received_data), 1)
        self.assertEqual(received_data[0]["frequency"], 432.0)

if __name__ == "__main__":
    unittest.main()
