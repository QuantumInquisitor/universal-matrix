import json
import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class TeleoperationPacket(BaseModel):
    session_id: str
    operator_id: str
    target_hardware_node: str = "node_alpha_cnc"
    teleop_command_type: str = "POSITION_DELTA" # "POSITION_DELTA", "EMERGENCY_HALT", "PARAM_OVERRIDE"
    command_vector: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    timestamp_ns: int = Field(default_factory=time.time_ns)

class SpatialTeleoperationGateway:
    """
    Phase 43: Spatial digital twin telemetry and low-latency remote teleoperation gateway
    processing bi-directional 3D control packets for WebXR headsets and dashboards.
    """
    def process_teleop_command(self, packet: TeleoperationPacket) -> Dict[str, Any]:
        # Latency evaluation
        current_ns = time.time_ns()
        latency_ms = round((current_ns - packet.timestamp_ns) / 1e6, 3)

        execution_allowed = latency_ms < 250.0  # Safety threshold: 250 ms max teleop lag

        return {
            "status": "TELEOP_COMMAND_PROCESSED" if execution_allowed else "TELEOP_LATENCY_EXCEEDED",
            "session_id": packet.session_id,
            "target_node": packet.target_hardware_node,
            "roundtrip_latency_ms": max(0.001, latency_ms),
            "command_executed": execution_allowed,
            "spatial_vector_applied": packet.command_vector if execution_allowed else [0.0, 0.0, 0.0]
        }
