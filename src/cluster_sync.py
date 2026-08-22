import json
import asyncio
from typing import Dict, Any, Callable

class ClusterSyncManager:
    """
    Manages multi-instance state synchronization and Pub/Sub broadcasting
    for distributed 13D SO(13) reality engines via Redis/In-Memory fallback.
    """

    def __init__(self, channel_name: str = "reality:manifold:state"):
        self.channel_name = channel_name
        self.listeners = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Registers a callback for state update broadcasts."""
        self.listeners.append(callback)

    async def broadcast_state(self, payload: Dict[str, Any]):
        """Broadcasts manifold state updates to all registered cluster listeners."""
        for callback in self.listeners:
            if asyncio.iscoroutinefunction(callback):
                await callback(payload)
            else:
                callback(payload)
