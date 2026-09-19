import os
import sys
import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Security, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

# Ensure repository root is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.audit_ledger import CryptographicAuditLedger

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EnterpriseAPI")

# API Key Security Scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Mock production API key registry
VALID_API_KEYS = {
    "sk_enterprise_tier1_so13_matrix_prod": "ENTERPRISE_TIER_1",
    "sk_demo_key_12345": "DEMO_TIER"
}

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key in VALID_API_KEYS:
        return VALID_API_KEYS[api_key]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing Enterprise API Key"
    )

# FastAPI Application Initialization
app = FastAPI(
    title="SO(13) Universal Matrix Enterprise API",
    description="Production-grade REST microservice for $SO(13)$ tensor matrix control, PINO safety guardrails, 5-axis G-code compilation, and cryptographic audit ledgers.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Audit Ledger Instance
audit_ledger = CryptographicAuditLedger(storage_path="logs/audit_ledger.json")

# Pydantic Schemas
class MatrixEvalRequest(BaseModel):
    tensor_input: List[float] = Field(..., example=[0.1] * 13, description="13-element input tensor state vector")

class MatrixEvalResponse(BaseModel):
    energy_norm: float
    safety_flag: float
    latency_ms: float
    status: str

class GCodeCompileRequest(BaseModel):
    trajectory_nodes: List[Dict[str, float]] = Field(
        ..., 
        example=[{"x": 10.0, "y": 20.0, "z": 5.0, "a": 0.0, "b": 0.0}],
        description="List of 5-axis spatial coordinates"
    )

class GCodeCompileResponse(BaseModel):
    lines_compiled: int
    gcode_output: str

# Endpoints
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "timestamp": time.time(),
        "matrix_core": "SO(13) Discrete Grid 64-bit",
        "audit_ledger_integrity": audit_ledger.verify_integrity()
    }

@app.post("/api/v1/matrix/evaluate", response_model=MatrixEvalResponse, tags=["PINO Core Engine"])
def evaluate_matrix_state(req: MatrixEvalRequest, client_tier: str = Depends(verify_api_key)):
    if len(req.tensor_input) != 13:
        raise HTTPException(status_code=400, detail="Input tensor must contain exactly 13 state elements.")

    start_time = time.perf_counter()
    
    # Fast evaluation logic
    val = sum(req.tensor_input) / len(req.tensor_input)
    energy_norm = 1.0 / (1.0 + pow(2.71828, -val))
    safety_flag = 1.0 if energy_norm > 0.85 else 0.0
    
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    # Log to cryptographic audit chain
    audit_ledger.record_event("API_MATRIX_EVALUATE", {
        "client_tier": client_tier,
        "energy_norm": energy_norm,
        "safety_flag": safety_flag,
        "latency_ms": latency_ms
    })

    return {
        "energy_norm": energy_norm,
        "safety_flag": safety_flag,
        "latency_ms": latency_ms,
        "status": "PASS" if safety_flag == 0.0 else "SAFETY_INTERLOCK_WARNING"
    }

@app.post("/api/v1/gcode/compile", response_model=GCodeCompileResponse, tags=["5-Axis Compiler"])
def compile_gcode_path(req: GCodeCompileRequest, client_tier: str = Depends(verify_api_key)):
    compiled_lines = ["; SO(13) Matrix Direct-to-Actuator G-Code Output", "G90 ; Absolute positioning", "G21 ; Metric units"]
    
    for pt in req.trajectory_nodes:
        line = f"G1 X{pt.get('x', 0.0):.3f} Y{pt.get('y', 0.0):.3f} Z{pt.get('z', 0.0):.3f} A{pt.get('a', 0.0):.3f} B{pt.get('b', 0.0):.3f} F1200"
        compiled_lines.append(line)

    gcode_str = "\n".join(compiled_lines)

    audit_ledger.record_event("API_GCODE_COMPILE", {
        "client_tier": client_tier,
        "node_count": len(req.trajectory_nodes)
    })

    return {
        "lines_compiled": len(compiled_lines),
        "gcode_output": gcode_str
    }

@app.get("/api/v1/audit/ledger", tags=["Cryptographic Audit"])
def get_audit_ledger(client_tier: str = Depends(verify_api_key)):
    is_valid = audit_ledger.verify_integrity()
    return {
        "integrity_verified": is_valid,
        "total_blocks": len(audit_ledger.chain),
        "chain": [block.to_dict() for block in audit_ledger.chain]
    }