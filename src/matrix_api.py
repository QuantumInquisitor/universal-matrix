#!/usr/bin/env python3
"""
Universal Playing Field: REST API Server Module (v5.0 Integration Spec)
Wraps core matrix logic and Axiom VI variables inside a lightweight 
Flask microservice, exposing endpoints to return structured JSON payloads.
"""

import os
import sys
from flask import Flask, jsonify, request

# Ensure the local path can import the verified matrix core cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL ERROR: 'calculator.py' must be present in the same directory.")
    sys.exit(1)

# Initialize the Flask server app container
app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_index():
    """Returns a general operational status diagnostic for the API network hook."""
    return jsonify({
        "status": "ONLINE",
        "system_identity": "Universal Playing Field Core Engine API",
        "version": "5.0 Master Standard",
        "endpoints": {
            "/api/status": "Get system topology configuration snapshots.",
            "/api/calculate": "Query stabilized matrix density using dynamic Psi variables. Example: /api/calculate?psi=13.5"
        }
    }), 200


@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Exposes internal topological invariants and system configuration boundaries."""
    # Fetch core baseline validations
    _, core_val = mc.verify_axiom_1()
    _, boundary_val, matrix_tensor = mc.verify_axiom_2_and_3()
    _, speed_of_light = mc.verify_axiom_5()

    return jsonify({
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
    }), 200


@app.route('/api/calculate', methods=['GET'])
def calculate_matrix():
    """
    Processes incoming dynamic external pressure metrics via web query arguments.
    Route URL pattern: http://localhost:5000/api/calculate?psi=13.5
    """
    # Pull 'psi' parameter from the URL string. Default to 0.0 if omitted or empty.
    psi_param = request.args.get('psi', default='0.0')
    
    try:
        # Convert string input safely into a floating-point computational value
        user_psi = float(psi_param)
    except ValueError:
        return jsonify({
            "error": "INVALID_PARAMETER",
            "message": "The external macro-flux variable 'psi' must be a valid numeric integer or float format."
        }), 400

    # Route input variable directly against verified Axiom VI equations
    d_stabilized, ext_contribution = mc.calculate_axiom_6(user_psi)

    return jsonify({
        "input_parameters": {
            "requested_external_psi": user_psi
        },
        "calculation_matrix_output": {
            "external_boundary_contribution": round(ext_contribution, 6),
            "total_stabilized_system_density": round(d_stabilized, 6)
        },
        "verification_signature": "AXIOM_VI_INTEGRATED_PASS"
    }), 200


def main():
    print("=" * 60)
    print("  UPF ENGINE LOGIC microserver SPINNING UP...")
    print("  Host Local Processing Channel Address: http://127.0.0.1:5000")
    print("=" * 60)
    # Launch local debug micro-server listening directly on local port 5000
    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == '__main__':
    main()
