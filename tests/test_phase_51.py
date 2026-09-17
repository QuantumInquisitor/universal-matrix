import unittest
from src.cluster_sync import ClusterHealthEvaluator

class TestPhase51ClusterHealth(unittest.TestCase):
    def setUp(self):
        self.evaluator = ClusterHealthEvaluator(max_latency_ms=200.0, minimum_quorum_ratio=0.5)

    def test_cluster_healthy_quorum(self):
        nodes = [
            {"node_id": "node_1", "is_alive": True, "heartbeat_latency_ms": 15.0},
            {"node_id": "node_2", "is_alive": True, "heartbeat_latency_ms": 45.0},
            {"node_id": "node_3", "is_alive": False, "heartbeat_latency_ms": 999.0}
        ]
        res = self.evaluator.evaluate_cluster_health(nodes)
        self.assertEqual(res["status"], "HEALTHY")
        self.assertTrue(res["quorum_reached"])
        self.assertEqual(res["healthy_nodes"], 2)

    def test_cluster_degraded_quorum(self):
        nodes = [
            {"node_id": "node_1", "is_alive": False, "heartbeat_latency_ms": 999.0},
            {"node_id": "node_2", "is_alive": True, "heartbeat_latency_ms": 350.0}
        ]
        res = self.evaluator.evaluate_cluster_health(nodes)
        self.assertEqual(res["status"], "DEGRADED_FAILOVER_REQUIRED")
        self.assertFalse(res["quorum_reached"])
        self.assertEqual(res["healthy_nodes"], 0)

if __name__ == "__main__":
    unittest.main()

