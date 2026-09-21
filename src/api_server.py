from __future__ import annotations

import logging
import math
import os
import secrets
import time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field

from src.audit_ledger import CryptographicAuditLedger
from src import canonical_kernel as ck

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("UniversalMatrixAPI")

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def _load_api_keys() -> dict[str, str]:
    """Load API keys from UNIVERSAL_MATRIX_API_KEYS.

    Format:
        key1:tier1,key2:tier2

    No built-in production or demo credentials are shipped in source.
    """
    raw = os.getenv("UNIVERSAL_MATRIX_API_KEYS", "").strip()
    result: dict[str, str] = {}
    if not raw:
        return result
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            raise RuntimeError(
                "UNIVERSAL_MATRIX_API_KEYS entries must use key:tier format"
            )
        key, tier = item.split(":", 1)
        key, tier = key.strip(), tier.strip()
        if not key or not tier:
            raise RuntimeError("API key and tier must both be non-empty")
        result[key] = tier
    return result


def _load_cors_origins() -> list[str]:
    raw = os.getenv("UNIVERSAL_MATRIX_CORS_ORIGINS", "").strip()
    if not raw:
        return []
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


VALID_API_KEYS = _load_api_keys()
CORS_ORIGINS = _load_cors_origins()


def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    for configured_key, tier in VALID_API_KEYS.items():
        if secrets.compare_digest(api_key, configured_key):
            return tier
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


app = FastAPI(
    title="Universal Matrix Experimental API",
    description=(
        "API for the canonical finite kernel, experimental gauge extensions, "
        "G-code tooling, and audit utilities. Experimental physics adapters are "
        "not presented as validated physical laws."
    ),
    version="0.4.0",
)

if CORS_ORIGINS:
    if "*" in CORS_ORIGINS:
        raise RuntimeError(
            "Wildcard CORS is not permitted when API credentials are in use"
        )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=[API_KEY_NAME, "Content-Type"],
    )

audit_ledger = CryptographicAuditLedger(
    storage_path=os.getenv(
        "UNIVERSAL_MATRIX_AUDIT_LEDGER",
        "logs/audit_ledger.json",
    )
)


API_REQUESTS = Counter(
    "universal_matrix_api_requests_total",
    "Research API requests by endpoint and outcome.",
    ["endpoint", "outcome"],
)
API_LATENCY = Histogram(
    "universal_matrix_api_latency_seconds",
    "Research API handler latency.",
    ["endpoint"],
)


class MatrixEvalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tensor_input: list[float] = Field(
        ...,
        min_length=1,
        max_length=4096,
        json_schema_extra={"example": [0.1] * 13},
        description="Experimental numeric state vector.",
    )


class MatrixEvalResponse(BaseModel):
    energy_norm: float
    safety_flag: float
    latency_ms: float
    status: str


class GCodeCompileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trajectory_nodes: list[dict[str, float]] = Field(
        ...,
        min_length=1,
        max_length=100_000,
        json_schema_extra={
            "example": [{"x": 10.0, "y": 20.0, "z": 5.0, "a": 0.0, "b": 0.0}]
        },
        description="5-axis spatial coordinate records.",
    )


class GCodeCompileResponse(BaseModel):
    lines_compiled: int
    gcode_output: str


@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    return {
        "status": "HEALTHY",
        "timestamp": time.time(),
        "kernel_version": ck.KERNEL_VERSION,
        "core_nodes": ck.N_CORE,
        "external_gates": ck.BOUNDARY_COUNT,
        "register_addresses": ck.REGISTER_SIZE,
        "api_key_count": len(VALID_API_KEYS),
        "audit_ledger_integrity": audit_ledger.verify_integrity(),
    }


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post(
    "/api/v1/matrix/evaluate",
    response_model=MatrixEvalResponse,
    tags=["Experimental Numeric Adapter"],
)
def evaluate_matrix_state(
    req: MatrixEvalRequest,
    client_tier: str = Depends(verify_api_key),
) -> dict[str, float | str]:
    start_time = time.perf_counter()

    val = math.fsum(req.tensor_input) / len(req.tensor_input)
    energy_norm = 1.0 / (1.0 + math.exp(-max(-700.0, min(700.0, val))))
    safety_flag = 1.0 if energy_norm > 0.85 else 0.0

    elapsed = time.perf_counter() - start_time
    latency_ms = elapsed * 1000.0
    API_REQUESTS.labels(endpoint="matrix_evaluate", outcome="ok").inc()
    API_LATENCY.labels(endpoint="matrix_evaluate").observe(elapsed)

    audit_ledger.record_event(
        "API_MATRIX_EVALUATE",
        {
            "client_tier": client_tier,
            "energy_norm": energy_norm,
            "safety_flag": safety_flag,
            "latency_ms": latency_ms,
        },
    )

    return {
        "energy_norm": energy_norm,
        "safety_flag": safety_flag,
        "latency_ms": latency_ms,
        "status": "PASS" if safety_flag == 0.0 else "THRESHOLD_WARNING",
    }


@app.post(
    "/api/v1/gcode/compile",
    response_model=GCodeCompileResponse,
    tags=["5-Axis Compiler"],
)
def compile_gcode_path(
    req: GCodeCompileRequest,
    client_tier: str = Depends(verify_api_key),
) -> dict[str, Any]:
    compiled_lines = [
        "; Universal Matrix experimental G-code output",
        "G90 ; Absolute positioning",
        "G21 ; Metric units",
    ]

    for pt in req.trajectory_nodes:
        line = (
            f"G1 X{pt.get('x', 0.0):.3f} "
            f"Y{pt.get('y', 0.0):.3f} "
            f"Z{pt.get('z', 0.0):.3f} "
            f"A{pt.get('a', 0.0):.3f} "
            f"B{pt.get('b', 0.0):.3f} F1200"
        )
        compiled_lines.append(line)

    gcode_str = "\n".join(compiled_lines)
    API_REQUESTS.labels(endpoint="gcode_compile", outcome="ok").inc()

    audit_ledger.record_event(
        "API_GCODE_COMPILE",
        {
            "client_tier": client_tier,
            "node_count": len(req.trajectory_nodes),
        },
    )

    return {
        "lines_compiled": len(compiled_lines),
        "gcode_output": gcode_str,
    }


@app.get("/api/v1/audit/ledger", tags=["Cryptographic Audit"])
def get_audit_ledger(
    client_tier: str = Depends(verify_api_key),
) -> dict[str, Any]:
    _ = client_tier
    return {
        "integrity_verified": audit_ledger.verify_integrity(),
        "total_blocks": len(audit_ledger.chain),
        "chain": [block.to_dict() for block in audit_ledger.chain],
    }
