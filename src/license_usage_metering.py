import time
import hashlib
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class UsageEventPayload(BaseModel):
    tenant_id: str
    hardware_resource: str = Field(..., description="e.g., SDR, CNC_WINDING, PEMF_PULSE, SO13_COMPUTE")
    operation_count: int = Field(1, ge=1)
    execution_duration_sec: float = Field(0.0, ge=0.0)

class LicenseUsageMeteringEngine:
    """
    Phase 44: Cryptographic usage metering and enterprise licensing engine
    tracking hardware machine-hours and compute operations for commercial billing.
    """
    def __init__(self):
        self._tenant_ledger: Dict[str, Dict[str, Any]] = {}

    def record_usage_event(self, payload: UsageEventPayload) -> Dict[str, Any]:
        tenant = payload.tenant_id
        if tenant not in self._tenant_ledger:
            self._tenant_ledger[tenant] = {
                "total_compute_ops": 0,
                "total_execution_sec": 0.0,
                "resource_breakdown": {}
            }

        ledger = self._tenant_ledger[tenant]
        ledger["total_compute_ops"] += payload.operation_count
        ledger["total_execution_sec"] += payload.execution_duration_sec

        res_type = payload.hardware_resource
        ledger["resource_breakdown"][res_type] = ledger["resource_breakdown"].get(res_type, 0) + payload.operation_count

        # Generate cryptographic proof hash for verifiable licensing audits
        raw_proof = f"{tenant}:{payload.hardware_resource}:{payload.operation_count}:{time.time_ns()}".encode('utf-8')
        usage_proof_hash = hashlib.sha256(raw_proof).hexdigest()

        return {
            "status": "USAGE_METERED",
            "tenant_id": tenant,
            "resource_metered": payload.hardware_resource,
            "accumulated_tenant_ops": ledger["total_compute_ops"],
            "accumulated_machine_hours": round(ledger["total_execution_sec"] / 3600.0, 6),
            "cryptographic_proof_hash": usage_proof_hash
        }

    def get_tenant_billing_summary(self, tenant_id: str) -> Dict[str, Any]:
        if tenant_id not in self._tenant_ledger:
            return {"tenant_id": tenant_id, "status": "NO_RECORDED_USAGE", "billable_amount_usd": 0.0}

        ledger = self._tenant_ledger[tenant_id]
        # Base commercial licensing rate model (.001 per operation, .00 per machine-hour)
        ops_cost = ledger["total_compute_ops"] * 0.001
        time_cost = (ledger["total_execution_sec"] / 3600.0) * 10.0
        total_billable_usd = round(ops_cost + time_cost, 2)

        return {
            "tenant_id": tenant_id,
            "total_compute_ops": ledger["total_compute_ops"],
            "total_machine_hours": round(ledger["total_execution_sec"] / 3600.0, 4),
            "resource_breakdown": ledger["resource_breakdown"],
            "total_billable_usd": total_billable_usd
        }
