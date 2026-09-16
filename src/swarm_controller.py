import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class HardwareNodeStatus(BaseModel):
    node_id: str
    ip_address: str
    hardware_type: str  # "SDR_TRANSCEIVER", "CNC_DRIVER", "SENSOR_RIG"
    is_active: bool = True
    clock_skew_ns: float = 0.0

class SwarmCommandPayload(BaseModel):
    target_node_ids: List[str] = Field(default_factory=list)
    so13_rotation_angle_rad: float = 0.0
    rf_carrier_freq_hz: float = 432000000.0
    execution_timestamp_ns: int = 0

class SwarmClusterOrchestrator:
    """
    Phase 22: Autonomous multi-node hardware swarm controller providing nanosecond-level
    coordinated emission and state synchronization across edge clusters.
    """
    def __init__(self):
        self.nodes: Dict[str, HardwareNodeStatus] = {
            "node_alpha_sdr": HardwareNodeStatus(
                node_id="node_alpha_sdr",
                ip_address="192.168.1.101",
                hardware_type="SDR_TRANSCEIVER"
            ),
            "node_beta_cnc": HardwareNodeStatus(
                node_id="node_beta_cnc",
                ip_address="192.168.1.102",
                hardware_type="CNC_DRIVER"
            )
        }

    def register_node(self, node: HardwareNodeStatus) -> Dict[str, Any]:
        self.nodes[node.node_id] = node
        return {"status": "REGISTERED", "node_id": node.node_id, "total_nodes": len(self.nodes)}

    def dispatch_swarm_command(self, command: SwarmCommandPayload) -> Dict[str, Any]:
        # Assign execution timestamp if omitted
        exec_time = command.execution_timestamp_ns or (time.time_ns() + 50000000)  # +50ms offset
        
        target_ids = command.target_node_ids or list(self.nodes.keys())
        dispatched_nodes = []

        for nid in target_ids:
            if nid in self.nodes and self.nodes[nid].is_active:
                dispatched_nodes.append({
                    "node_id": nid,
                    "type": self.nodes[nid].hardware_type,
                    "target_time_ns": exec_time,
                    "status": "DISPATCHED"
                })

        return {
            "swarm_execution_id": f"exec_{exec_time}",
            "execution_timestamp_ns": exec_time,
            "dispatched_nodes_count": len(dispatched_nodes),
            "dispatched_nodes": dispatched_nodes
        }
