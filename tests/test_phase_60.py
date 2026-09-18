import unittest
from src.autonomous_agent import AutonomousAgentLayer

class TestPhase60AutonomousAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AutonomousAgentLayer(latency_threshold_ms=50.0)

    def test_agent_nominal_cluster(self):
        nodes = [
            {"node_id": "node_1", "region": "us-east", "latency_ms": 20.0, "status": "HEALTHY"},
            {"node_id": "node_2", "region": "us-west", "latency_ms": 25.0, "status": "HEALTHY"}
        ]
        res = self.agent.evaluate_and_remediate(nodes)
        self.assertEqual(res["status"], "EVALUATION_COMPLETE")
        self.assertEqual(res["remediation_count"], 0)

    def test_agent_high_latency_remediation(self):
        nodes = [
            {"node_id": "node_1", "region": "us-east", "latency_ms": 80.0, "status": "HEALTHY"},
            {"node_id": "node_2", "region": "us-west", "latency_ms": 90.0, "status": "HEALTHY"}
        ]
        res = self.agent.evaluate_and_remediate(nodes)
        self.assertEqual(res["remediation_count"], 1)
        self.assertEqual(res["actions_triggered"][0]["action"], "RL_FIELD_OPTIMIZATION")

    def test_agent_degraded_node_remediation(self):
        nodes = [
            {"node_id": "node_1", "region": "us-east", "latency_ms": 10.0, "status": "DEGRADED"}
        ]
        res = self.agent.evaluate_and_remediate(nodes)
        self.assertEqual(res["remediation_count"], 1)
        self.assertEqual(res["actions_triggered"][0]["action"], "FPGA_BITSTREAM_RESYNTHESIS")

if __name__ == "__main__":
    unittest.main()

