
from src.toroidal_winding_engine import ToroidalWindingEngine, WindingParameters

from src.plasma_shader_pipeline import PlasmaShaderCompiler, ShaderUniformsPayload

from src.webxr_haptic_controller import WebXRHapticController, SpatialXRState

from src.metrics_exporter import PrometheusMetricsExporter
from fastapi import Response

from src.auth_gateway import HardwareAuthGateway, TenantCredentials

from src.drift_predictor import QuantumDriftPredictor, TelemetryHistoryPayload

from src.swarm_controller import SwarmClusterOrchestrator, HardwareNodeStatus, SwarmCommandPayload

from src.sensor_network_gateway import PhysicalFieldCorrector, SensorTelemetryPayload

from src.closed_loop_bio_driver import ClosedLoopBioDriver

from src.sdr_rf_synthesizer import SDRRFSynthesizer, RFSignalConfig

from src.cnc_hardware_controller import CNCGRBLController, MachinePosition

from src.gpu_batch_accelerator import GPUBatchAccelerator

from src.russell_periodic_mapper import RussellPeriodicEngine
async def get_current_user():
    return "operator"

import numpy as np
import os
import json
import asyncio
import datetime
import jwt
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, Response, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

for collector in list(REGISTRY._collector_to_names.keys()):
    try:
        REGISTRY.unregister(collector)
    except KeyError:
        pass
import redis.asyncio as aioredis

from src.macro_lattice_mapper import MacroLatticeMapper
from src.toroidal_resonance_engine import ToroidalResonanceEngine
from src.dna_bio_mapper import DNABioMapper

# --- App Initialization & Constants ---
SECRET_KEY = "universal_matrix_super_secret_jwt_key_change_in_prod"
ALGORITHM = "HS256"
REDIS_CLUSTER_CHANNEL = "matrix_cluster_sync_channel"

