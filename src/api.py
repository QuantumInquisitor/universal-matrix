#!/usr/bin/env python3
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
    from field_synthesizer import FieldSynthesizer
    from lattice_quantum_engine import LatticeQuantumEngine
    from geodesic_simulator import GeodesicSimulator
    from light_cone_simulator import LightConeSimulator
    from m_theory_router import MTheoryRouter
except ImportError:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    sys.path.insert(0, root_dir)
    import calculator as mc
    from field_synthesizer import FieldSynthesizer
    from lattice_quantum_engine import LatticeQuantumEngine
    from geodesic_simulator import GeodesicSimulator
    from light_cone_simulator import LightConeSimulator
    from m_theory_router import MTheoryRouter

app = FastAPI(title="The Universal Playing Field Matrix Engine", version="6.4.0")

synthesizer = FieldSynthesizer()
quantum_engine = LatticeQuantumEngine()
orbiter = GeodesicSimulator()
tracer = LightConeSimulator()
m_theory_engine = MTheoryRouter()

class FluxInput(BaseModel):
    flux_matrix: list = [1.23, 4.56, 7.89, 9.87, 6.54, 3.21]

class MTheoryBatchInput(BaseModel):
    state_ids: list = []

@app.get("/")
async def get_root_verification_registry():
    return {"status": "VERIFIED_NODE_NETWORK_ACTIVE", "matrix_ring": "Z_114", "alpha_geometric": float(mc.ALPHA_GEOMETRIC)}

@app.get("/api/v1/node/{node_id}")
async def query_individual_node(node_id: int):
    if node_id < 0 or node_id >= mc.M_TOTAL: raise HTTPException(status_code=404)
    bit_offset = (node_id * 7) % 64
    return {"node_id": node_id, "up_bit_state": int((mc.STREAM_UP >> bit_offset) & 1), "down_bit_state": int((mc.STREAM_DOWN >> bit_offset) & 1)}

@app.get("/api/v1/simulation/m-theory-router/{state_id}")
async def query_m_theory_vr_routing(state_id: int):
    try: return m_theory_engine.route_omnidirectional_vr_data(state_id)
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/simulation/m-theory-batch")
async def query_m_theory_batch_routing(payload: MTheoryBatchInput):
    try:
        batch_stream = [m_theory_engine.route_omnidirectional_vr_data(s_id) for s_id in payload.state_ids]
        return {"batch_count": len(batch_stream), "telemetry_stream": batch_stream}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/simulation/waveguide/{node_id}")
async def query_rf_waveguide_synthesis(node_id: int, voltage: float = 1.0):
    return synthesizer.synthesize_waveguide(node_id, external_flux_voltage=voltage)

@app.post("/api/v1/simulation/quantum-cascade")
async def trigger_lattice_quantum_collapse(payload: FluxInput):
    quantum_engine.inject_multi_vector_flux(payload.flux_matrix)
    return quantum_engine.execute_measurement_collapse()

@app.get("/api/v1/simulation/geodesic-orbit")
async def trigger_orbit_propagation(steps: int = 50):
    return orbiter.propagate_orbit(steps=steps)

@app.get("/api/v1/simulation/light-cone")
async def trigger_light_cone_trace(angle: float = 0.5, wavelength: float = 532.0):
    return tracer.simulate_light_ray(entrance_angle_rad=angle, wavelength_nm=wavelength)
