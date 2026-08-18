#!/usr/bin/env python3
"""
Universal Playing Field: Dynamic REST API Layer (v1.0 Peer-Review Standard)
Exposes the discrete 114-node topological registers via an ASGI endpoints web layer.
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ensure local path can load calculator variables cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL: 'calculator.py' must be present in the same directory.")
    sys.exit(1)

# Initialize the core ASGI web framework
app = FastAPI(
    title="Universal Playing Field API Matrix",
    description="Decentralized Real-Time Verification Node for 114-Node Discrete Lattices.",
    version="6.0"
)

# Define response payload validation schemas using Pydantic models
class SystemStatusSchema(BaseModel):
    status: str
    hardware_footprint: str
    alpha_geometric: float
    registers: dict

class NodeStateSchema(BaseModel):
    node_id: int
    classification: str
    coordinates_3d: dict
    bit_state: dict


@app.get("/", tags=["System Status"])
def read_root():
    """Returns the foundational network state validation summary."""
    a1_pass, a1_val = mc.verify_axiom_1()
    a2_pass, a2_val, _ = mc.verify_axiom_2_and_3()
    a5_pass, c_val = mc.verify_axiom_5()
    
    return {
        "network_identifier": "UPF_NODE_LATTICE_B64",
        "system_equilibrium": "BALANCED" if a1_pass else "ERR_DISPLACED",
        "weyl_symmetry_density": "VERIFIED (48)" if a2_pass else "ERR_MUTATED",
        "velocity_invariance": "MATCHED (299792458 m/s)" if a5_pass else "ERR_DRIFT",
        "alpha_geometric_constant": mc.ALPHA_GEOMETRIC
    }


@app.get("/api/v1/registers", response_model=SystemStatusSchema, tags=["Hardware Registers"])
def get_hardware_registers():
    """Queries the exact 64-bit integer bitmasks currently initialized on hardware registers."""
    return {
        "status": "synchronized",
        "hardware_footprint": "64-bit padded array matrix",
        "alpha_geometric": mc.ALPHA_GEOMETRIC,
        "registers": {
            "S_up": {"decimal": mc.STREAM_UP, "hex": hex(mc.STREAM_UP)},
            "S_down": {"decimal": mc.STREAM_DOWN, "hex": hex(mc.STREAM_DOWN)},
            "Delta_S": {"decimal": mc.DELTA_S, "hex": hex(mc.DELTA_S)}
        }
    }


@app.get("/api/v1/node/{node_id}", response_model=NodeStateSchema, tags=["Topological Nodes"])
def get_node_state(node_id: int):
    """
    Queries the deterministic state metrics of a specific individual coordinate node (0-113).
    Calculates 3D spatial mapping arrays on-the-fly from active bit registers.
    """
    if node_id < 0 or node_id >= mc.M_TOTAL:
        raise HTTPException(
            status_code=404, 
            detail=f"Node Index Boundary Error: Value must sit securely within range 0 to {mc.M_TOTAL - 1}."
        )

    # Programmatically extract the node's distinct bit-shifting properties matching src/vr_13d_space.py
    bit_shift_offset = (node_id * 7) % 64
    up_bit = (mc.STREAM_UP >> bit_shift_offset) & 1
    down_bit = (mc.STREAM_DOWN >> bit_shift_offset) & 1
    
    # Isolate boundary gate classifications
    is_boundary_gate = (node_id % (mc.M_TOTAL // mc.B_BOUNDARY)) == 0
    classification_string = "6-Node Outer Hypercube Boundary Gate" if is_boundary_gate else "108-Node Core Processing Manifold"

    # Derive baseline spherical coordinate tracking values
    phi = math.acos(1 - 2 * (node_id + 0.5) / mc.M_TOTAL)
    theta = math.pi * (1.0 + math.sqrt(5.0)) * node_id
    
    # Modulate local geometry footprint via the analytical compression scale factor
    bit_mod = (up_bit * 0.05) - (down_bit * 0.05)
    dynamic_minor_radius = 15.0 * (1.0 + bit_mod * (mc.ALPHA_GEOMETRIC * 10.0))
    major_radius = 50.0

    # Project raw Cartesian vectors
    x = (major_radius + dynamic_minor_radius * math.cos(phi)) * math.cos(theta)
    y = (major_radius + dynamic_minor_radius * math.cos(phi)) * math.sin(theta)
    z = dynamic_minor_radius * math.sin(phi)

    return {
        "node_id": node_id,
        "classification": classification_string,
        "coordinates_3d": {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4)},
        "bit_state": {"up_bit": up_bit, "down_bit": down_bit, "shift_offset": bit_shift_offset}
    }
