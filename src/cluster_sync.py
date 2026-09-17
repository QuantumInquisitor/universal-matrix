import time
import json
import asyncio

class ClusterSyncManager:
    def __init__(self, channel_name: str = "matrix_cluster_sync_channel"):
        self.channel_name = channel_name
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    async def broadcast_state(self, state_data: dict):
        for sub in self.subscribers:
            if asyncio.iscoroutinefunction(sub):
                await sub(state_data)
            else:
                sub(state_data)
        return state_data

    def broadcast(self, state_data: dict):
        for sub in self.subscribers:
            sub(state_data)
        return state_data

    def format_sync_payload(self, state_data: dict) -> str:
        payload = {
            "channel": self.channel_name,
            "timestamp": time.time(),
            "data": state_data
        }
        return json.dumps(payload)

class ClusterHealthEvaluator:
    def __init__(self, max_latency_ms: float = 200.0, minimum_quorum_ratio: float = 0.5):
        self.max_latency_ms = max_latency_ms
        self.minimum_quorum_ratio = minimum_quorum_ratio

    def evaluate_cluster_health(self, nodes: list) -> dict:
        if not nodes:
            return {
                "status": "NO_NODES",
                "quorum_reached": False,
                "healthy_nodes": 0,
                "total_nodes": 0,
                "quorum_ratio": 0.0
            }

        healthy_nodes = 0
        total_nodes = len(nodes)

        for node in nodes:
            is_alive = node.get("is_alive", False)
            latency = node.get("heartbeat_latency_ms", 9999.0)
            
            if is_alive and latency <= self.max_latency_ms:
                healthy_nodes += 1

        quorum_ratio = healthy_nodes / total_nodes
        quorum_reached = quorum_ratio >= self.minimum_quorum_ratio

        status = "HEALTHY" if quorum_reached else "DEGRADED_FAILOVER_REQUIRED"

        return {
            "status": status,
            "quorum_reached": quorum_reached,
            "healthy_nodes": healthy_nodes,
            "total_nodes": total_nodes,
            "quorum_ratio": quorum_ratio,
            "timestamp": time.time()
        }

