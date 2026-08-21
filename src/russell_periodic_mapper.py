import math

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

    def calculate_element_properties(self, atomic_number: int):
        """Maps an Atomic Number (Z = 1 to 118) to Russell's Octave, Tone Position, and Frequency."""
        if atomic_number < 1 or atomic_number > 118:
            raise ValueError("Atomic number Z must be between 1 and 118.")

        TONE_MAP = {
            1: 1,  # H
            2: 0,  # He (Inert)
            3: 1,  # Li
            4: 2,  # Be
            5: 3,  # B
            6: 4,  # C (Maximum 90-degree amplitude peak)
            7: 3,  # N
            8: 2,  # O
            9: 1,  # F
            10: 0  # Ne (Inert)
        }

        octave = min(9, math.ceil(atomic_number / 12.0))
        tone_pos = TONE_MAP.get(atomic_number, (atomic_number - 2) % 5)

        pos_info = RUSSELL_OCTAVE_POSITIONS[tone_pos]
        tilt_rad = math.radians(pos_info["tilt_deg"])
        frequency_hz = self.base_freq * (2 ** (octave - 1)) * (1.0 + math.sin(tilt_rad))

        return {
            "atomic_number": atomic_number,
            "octave": octave,
            "tone_position": tone_pos,
            "classification": pos_info["name"],
            "gyroscopic_tilt_deg": pos_info["tilt_deg"],
            "resonant_frequency_hz": round(frequency_hz, 4)
        }

    def map_matrix_nodes_to_periodic_grid(self, num_nodes: int = 114):
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
                    "resonant_frequency_hz": self.base_freq
                }
            node_mappings.append(prop)
        return node_mappings