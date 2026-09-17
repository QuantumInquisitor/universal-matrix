import unittest
from src.raft_consensus_engine import RAFTConsensusEngine

class TestPhase55RAFTConsensus(unittest.TestCase):
    def setUp(self):
        self.engine = RAFTConsensusEngine(node_id="node_1", cluster_nodes=["node_1", "node_2", "node_3"])

    def test_start_election(self):
        res = self.engine.start_election()
        self.assertEqual(res["term"], 1)
        self.assertEqual(res["role"], "CANDIDATE")
        self.assertEqual(res["quorum_required"], 2)

    def test_receive_heartbeat(self):
        res = self.engine.receive_heartbeat(leader_id="node_2", term=2)
        self.assertTrue(res["accepted"])
        self.assertEqual(self.engine.current_term, 2)
        self.assertEqual(self.engine.role, "FOLLOWER")

if __name__ == "__main__":
    unittest.main()

