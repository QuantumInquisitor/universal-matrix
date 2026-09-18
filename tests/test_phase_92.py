import unittest
from src.hal.swarm_consensus import SwarmConsensusEngine

class TestPhase92Swarm(unittest.TestCase):
    def setUp(self):
        self.engine = SwarmConsensusEngine(total_agents=5)

    def test_swarm_consensus_quorum(self):
        res = self.engine.propose_trajectory_consensus([10.0, 5.0, 0.0], "agent-01")
        self.assertEqual(res["status"], "CONSENSUS_ACHIEVED")
        self.assertTrue(res["votes_received"] >= res["quorum_required"])
        self.assertEqual(res["synced_vector"], [10.0, 5.0, 0.0])

if __name__ == "__main__":
    unittest.main()
