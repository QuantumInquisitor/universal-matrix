#!/usr/bin/env python3
"""
Universal Playing Field: Asynchronous ASGI Web Endpoint Interface (v6.2)
Exposes matrix registers, waveguide syntheses, and quantum lattice simulations.
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ensure native path resolution for core imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
    from field_synthesizer import FieldSynthesizer
    from lattice_quantum_engine import LatticeQuantumEngine
    from geodesic_simulator import GeodesicSimulator
    from light_cone_simulator import LightConeSimulator
except ImportError as e:
    sys.exit(f"CRITICAL: Structural dependencies missing from src directory: {e}")

app = FastAPI(
    title="The Universal Playing Field Matrix Engine",
    description="Asynchronous ASGI topological endpoint framework exposing v6.2 discrete spacetime nodes.",
    version="6.2.0"
)

# Instantiate static simulation bridges
synthesizer = FieldSynthesizer()
quantum_engine = LatticeQuantumEngine()
orbiter = GeodesicSimulator()
tracer = LightConeSimulator()

class FluxInput(BaseModel):
    flux_matrix: list = [1.23, 4.56, 7.89, 9.87, 6.54, 3.21]

@app.get("/")
async def get_root_verification_registry():
    return {
        "status": "VERIFIED_NODE_NETWORK_ACTIVE",
        "matrix_ring": "Z_114",
        "alpha_geometric": float(mc.ALPHA_GEOMETRIC),
        "hardware_stream_up": hex(mc.STREAM_UP),
        "hardware_stream_down": hex(mc.STREAM_DOWN)
    }

@app.get("/api/v1/registers")
async def get_hardware_payload():
    return {
        "stream_up_bits": [int((mc.STREAM_UP >> i) & 1) for i in range(64)],
        "stream_down_bits": [int((mc.STREAM_DOWN >> i) & 1) for i in range(64)],
        "delta_s_invariants": int(mc.DELTA_S)
    }

@app.get("/api/v1/node/{node_id}")
async def query_individual_node(node_id: int):
    if node_id < 0 or node_id >= mc.M_TOTAL:
        raise HTTPException(status_code=404, detail=f"Node index {node_id} out of bounds.")
    bit_offset = (node_id * 7) % 64
    return {
        "node_id": node_id,
        "is_tesla_control_triad": bool(node_id % 3 == 0 or node_id % 6 == 0 or node_id % 9 == 0),
        "up_bit_state": int((mc.STREAM_UP >> bit_offset) & 1),
        "down_bit_state": int((mc.STREAM_DOWN >> bit_offset) & 1)
    }

@app.get("/api/v1/simulation/waveguide/{node_id}")
async def query_rf_waveguide_synthesis(node_id: int, voltage: float = 1.0):
    res = synthesizer.synthesize_waveguide(node_id, external_flux_voltage=voltage)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/v1/simulation/quantum-cascade")
async def trigger_lattice_quantum_collapse(payload: FluxInput):
    try:
        quantum_engine.inject_multi_vector_flux(payload.flux_matrix)
        return quantum_engine.execute_measurement_collapse()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/simulation/geodesic-orbit")
async def trigger_orbit_propagation(steps: int = 50):
    return orbiter.propagate_orbit(steps=steps)

@app.get("/api/v1/simulation/light-cone")
async def trigger_light_cone_trace(angle: float = 0.5, wavelength: float = 532.0):
    return tracer.simulate_light_ray(entrance_angle_rad=angle, wavelength_nm=wavelength)
