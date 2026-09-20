from typing import Dict, Any, List
from pydantic import BaseModel, Field

class MarxArrayConfig(BaseModel):
    stage_count: int = Field(5, ge=1, le=20)
    charge_voltage_kv: float = Field(10.0, ge=0.5)
    gate_trigger_delay_ns: float = Field(12.5, ge=0.0)

class MarxGateArrayController:
    """
    Phase 48: High-power solid-state Marx generator gate timing controller generating
    nanosecond-precision pulse sequences.
    """
    def compute_gate_delays(self, config: MarxArrayConfig) -> Dict[str, Any]:
        total_output_kv = round(config.stage_count * config.charge_voltage_kv, 2)
        gate_delays_ns = [round(i * config.gate_trigger_delay_ns, 2) for i in range(config.stage_count)]

        return {
            "status": "MARX_ARRAY_SCHEDULED",
            "configured_stages": config.stage_count,
            "peak_erected_voltage_kv": total_output_kv,
            "gate_trigger_delays_ns": gate_delays_ns,
            "erection_time_ns": gate_delays_ns[-1] if gate_delays_ns else 0.0
        }
