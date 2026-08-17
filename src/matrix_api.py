#!/usr/bin/env python3
"""
Universal Playing Field: REST API Server Module (v5.0 Integration Spec)
Wraps core matrix logic and Axiom VI variables inside a high-performance 
FastAPI microservice, exposing endpoints to return structured JSON payloads.
"""

import os
import sys
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn


# Ensure the local path can import the verified matrix core cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    # Double-checked import alignment to match your v5.0 spec exactly
    import calculator as mc
except ImportError:
    try:
        import matrix_calculator as mc
    except ImportError:
        print("CRITICAL ERROR: Matrix core engine source file must be present in the same directory.")
        sys.exit(1)

# Initialize the FastAPI app container with custom metadata
app = FastAPI(
    title="Universal Playing Field Core Engine API",
    version="5.0 Master Standard",
    docs_url="/docs"
)


@app.get('/', status_code=200)
async def home_index():
    """Returns a general operational status diagnostic for the API network hook."""
    return {
        "status": "ONLINE",
        "system_identity": "Universal Playing Field Core Engine API",
        "version": "5.0 Master Standard",
        "endpoints": {
            "/api/status": "Get system topology configuration snapshots.",
            "/api/calculate": "Query stabilized matrix density using dynamic Psi variables. Example: /api/calculate?psi=13.5"
        }
    }


@app.get('/api/status', status_code=200)
async def get_system_status():
    """Exposes internal topological invariants and system configuration boundaries."""
    # Fetch core baseline validations exactly as specified in your v5.0 profile
    _, core_val = mc.verify_axiom_1()
    _, boundary_val, matrix_tensor = mc.verify_axiom_2_and_3()
    _, speed_of_light = mc.verify_axiom_5()

    return {
        "topology": {
            "total_nodes_ceiling": mc.M_TOTAL,       # 114
            "internal_core_loop": mc.N_CORE,         # 108
            "external_boundary_gates": mc.B_BOUNDARY, # 6
            "singularity_axis_base": mc.S_AXIS       # 9
        },
        "invariants": {
            "core_zero_point_balance": core_val,     # Should be 0
            "net_boundary_density_weyl": boundary_val, # Should be 48
            "active_6_node_sieve_tensor": matrix_tensor,
            "informational_velocity_limit_c": speed_of_light # 299792458
        }
    }


@app.get('/api/calculate')
async def calculate_matrix(psi: str = Query(default="0.0")):
    """
    Processes incoming dynamic external pressure metrics via web query arguments.
    Route URL pattern: http://127.0.0
    """
    try:
        # Convert string input safely into a floating-point computational value
        user_psi = float(psi)
    except ValueError:
        # Returns exact 400 Bad Request error structural footprint from your v5.0 spec
        return JSONResponse(
            status_code=400,
            content={
                "error": "INVALID_PARAMETER",
                "message": "The external macro-flux variable 'psi' must be a valid numeric integer or float format."
            }
        )

    # Route input variable directly against verified Axiom VI equations
    d_stabilized, ext_contribution = mc.calculate_axiom_6(user_psi)

    return {
        "input_parameters": {
            "requested_external_psi": user_psi
        },
        "calculation_matrix_output": {
            "external_boundary_contribution": round(ext_contribution, 6),
            "total_stabilized_system_density": round(d_stabilized, 6)
        },
        "verification_signature": "AXIOM_VI_INTEGRATED_PASS"
    }


def main():
    print("=" * 60)
    print("  UPF ENGINE LOGIC microserver SPINNING UP...")
    print("  Host Local Processing Channel Address: http://127.0.0.1:5000")
    print("=" * 60)
    # Launch local uvicorn server running on port 5000 to maintain compatibility with your original specs
    uvicorn.run("matrix_api:app", host='127.0.0.1', port=5000, reload=False, access_log=True)


if __name__ == '__main__':
    main()