app = FastAPI(title="Universal Matrix System API", version="6.4.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- Observability Metrics ---
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

ACTIVE_NODES_GAUGE.set(114)

# --- Subsystem Initialization ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

macro_mapper = MacroLatticeMapper(base_freq=432.0)
dna_mapper = DNABioMapper(base_freq=432.0)

engine_config = {
    "rotation_angle": 0.042,
    "matrix_dampening": 1.0,
    "step_delay": 0.05
}

# --- Authentication & Verification ---
USERS_DB = {
    "operator": {
        "username": "operator",
        "password": "matrix_secure_password_2026",
        "role": "admin"
    }
}

def verify_token(token: str = Depends(oauth2_scheme)):
    """Decodes JWT tokens and verifies admin operator privileges."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient RBAC permissions")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired Bearer token")

async def broadcast_cluster_state(state_payload: dict):
    """Broadcasts updated engine state across all distributed regional cluster nodes."""
    try:
        r = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        await r.publish(REDIS_CLUSTER_CHANNEL, json.dumps(state_payload))
        await r.close()
    except Exception:
        pass

# --- Data Models ---
class ControlPayload(BaseModel):
    rotation_angle: Optional[float] = None
    matrix_dampening: Optional[float] = None
    step_delay: Optional[float] = None

class DNASequencePayload(BaseModel):
    sequence: str = Field(..., description="Raw nucleotide sequence (A, T, C, G)", example="ATGCGATCG")

# --- System & Authentication Endpoints ---
@app.get("/")
def read_root():
    SYSTEM_REQUESTS_TOTAL.labels(method="GET", endpoint="/").inc()
    dashboard_path = os.path.join(STATIC_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"status": "online", "system": "114-Node Discrete Matrix Framework"}

@app.get("/metrics")
def get_prometheus_metrics():
    SYSTEM_REQUESTS_TOTAL.labels(method="GET", endpoint="/metrics").inc()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/v1/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token_expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    access_token = jwt.encode(
        {"sub": user["username"], "role": user["role"], "exp": token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Matrix Simulation & Streaming Endpoints ---
@app.get("/api/v1/telemetry/stream")
async def telemetry_stream():
    SYSTEM_REQUESTS_TOTAL.labels(method="GET", endpoint="/api/v1/telemetry/stream").inc()

    async def event_generator():
        step = 0
        while True:
            step += 1
            clock_drift = round(0.042 * step, 4)
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

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
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

@app.post("/api/v1/control")
async def update_control_parameters(payload: ControlPayload, current_user: dict = Depends(verify_token)):
    if payload.rotation_angle is not None:
        engine_config["rotation_angle"] = payload.rotation_angle
    if payload.matrix_dampening is not None:
        engine_config["matrix_dampening"] = payload.matrix_dampening
    if payload.step_delay is not None:
        engine_config["step_delay"] = payload.step_delay

    await broadcast_cluster_state({
        "event": "CONFIG_UPDATE",
        "config": engine_config,
        "operator": current_user["sub"]
    })

    return {"status": "success", "config": engine_config, "modified_by": current_user["sub"]}

# --- Biological & Energetic Mapping Endpoints ---
@app.post("/api/v1/dna/map")
async def map_dna_sequence(payload: DNASequencePayload, current_user: dict = Depends(verify_token)):
    try:
        seq = payload.sequence.strip().upper()
        base_metrics = [dna_mapper.map_base_to_frequency(base) for base in seq]
        tensor_13d = dna_mapper.sequence_to_13d_tensor(seq)
        
        await broadcast_cluster_state({
            "event": "DNA_MAPPING_LOADED",
            "sequence_length": len(seq),
            "torus_target_layer": 8,
            "operator": current_user["sub"]
        })

        return {
            "status": "success",
            "sequence": seq,
            "length": len(seq),
            "torus_target_layer": 8,
            "base_metrics": base_metrics,
            "tensor_13d_shape": list(tensor_13d.shape),
            "tensor_13d_sample": tensor_13d[:2].tolist()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/lattice/energetic")
async def get_energetic_lattice(current_user: dict = Depends(verify_token)):
    """Returns the 19-node subtle-energetic and macro-anatomical SO(13) field grid."""
    lattice_nodes = macro_mapper.map_full_energetic_lattice()
    return {
        "status": "success",
        "total_nodes": len(lattice_nodes),
        "target_layers": [9, 10, 11, 12],
        "lattice": lattice_nodes
    }

# --- Resonance Engine Instance ---
resonance_engine = ToroidalResonanceEngine(base_freq=432.0)

@app.get("/api/v1/resonance/coherence")
async def get_field_coherence(current_user: dict = Depends(verify_token)):
    """
    Returns real-time phase coherence, harmonic standing wave metrics,
    and field stability across active toroidal lattice nodes.
    """
    chakra_nodes = macro_mapper.map_full_energetic_lattice()
    tensors = [macro_mapper.get_chakra_torus_tensor(node["name"]) for node in chakra_nodes if node["category"] == "Chakra"]
    field_data = resonance_engine.compute_lattice_resonance_field(tensors)
    return {
        "status": "success",
        "resonance": field_data
    }

# --- Phase 8: Dynamic Resonance WebSocket Stream ---
@app.websocket("/ws/resonance/stream")
async def websocket_resonance_endpoint(websocket: WebSocket):
    """
    Bi-directional WebSocket streaming live toroidal field coherence, 
    harmonic oscillations, and accepting real-time frequency modulation inputs.
    """
    await websocket.accept()
    current_freq = 432.0
    phase_shift = 0.0

    try:
        while True:
            phase_shift += 0.042
            coherence = round(0.5 + 0.5 * np.sin(phase_shift), 4)
            resonant_hz = round(current_freq * (1.0 + 0.01 * np.cos(phase_shift)), 2)

            telemetry_packet = {
                "status": "synchronized",
                "phase_coherence": coherence,
                "resonant_frequency_hz": resonant_hz,
                "field_stability": "Harmonic" if coherence > 0.5 else "Turbulent",
                "phase_shift_rad": round(phase_shift, 4)
            }
            await websocket.send_text(json.dumps(telemetry_packet))

            # Non-blocking reception for live operator overrides
            try:
                incoming = await asyncio.wait_for(websocket.receive_text(), timeout=0.05)
                data = json.loads(incoming)
                if "base_freq" in data:
                    current_freq = float(data["base_freq"])
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        print("[WS] Client disconnected from /ws/resonance/stream")


from fastapi.responses import HTMLResponse
import os

@app.get("/", response_class=HTMLResponse)
async def get_spatial_telemetry_dashboard():
    """Serves the OpenXR spatial 3D telemetry dashboard and WebXR viewport."""
    html_file = os.path.join("src", "static", "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Reality Engine Spatial Viewport File Not Found</h1>"

# --- Phase 15: Biometrics Telemetry Ingestion Endpoints ---
from src.biometric_ingestion import BiometricTelemetryPayload, BiometricLatticeTransformer

transformer = BiometricLatticeTransformer()

@app.post("/api/v1/biometrics/ingest", tags=["Biometrics"])
async def ingest_biometric_telemetry(
    payload: BiometricTelemetryPayload,
    current_user: str = Depends(lambda: 'operator')
):
    """Processes real-time biometric telemetry and returns updated lattice coherence metrics."""
    metrics = transformer.compute_coherence_index(payload)
    return {
        "status": "success",
        "operator": current_user,
        "telemetry_metrics": metrics
    }

@app.websocket("/ws/biometrics/ingest")
async def websocket_biometrics_ingest(websocket: WebSocket):
    """Live bi-directional WebSocket stream for hardware biometric sensor streams."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            payload = BiometricTelemetryPayload(**data)
            metrics = transformer.compute_coherence_index(payload)
            await websocket.send_json({"type": "BIOMETRIC_LATTICE_UPDATE", "data": metrics})
    except WebSocketDisconnect:
        logger.info("[WS] Biometric telemetry client disconnected.")



# Phase 16: Walter Russell 10-Octave Periodic API Route
russell_engine = RussellPeriodicEngine()

@app.get("/api/v1/russell/element/{atomic_number}")
async def get_russell_element_properties(atomic_number: int):
    if atomic_number < 1 or atomic_number > 118:
        raise HTTPException(status_code=400, detail="Atomic number must be between 1 and 118.")
    return russell_engine.calculate_element_properties(atomic_number)

# Phase 17: CUDA / GPU Hardware Acceleration Batch Route
gpu_accelerator = GPUBatchAccelerator()

@app.post("/api/v1/hardware/gpu-batch")
async def execute_gpu_batch(batch: List[List[List[float]]], angle_rad: float = 0.0):
    if not batch:
        raise HTTPException(status_code=400, detail="Matrix batch payload cannot be empty.")
    return gpu_accelerator.execute_so13_batch_rotation(batch, angle_rad)

# Phase 18: CNC / GRBL Hardware Control Routes
cnc_controller = CNCGRBLController(mock_mode=True)

@app.post("/api/v1/hardware/cnc/gcode")
async def execute_cnc_gcode(command: str):
    if not command:
        raise HTTPException(status_code=400, detail="G-code command cannot be empty.")
    return cnc_controller.send_gcode_line(command)

@app.get("/api/v1/hardware/cnc/telemetry", response_model=MachinePosition)
async def get_cnc_telemetry():
    return cnc_controller.poll_telemetry()

# Phase 19: SDR RF Signal Transmission Route
sdr_synthesizer = SDRRFSynthesizer(mock_mode=True)

@app.post("/api/v1/hardware/sdr/transmit")
async def transmit_rf_signal(config: RFSignalConfig, num_samples: int = 1024):
    engine = SDRRFSynthesizer(config=config, mock_mode=True)
    return engine.transmit_carrier_burst(num_samples=num_samples)

# Phase 20: Closed-Loop Biometric Driver Route
bio_driver = ClosedLoopBioDriver()

@app.post("/api/v1/hardware/bio-loop/adapt")
async def process_closed_loop_bio(payload: BiometricPayload):
    return bio_driver.process_and_adapt(payload)

# Phase 21: Hardware Sensor Network Route
sensor_corrector = PhysicalFieldCorrector()

@app.post("/api/v1/hardware/sensors/ingest")
async def ingest_hardware_sensors(payload: SensorTelemetryPayload):
    return sensor_corrector.process_sensor_feed(payload)

# Phase 22: Autonomous Multi-Node Swarm Controller Routes
swarm_orchestrator = SwarmClusterOrchestrator()

@app.post("/api/v1/hardware/swarm/register")
async def register_swarm_node(node: HardwareNodeStatus):
    return swarm_orchestrator.register_node(node)

@app.post("/api/v1/hardware/swarm/dispatch")
async def dispatch_swarm_command(command: SwarmCommandPayload):
    return swarm_orchestrator.dispatch_swarm_command(command)

# Phase 23: Machine Learning Quantum Drift Predictor Route
drift_predictor = QuantumDriftPredictor()

@app.post("/api/v1/hardware/ml/predict-drift")
async def predict_quantum_drift(payload: TelemetryHistoryPayload):
    return drift_predictor.predict_decoherence_risk(payload)

# Phase 24: Enterprise JWT & Multi-Tenant Authentication Routes
auth_gateway = HardwareAuthGateway()

@app.post("/api/v1/auth/token")
async def request_tenant_token(creds: TenantCredentials):
    token = auth_gateway.generate_token(creds)
    return {"access_token": token, "token_type": "bearer", "expires_in": 3600}

@app.get("/api/v1/auth/verify")
async def verify_tenant_token(token: str):
    return auth_gateway.verify_token(token)

# Phase 25: Prometheus Metrics Exporter Route
metrics_exporter = PrometheusMetricsExporter()

@app.get("/metrics")
async def get_prometheus_metrics():
    content = metrics_exporter.generate_prometheus_metrics()
    return Response(content=content, media_type="text/plain")

# Phase 26: WebXR Haptic & Spatial Controller Route
xr_controller = WebXRHapticController()

@app.post("/api/v1/hardware/xr/process-frame")
async def process_xr_spatial_frame(state: SpatialXRState):
    return xr_controller.process_xr_frame(state)

# Phase 27: Volumetric Plasma & Waveguide Shader Route
shader_compiler = PlasmaShaderCompiler()

@app.post("/api/v1/hardware/shaders/compile")
async def compile_plasma_shader_uniforms(payload: ShaderUniformsPayload):
    return shader_compiler.compile_uniforms(payload)

# Phase 28: Multi-Axis CNC Toroidal Winding Route
winding_engine = ToroidalWindingEngine()

@app.post("/api/v1/hardware/cnc/winding-toolpath")
async def generate_toroidal_winding_toolpath(params: WindingParameters):
    return winding_engine.generate_5axis_gcode(params)
