import hashlib
import time

class DAOGovernanceVoter:
    def __init__(self, min_staking_power_wei: int = 1000000):
        self.min_staking_power_wei = min_staking_power_wei

    def process_vote(self, vote_data: dict) -> dict:
        proposal_id = vote_data.get("proposal_id", "")
        voter_address = vote_data.get("voter_address", "")
        vote_decision = vote_data.get("vote_decision", "ABSTAIN").upper()
        staking_power = vote_data.get("staking_power_wei", 0)

        if staking_power < self.min_staking_power_wei:
            return {
                "status": "REJECTED_INSUFFICIENT_STAKE",
                "is_valid": False,
                "staking_power_wei": staking_power,
                "min_required_wei": self.min_staking_power_wei
            }

        payload_str = f"{proposal_id}:{voter_address}:{vote_decision}:{staking_power}:{time.time()}"
        vote_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        return {
            "status": "VOTE_ACCEPTED",
            "is_valid": True,
            "proposal_id": proposal_id,
            "voter_address": voter_address,
            "vote_decision": vote_decision,
            "weight": staking_power,
            "vote_hash": vote_hash
        }

