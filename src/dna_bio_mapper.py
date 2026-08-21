import math
import torch
from src.russell_periodic_mapper import RussellPeriodicEngine

# Base pair elemental composition ratios (C, N, O, H, P)
BASE_ELEMENTAL_MAP = {
    'A': {"C": 5, "N": 5, "O": 0, "H": 5, "P": 1, "name": "Adenine",   "bonds": 2},
    'T': {"C": 5, "N": 2, "O": 2, "H": 6, "P": 1, "name": "Thymine",   "bonds": 2},
    'C': {"C": 4, "N": 3, "O": 1, "H": 5, "P": 1, "name": "Cytosine",  "bonds": 3},
    'G': {"C": 5, "N": 5, "O": 1, "H": 5, "P": 1, "name": "Guanine",   "bonds": 3}
}

class DNABioMapper:
    """
    Translates genetic sequences into 13D gyroscopic state matrices
    and spatial double-helix coordinate meshes.
    """
    def __init__(self, base_freq: float = 432.0):
        self.russell_engine = RussellPeriodicEngine(base_freq=base_freq)
        self.helical_step_deg = 34.29  # 360 deg / 10.5 base pairs per full pitch turn

    def map_base_to_frequency(self, base_char: str):
        """Calculates harmonic resonance frequency based on elemental mass weighted average."""
        base = base_char.upper()
        if base not in BASE_ELEMENTAL_MAP:
            raise ValueError(f"Invalid nucleotide base: {base_char}. Must be A, T, C, or G.")

        elem_counts = BASE_ELEMENTAL_MAP[base]
        
        # Atomic numbers: H=1, C=6, N=7, O=8, P=15
        atomic_weights = {1: elem_counts["H"], 6: elem_counts["C"], 7: elem_counts["N"], 8: elem_counts["O"], 15: elem_counts["P"]}
        total_atoms = sum(atomic_weights.values())

        # Weighted frequency from Russell Periodic Engine
        total_freq = 0.0
        for z, count in atomic_weights.items():
            props = self.russell_engine.calculate_element_properties(z)
            total_freq += props["resonant_frequency_hz"] * count

        avg_freq = total_freq / total_atoms
        return {
            "base": base,
            "name": elem_counts["name"],
            "hydrogen_bonds": elem_counts["bonds"],
            "weighted_frequency_hz": round(avg_freq, 4),
            "element_breakdown": elem_counts
        }

    def sequence_to_13d_tensor(self, dna_sequence: str):
        """
        Converts a DNA sequence into a [N, 13] SO(13) state tensor where
        each nucleotide defines a gyroscopic helical position in 13D space.
        """
        seq = dna_sequence.upper()
        tensor_rows = []

        for idx, base in enumerate(seq):
            base_info = self.map_base_to_frequency(base)
            angle_rad = math.radians(idx * self.helical_step_deg)
            
            # Double helix coordinates (Strand A & Strand B phase offset by 180 deg)
            x = math.cos(angle_rad)
            y = math.sin(angle_rad)
            z = idx * 0.34  # 0.34 nm pitch rise per base step

            # Construct 13D vector: [3D spatial, Gyroscopic Tilt, Bonds, Freq, 7-D High-Toroid padding]
            v13 = [
                x, y, z,
                float(base_info["hydrogen_bonds"]),
                base_info["weighted_frequency_hz"] / 1000.0,
                math.sin(angle_rad * 2),
                math.cos(angle_rad * 2),
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ]
            tensor_rows.append(v13)

        return torch.tensor(tensor_rows, dtype=torch.float64)