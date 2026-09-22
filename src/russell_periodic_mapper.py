# LEGACY / COMPATIBILITY MODULE
# This module preserves an earlier experimental interface and may use historical
# SO(13), 114-node, 3/6/9, toroidal, biological, or related terminology.
# Those labels are not part of the current canonical Universal Matrix kernel
# unless separately migrated, documented, and tested. See ARCHITECTURE.md and
# docs/DOCUMENTATION_STATUS.md for current authority.

import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

BASE_FREQ_HZ = 432.0

RUSSELL_OCTAVE_POSITIONS = {
    0: {"name": "Inert Gas (Zero Axis)", "tilt_deg": 0.0,    "charge_bias": 0.0},
    1: {"name": "Alkali / Halogen",     "tilt_deg": 18.417, "charge_bias": +1.0},
    2: {"name": "Alkaline / Chalcogen", "tilt_deg": 36.833, "charge_bias": +2.0},
    3: {"name": "Boron / Pnictogen",    "tilt_deg": 65.217, "charge_bias": +3.0},
    4: {"name": "Carbon Group (Center)","tilt_deg": 90.0,   "charge_bias": +4.0}
}

class RussellPeriodicEngine:
    def __init__(self, base_freq: float = BASE_FREQ_HZ):
        self.base_freq = base_freq

    def calculate_element_properties(self, atomic_number: int) -> Dict[str, Any]:
        if atomic_number < 1 or atomic_number > 118:
            raise ValueError("Atomic number Z must be between 1 and 118.")

        TONE_MAP = {
            1: 1, 2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 3, 8: 2, 9: 1, 10: 0
        }

        octave = min(10, math.ceil(atomic_number / 11.8))
        tone_pos = TONE_MAP.get(atomic_number, (atomic_number - 2) % 5)

        pos_info = RUSSELL_OCTAVE_POSITIONS[tone_pos]
        tilt_rad = math.radians(pos_info["tilt_deg"])
        frequency_hz = self.base_freq * (2 ** (octave - 1)) * (1.0 + math.sin(tilt_rad))

        # SO(13) Gyroscopic Tilt Rotation Tensor
        tensor_matrix = [
            [round(math.cos(tilt_rad), 6), round(-math.sin(tilt_rad), 6)],
            [round(math.sin(tilt_rad), 6), round(math.cos(tilt_rad), 6)]
        ]

        return {
            "atomic_number": atomic_number,
            "octave": octave,
            "tone_position": tone_pos,
            "classification": pos_info["name"],
            "gyroscopic_tilt_deg": pos_info["tilt_deg"],
            "so13_rotation_tensor": tensor_matrix,
            "resonant_frequency_hz": round(frequency_hz, 4)
        }

    def map_matrix_nodes_to_periodic_grid(self, num_nodes: int = 114) -> List[Dict[str, Any]]:
        node_mappings = []
        for node_id in range(num_nodes):
            if node_id < 108:
                z_equivalent = int((node_id / 108.0) * 118) + 1
                prop = self.calculate_element_properties(z_equivalent)
                prop["node_id"] = node_id
                prop["node_type"] = "Internal Vortex Core"
            else:
                prop = {
                    "node_id": node_id,
                    "node_type": "Outer Hypercube Boundary Gate",
                    "octave": 0,
                    "tone_position": 0,
                    "classification": "Inert Zero Potential Boundary",
                    "gyroscopic_tilt_deg": 0.0,
                    "so13_rotation_tensor": [[1.0, 0.0], [0.0, 1.0]],
                    "resonant_frequency_hz": self.base_freq
                }
            node_mappings.append(prop)
        return node_mappings
