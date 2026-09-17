import unittest
from src.dao_governance import DAOGovernanceVoter

class TestPhase52DAOGovernance(unittest.TestCase):
    def setUp(self):
        self.voter = DAOGovernanceVoter(min_staking_power_wei=1000000)

    def test_vote_accepted(self):
        payload = {
            "proposal_id": "prop_001",
            "voter_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "vote_decision": "YES",
            "staking_power_wei": 5000000
        }
        res = self.voter.process_vote(payload)
        self.assertEqual(res["status"], "VOTE_ACCEPTED")
        self.assertTrue(res["is_valid"])
        self.assertIn("vote_hash", res)

    def test_vote_rejected_insufficient_stake(self):
        payload = {
            "proposal_id": "prop_001",
            "voter_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            "vote_decision": "YES",
            "staking_power_wei": 500
        }
        res = self.voter.process_vote(payload)
        self.assertEqual(res["status"], "REJECTED_INSUFFICIENT_STAKE")
        self.assertFalse(res["is_valid"])

if __name__ == "__main__":
    unittest.main()

