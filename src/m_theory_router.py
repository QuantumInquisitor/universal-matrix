#!/usr/bin/env python3
"""
Universal Playing Field: 11D M-Theory Super-Lattice & Omnidirectional VR Router
Maps discrete 11-dimensional string/brane vibrations directly to 64-bit hardware
bitmasks and routes metrics down to omnidirectional stereographic VR meshes.
"""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL: calculator.py missing from the local source directory.")
    sys.exit(1)

class MTheoryRouter:
    def __init__(self, dimensions=11):
        self.dimensions = dimensions
        self.total_nodes = mc.M_TOTAL          # 114 Invariant Node Base
        self.alpha = mc.ALPHA_GEOMETRIC        # Derived attenuation coefficient
        
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
        bit_offset = (system_state_id * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_offset) & 1
        
        # Compute 11D Lattice coordinates
        lattice_coords = []
        for d in range(self.dimensions):
            coord_sum = 0.0
            for n in range(self.total_nodes):
                mode_vibe = self._calculate_string_vibration(d, time_param)
                coord_sum += self.basis_matrix[n][d] * mode_vibe
            lattice_coords.append(coord_sum)
            
        # Down-project 11D hyper-spatial coordinates to 3D Cartesian VR meshes
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
                "spatial_routing_address": f"M_THEORY_11D_NODE_{system_state_id}",
                "omnidirectional_vector": [round(v, 6) for v in omni_vector],
                "membrane_energy_density": round(membrane_density, 6)
            }
        }

if __name__ == "__main__":
    router = MTheoryRouter()
    print("11D Telemetry Routing Test Vector (Node 9):")
    print(router.route_omnidirectional_vr_data(9))
