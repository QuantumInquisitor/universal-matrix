import time

class RAFTConsensusEngine:
    def __init__(self, node_id: str, cluster_nodes: list = None):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes or []
        self.current_term = 0
        self.voted_for = None
        self.role = "FOLLOWER"  # FOLLOWER, CANDIDATE, LEADER
        self.votes_received = set()

    def receive_heartbeat(self, leader_id: str, term: int) -> dict:
        if term >= self.current_term:
            self.current_term = term
            self.role = "FOLLOWER"
            self.voted_for = None
            return {"node_id": self.node_id, "term": self.current_term, "accepted": True}
        return {"node_id": self.node_id, "term": self.current_term, "accepted": False}

    def start_election(self) -> dict:
        self.current_term += 1
        self.role = "CANDIDATE"
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}

        # Calculate quorum requirement
        total_cluster_size = len(self.cluster_nodes) if self.cluster_nodes else 1
        quorum_required = (total_cluster_size // 2) + 1

        if len(self.votes_received) >= quorum_required:
            self.role = "LEADER"

        return {
            "node_id": self.node_id,
            "term": self.current_term,
            "role": self.role,
            "votes_count": len(self.votes_received),
            "quorum_required": quorum_required
        }

