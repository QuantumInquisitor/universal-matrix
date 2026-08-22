import numpy as np
import torch
from typing import Dict, Any, List

class ToroidalResonanceEngine:
    """
    Calculates multi-layer wave interference, phase coherence, and harmonic resonance
    between micro-biological tensors (T8) and macro-energetic lattices (T9-T12)
    within the 13D SO(13) toroidal manifold.
    """

    def __init__(self, base_freq: float = 432.0):
        self.base_freq = base_freq

    def calculate_phase_coherence(self, tensor_a: torch.Tensor, tensor_b: torch.Tensor) -> float:
        """
        Computes the cosine similarity phase coherence index between two 13D state vectors.
        Returns a value between 0.0 (incoherent/destructive) and 1.0 (perfect resonance).
        """
        vec_a = tensor_a.detach().cpu().numpy().flatten()
        vec_b = tensor_b.detach().cpu().numpy().flatten()

        min_len = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:min_len]
        vec_b = vec_b[:min_len]

        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        cosine_sim = np.dot(vec_a, vec_b) / (norm_a * norm_b)
        return float(np.clip((cosine_sim + 1.0) / 2.0, 0.0, 1.0))

    def compute_lattice_resonance_field(self, node_tensors: List[torch.Tensor]) -> Dict[str, Any]:
        """
        Synthesizes total field resonance, harmonic standing waves, and average 
        coherence across an arbitrary array of 13D lattice node state vectors.
        """
        if not node_tensors:
            return {"mean_coherence": 0.0, "total_nodes": 0, "resonant_frequency_hz": self.base_freq}

        coherence_scores = []
        primary_tensor = node_tensors[0]

        for tensor in node_tensors[1:]:
            score = self.calculate_phase_coherence(primary_tensor, tensor)
            coherence_scores.append(score)

        mean_coherence = float(np.mean(coherence_scores)) if coherence_scores else 1.0
        resonant_freq = self.base_freq * (1.0 + 0.042 * mean_coherence)

        return {
            "mean_coherence": round(mean_coherence, 4),
            "total_nodes": len(node_tensors),
            "resonant_frequency_hz": round(resonant_freq, 2),
            "field_stability": "Harmonic" if mean_coherence > 0.6 else "Turbulent"
        }
