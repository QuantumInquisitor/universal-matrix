#!/usr/bin/env python3
"""Legacy 11-component visualization router.

The historical filename/class name is retained for compatibility. This module
does not implement M-theory: it has no 11D supergravity action, supersymmetry,
M2/M5 branes, or 3-form gauge field. Treat its 11-component vectors as generic
visualization features only. See src/theory_bridge.py for the current
comparative-theory classification.
"""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
    import canonical_kernel as ck
except ImportError:
    print("CRITICAL: calculator.py missing from the local source directory.")
    sys.exit(1)

class MTheoryRouter:
    def __init__(self, dimensions=11):
        self.dimensions = dimensions
        self.total_nodes = ck.M_TOTAL
        self.core_nodes = ck.N_CORE
        self.calculator = mc.UniversalMatrixCalculator()
        self.alpha = mc.ALPHA_GEOMETRIC        # legacy visualization coefficient
        
        # Map explicit discrete projection basis for the matrix space
        self.basis_matrix = [
            [math.sin(i * j * (2 * math.pi / self.total_nodes)) for j in range(dimensions)]
            for i in range(self.total_nodes)
        ]

    def _calculate_string_vibration(self, mode: int, time_param: float) -> float:
        if mode == 0: return 0.0
        return math.cos(mode * time_param) / math.sqrt(abs(mode))

    def _compute_membrane_energy(self, layer_idx: int) -> float:
        factor = (layer_idx * math.pi) / self.total_nodes
        return abs(math.sin(factor) * math.cos(factor * 11))

    def route_omnidirectional_vr_data(self, system_state_id: int) -> dict:
        time_param = (system_state_id * 0.088)
        
        # Extract register bit configurations to enforce hardware interlocking constraints
        bit_offset = ck.register_address(system_state_id)
        up_bit = (self.calculator.STREAM_UP >> bit_offset) & 1
        down_bit = (self.calculator.STREAM_DOWN >> bit_offset) & 1
        
        # Compute generic 11-component visualization coordinates
        lattice_coords = []
        for d in range(self.dimensions):
            coord_sum = 0.0
            for n in range(self.total_nodes):
                mode_vibe = self._calculate_string_vibration(d, time_param)
                coord_sum += self.basis_matrix[n][d] * mode_vibe
            lattice_coords.append(coord_sum)
            
        # Down-project the 11-component visualization vector to 3D
        # Applying bit modulation weights and alpha geometric compression bounds
        bit_mod_scale = 1.0 + (up_bit * 0.1) - (down_bit * 0.1)
        x_comp = sum(lattice_coords[0:4]) * bit_mod_scale * (self.alpha * 16.5)
        y_comp = sum(lattice_coords[4:8]) * bit_mod_scale * (self.alpha * 16.5)
        z_comp = sum(lattice_coords[8:11]) * bit_mod_scale * (self.alpha * 16.5)
        
        # Normalize final omnidirectional data tracking vectors
        magnitude = math.sqrt(x_comp**2 + y_comp**2 + z_comp**2) or 1.0
        omni_vector = [x_comp / magnitude, y_comp / magnitude, z_comp / magnitude]
        
        membrane_density = self._compute_membrane_energy(system_state_id % self.total_nodes)
        
        return {
            "system_state_id": system_state_id,
            "11d_lattice_coordinates": [round(c, 5) for c in lattice_coords],
            "vr_data_packet": {
                "spatial_routing_address": f"LEGACY_11D_VIS_NODE_{system_state_id}",
                "model_status": "visualization_only_not_m_theory",
                "omnidirectional_vector": [round(v, 6) for v in omni_vector],
                "membrane_energy_density": round(membrane_density, 6)
            }
        }

if __name__ == "__main__":
    router = MTheoryRouter()
    print("11D Telemetry Routing Test Vector (Node 9):")
    print(router.route_omnidirectional_vr_data(9))
