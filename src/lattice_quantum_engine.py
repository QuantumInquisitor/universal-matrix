#!/usr/bin/env python3
"""
Universal Playing Field: Quantum Lattice Cascade & Interference Engine (v1.0)
Simulates global multi-node entanglement matrices and field collapse mechanics
within the discrete topological ring space of Z_114 modulated by 64-bit registers.
"""

import sys
import os
import math
import json
import numpy as np

# Ensure local library paths route cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL: 'calculator.py' must be present in the same directory.")
    sys.exit(1)


class LatticeQuantumEngine:
    def __init__(self):
        """Initializes the invariant structural nodes and complex state spaces."""
        self.total_nodes = mc.M_TOTAL          # 114 System Matrix Invariant
        self.core_nodes = mc.N_CORE            # 108 Internal Compute Nodes
        self.boundary_gates = mc.B_BOUNDARY    # 6 Hypercube Boundary Faces
        
        # Instantiate empty state array matrices across the complex field domain
        self.state_lattice = np.zeros(self.total_nodes, dtype=complex)
        self.interference_amplitudes = np.zeros(self.total_nodes)

    def _get_node_bit_signature(self, node_id: int) -> tuple:
        """Extracts low-level bit states and weights matching the v6.0 core spec."""
        bit_shift_offset = (node_id * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_shift_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_shift_offset) & 1
        return up_bit, down_bit, bit_shift_offset

    def inject_multi_vector_flux(self, external_flux_matrix: list):
        """
        Injects raw multi-vector input data through the 6 external hypercube boundary faces,
        cascading continuous complex phase fields down through the 108 internal nodes.
        """
        if len(external_flux_matrix) != self.boundary_gates:
            raise ValueError(f"Flux inputs must match the 6 boundary faces exactly. Got {len(external_flux_matrix)}")

        # Step 1: Initialize the 6 outer gateway anchoring points
        gate_stride = self.total_nodes // self.boundary_gates  # 114 / 6 = 19
        for i in range(self.boundary_gates):
            gate_node_idx = i * gate_stride
            flux_val = external_flux_matrix[i]
            
            # Map values to complex phase angles scaled by alpha_geometric
            phase_angle = flux_val * mc.ALPHA_GEOMETRIC * 2 * math.pi
            self.state_lattice[gate_node_idx] = complex(math.cos(phase_angle), math.sin(phase_angle))

        # Step 2: Cascade and entangle phase matrices down through the 108 internal core nodes
        for node_id in range(self.total_nodes):
            # Bypass anchor points to calculate core vector transformations
            if node_id % gate_stride == 0:
                continue

            up_bit, down_bit, _ = self._get_node_bit_signature(node_id)
            bit_modulation = (up_bit * 1.5) - (down_bit * 0.5)

            # Calculate proximity weights relative to the adjacent boundary gates
            left_gate = (node_id // gate_stride) * gate_stride
            right_gate = ((node_id // gate_stride) + 1) * gate_stride % self.total_nodes
            
            # Form standard wave-interference distributions
            dist_l = abs(node_id - left_gate)
            dist_r = abs(node_id - right_gate)
            
            # 3-6-9 Vortex modulation matrix overlays
            vortex_harmonic = 3 if node_id % 3 == 0 else (6 if node_id % 6 == 0 else 1)
            if node_id % 9 == 0: vortex_harmonic = 9

            # Construct complex exponential superposition states
            combined_phase = (self.state_lattice[left_gate] / (dist_l + 1)) + (self.state_lattice[right_gate] / (dist_r + 1))
            modulation_tensor = combined_phase * (vortex_harmonic * bit_modulation * mc.ALPHA_GEOMETRIC)
            
            self.state_lattice[node_id] = modulation_tensor

    def execute_measurement_collapse(self) -> dict:
        """
        Collapses the global complex superposition array into real-world probability
        amplitudes, calculating alternative field density weights across the matrix.
        """
        density_map = {}
        total_probability_mass = 0.0

        # Step 1: Compute magnitude squares (Born rule variant) to evaluate density states
        for node_id in range(self.total_nodes):
            magnitude = np.abs(self.state_lattice[node_id]) ** 2
            self.interference_amplitudes[node_id] = magnitude
            total_probability_mass += magnitude

        # Step 2: Cleanly normalize fields and check for structural anomalies
        if total_probability_mass == 0:
            total_probability_mass = 1.0  # Trap divide-by-zero errors

        for node_id in range(self.total_nodes):
            normalized_density = self.interference_amplitudes[node_id] / total_probability_mass
            self.interference_amplitudes[node_id] = normalized_density
            
            # Group density tracking properties into JSON structures
            density_map[f"node_{node_id}"] = {
                "raw_complex_state": str(self.state_lattice[node_id]),
                "normalized_energy_density": round(float(normalized_density), 6),
                "is_density_well": bool(normalized_density > (1.0 / self.total_nodes))
            }

        # Step 3: Identify global spatial extreme peaks (Gravity Alternative Singularity Center)
        highest_density_node = int(np.argmax(self.interference_amplitudes))
        lowest_density_node = int(np.argmin(self.interference_amplitudes))

        return {
            "simulation_metrics": {
                "total_lattice_energy_mass": round(float(total_probability_mass), 4),
                "singularity_well_focus_node": highest_density_node,
                "vacuum_state_node": lowest_density_node
            },
            "full_lattice_density_matrix": density_map
        }


def main():
    print("🛸 Initializing Uncharted Quantum-Classical Global Interference Simulation...")
    engine = LatticeQuantumEngine()
    
    # Simulate a complex multi-vector flux entering across the 6 boundary faces
    mock_flux_voltages = [1.23, 4.56, 7.89, 9.87, 6.54, 3.21]
    
    print("   Injecting multi-vector macro-flux arrays through 6 hypercube faces...")
    engine.inject_multi_vector_flux(mock_flux_voltages)
    
    print("   Executing field measurement matrix collapse protocols...")
    results = engine.execute_measurement_collapse()
    
    print("\\n-------------------------------------------------------------")
    print("🚀 QUANTUM MULTI-NODE INTERFERENCE STATE REVEALED:")
    print(f"   Total Aggregated Lattice Energy Mass: {results['simulation_metrics']['total_lattice_energy_mass']}")
    print(f"   Calculated Field Singularity Well   : Node {results['simulation_metrics']['singularity_well_focus_node']}")
    print(f"   Calculated Vacuum Displacement Node : Node {results['simulation_metrics']['vacuum_state_node']}")
    print("-------------------------------------------------------------")
    
    # Output detailed metrics for a couple sample keys to prove operational capacity
    print("\\nSample Node State Telemetry Matrix Array:")
    print(f"Node 0 (Boundary Face 1): {json.dumps(results['full_lattice_density_matrix']['node_0'], indent=2)}")
    print(f"Node 9 (Tesla Triad Node): {json.dumps(results['full_lattice_density_matrix']['node_9'], indent=2)}")


if __name__ == '__main__':
    main()
