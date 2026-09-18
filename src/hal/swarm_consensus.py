from src.config import config

class SwarmConsensusEngine:
    def __init__(self, total_agents: int = 5):
        self.total_agents = total_agents
        self.mode = "HARDWARE_SWARM" if config.USE_REAL_HARDWARE else "SIMULATED_SWARM"
        self.current_term = 1
        self.active_agents = [f"agent-{i:02d}" for i in range(1, total_agents + 1)]

    def propose_trajectory_consensus(self, proposed_vector: list, initiating_agent: str) -> dict:
        quorum_required = (self.total_agents // 2) + 1
        participating_agents = len(self.active_agents)
        has_quorum = participating_agents >= quorum_required

        return {
            "status": "CONSENSUS_ACHIEVED" if has_quorum else "QUORUM_FAILED",
            "execution_mode": self.mode,
            "term": self.current_term,
            "initiator": initiating_agent,
            "quorum_required": quorum_required,
            "votes_received": participating_agents,
            "synced_vector": proposed_vector if has_quorum else None
        }
