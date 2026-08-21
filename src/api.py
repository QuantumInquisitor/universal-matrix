import os
import asyncio
import json
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Universal Matrix System API", version="6.4.0")

# --- Prometheus Observability Metrics ---
SYSTEM_REQUESTS_TOTAL = Counter(
    "matrix_api_requests_total",
    "Total HTTP requests handled by the Matrix API",
    ["method", "endpoint"]
)

MATRIX_STEP_COUNTER = Counter(
    "matrix_simulation_steps_total",
    "Total simulation steps executed across active matrix processes"
)

MATRIX_CLOCK_DRIFT = Gauge(
    "matrix_clock_drift_nanoseconds",
    "Real-time matrix clock drift variance in nanoseconds"
)

ACTIVE_NODES_GAUGE = Gauge(
    "matrix_active_nodes_count",
    "Number of active matrix nodes in the 114-Node Discrete Framework"
)

# Initialize static gauge baseline
ACTIVE_NODES_GAUGE.set(114)

# Determine path to 'static' directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    """Serve the Telemetry Web Dashboard as the primary interface."""
    SYSTEM_REQUESTS_TOTAL.labels(method="GET", endpoint="/").inc()
    dashboard_path = os.path.join(STATIC_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"status": "online", "system": "114-Node Discrete Matrix Framework"}


@app.get("/metrics")
def get_prometheus_metrics():
    """Expose standard OpenTelemetry / Prometheus metrics endpoint for Grafana scraping."""
    SYSTEM_REQUESTS_TOTAL.labels(method="GET", endpoint="/metrics").inc()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/telemetry/stream")
async def telemetry_stream():
    """Real-time SSE channel streaming matrix clock-drift and node probability states."""
    SYSTEM_REQUESTS_TOTAL.labels(method="GET", endpoint="/api/v1/telemetry/stream").inc()

    async def event_generator():
        step = 0
        while True:
            step += 1
            clock_drift = round(0.042 * step, 4)

            # Update Prometheus Gauges and Counters
            MATRIX_STEP_COUNTER.inc()
            MATRIX_CLOCK_DRIFT.set(clock_drift)

            data = {
                "step": step,
                "status": "synchronized",
                "clock_drift_ns": clock_drift,
                "active_nodes": 114,
                "norm_sum": 1.0000
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import json
import asyncio

# Global runtime engine parameters
engine_config = {
    "rotation_angle": 0.042,
    "matrix_dampening": 1.0,
    "step_delay": 0.05
}

class ControlPayload(BaseModel):
    rotation_angle: float | None = None
    matrix_dampening: float | None = None
    step_delay: float | None = None

@app.post("/api/v1/control")
async def update_control_parameters(payload: ControlPayload):
    """Update runtime simulation physics parameters dynamically."""
    if payload.rotation_angle is not None:
        engine_config["rotation_angle"] = payload.rotation_angle
    if payload.matrix_dampening is not None:
        engine_config["matrix_dampening"] = payload.matrix_dampening
    if payload.step_delay is not None:
        engine_config["step_delay"] = payload.step_delay
    return {"status": "success", "config": engine_config}

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Bi-directional WebSocket streaming telemetry and accepting control inputs."""
    await websocket.accept()
    try:
        while True:
            # Broadcast state packet to client
            telemetry_data = {
                "step": getattr(app.state, "step", 0),
                "clock_drift_ns": getattr(app.state, "clock_drift_ns", 0.0),
                "config": engine_config,
                "nodes": [
                    {
                        "id": i,
                        "x": float((i % 12) - 6),
                        "y": float((i // 12) - 5),
                        "z": float((i * 0.1) % 5 - 2.5),
                        "vx": float((i * engine_config["rotation_angle"]) % 1.0),
                        "vy": float((i * engine_config["matrix_dampening"]) % 1.0)
                    }
                    for i in range(114)
                ]
            }
            await websocket.send_text(json.dumps(telemetry_data))
            
            # Non-blocking check for incoming client control messages
            try:
                incoming = await asyncio.wait_for(websocket.receive_text(), timeout=engine_config["step_delay"])
                data = json.loads(incoming)
                if "rotation_angle" in data:
                    engine_config["rotation_angle"] = float(data["rotation_angle"])
                if "step_delay" in data:
                    engine_config["step_delay"] = float(data["step_delay"])
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        print("[WS] Client disconnected from /ws/telemetry")