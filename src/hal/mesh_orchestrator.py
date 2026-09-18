from src.config import config

class EdgeMeshOrchestrator:
    def __init__(self):
        self.mode = "REAL_K8S" if config.USE_REAL_HARDWARE else "SIMULATED_MESH"
        self.nodes = {
            "node-alpha": {"status": "ONLINE", "capacity": 1.0, "active_tasks": 0},
            "node-beta": {"status": "ONLINE", "capacity": 0.8, "active_tasks": 0}
        }

    def dispatch_workload(self, workload_id: str, tensor_size: int) -> dict:
        # Find online node with lowest active task count
        available_nodes = [n for n, data in self.nodes.items() if data["status"] == "ONLINE"]
        if not available_nodes:
            return {"status": "FAILED", "reason": "NO_ONLINE_NODES_AVAILABLE"}

        selected_node = min(available_nodes, key=lambda n: self.nodes[n]["active_tasks"])
        self.nodes[selected_node]["active_tasks"] += 1

        return {
            "status": "WORKLOAD_DISPATCHED",
            "execution_mode": self.mode,
            "workload_id": workload_id,
            "assigned_node": selected_node,
            "tensor_size": tensor_size,
            "node_state": self.nodes[selected_node]
        }
