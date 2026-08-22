import numpy as np
import torch
from typing import Dict, List, Any
from src.macro_lattice_mapper import MacroLatticeMapper

class VR13DIntegrationEngine:
    """
    Renders 13D SO(13) field matrices, DNA spatial geometry, 
    and subtle-energetic/anatomical lattices in interactive VR/3D space.
    """

    def __init__(self, base_freq: float = 432.0):
        self.base_freq = base_freq
        self.macro_mapper = MacroLatticeMapper(base_freq=base_freq)

    def project_13d_to_3d(self, tensor_13d: np.ndarray) -> np.ndarray:
        """Projects a 13D SO(13) vector array into 3D Cartesian space (X, Y, Z)."""
        if tensor_13d.ndim == 1:
            tensor_13d = tensor_13d.reshape(1, -1)
            
        # Extract primary 3D spatial basis via harmonic projection matrix
        x = tensor_13d[:, 0] + 0.5 * tensor_13d[:, 3] + 0.25 * tensor_13d[:, 6]
        y = tensor_13d[:, 1] + 0.5 * tensor_13d[:, 4] + 0.25 * tensor_13d[:, 7]
        z = tensor_13d[:, 2] + 0.5 * tensor_13d[:, 5] + 0.25 * tensor_13d[:, 8]
        
        return np.column_stack((x, y, z))

    def generate_energetic_vr_mesh(self) -> Dict[str, Any]:
        """Generates 3D vertex positions and color arrays for the full energetic lattice."""
        lattice = self.macro_mapper.map_full_energetic_lattice()
        vr_nodes = []

        for idx, node in enumerate(lattice):
            if node["category"] == "Chakra":
                tensor_13d = self.macro_mapper.get_chakra_torus_tensor(node["name"]).numpy()
                pos_3d = self.project_13d_to_3d(tensor_13d)[0]
                vr_nodes.append({
                    "id": node["id"],
                    "label": node["name"],
                    "category": "Chakra",
                    "position": pos_3d.tolist(),
                    "color": node["color_rgb"],
                    "scale": 1.5,
                    "target_layer": node["target_layer"]
                })
            else:
                # Meridian / Tissue structural placement
                angle = (idx - 7) * (2 * np.pi / 12)
                pos_3d = [np.cos(angle) * 3.0, (idx - 13) * 0.5, np.sin(angle) * 3.0]
                vr_nodes.append({
                    "id": node["id"],
                    "label": node["name"],
                    "category": "Meridian",
                    "element": node["element"],
                    "polarity": node["polarity"],
                    "tissue": node["target_tissue"],
                    "position": pos_3d,
                    "color": [0.2, 0.7, 0.9],
                    "scale": 0.8,
                    "target_layer": 10
                })

        return {
            "node_count": len(vr_nodes),
            "vr_nodes": vr_nodes
        }
