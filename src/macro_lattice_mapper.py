import torch
import numpy as np
from typing import Dict, List, Any

class MacroLatticeMapper:
    """
    Maps biological macro-structures, Chinese Medicine Meridians, 
    Chakras/Nadis, and gross human anatomy into SO(13) toroidal field space.
    """
    
    # 7 Primary Chakras mapped to harmonic octaves and Torus Layers T9-T12
    CHAKRA_FREQUENCY_MAP = {
        "Root": {"freq_hz": 256.0, "color_rgb": (0.8, 0.1, 0.1), "nadi_count": 4, "layer": 9},
        "Sacral": {"freq_hz": 288.0, "color_rgb": (0.9, 0.4, 0.1), "nadi_count": 6, "layer": 9},
        "Solar_Plexus": {"freq_hz": 320.0, "color_rgb": (0.9, 0.8, 0.1), "nadi_count": 10, "layer": 10},
        "Heart": {"freq_hz": 341.3, "color_rgb": (0.1, 0.8, 0.2), "nadi_count": 12, "layer": 10},
        "Throat": {"freq_hz": 384.0, "color_rgb": (0.1, 0.6, 0.9), "nadi_count": 16, "layer": 11},
        "Third_Eye": {"freq_hz": 426.7, "color_rgb": (0.3, 0.2, 0.8), "nadi_count": 2, "layer": 11},
        "Crown": {"freq_hz": 480.0, "color_rgb": (0.7, 0.1, 0.9), "nadi_count": 1000, "layer": 12}
    }

    # 12 Primary Meridians mapped to Five Elements and organ systems
    MERIDIAN_SYSTEM_MAP = {
        "Lung": {"element": "Metal", "type": "Yin", "tissue": "Skin/Fascia"},
        "Large_Intestine": {"element": "Metal", "type": "Yang", "tissue": "Ligaments"},
        "Stomach": {"element": "Earth", "type": "Yang", "tissue": "Muscles"},
        "Spleen": {"element": "Earth", "type": "Yin", "tissue": "Connective Tissue"},
        "Heart": {"element": "Fire", "type": "Yin", "tissue": "Vessels/Arteries"},
        "Small_Intestine": {"element": "Fire", "type": "Yang", "tissue": "Veins"},
        "Bladder": {"element": "Water", "type": "Yang", "tissue": "Bones"},
        "Kidney": {"element": "Water", "type": "Yin", "tissue": "Marrow/Bones"},
        "Pericardium": {"element": "Fire", "type": "Yin", "tissue": "Vascular Wall"},
        "Triple_Burner": {"element": "Fire", "type": "Yang", "tissue": "Fascial Lattice"},
        "Gallbladder": {"element": "Wood", "type": "Yang", "tissue": "Tendons"},
        "Liver": {"element": "Wood", "type": "Yin", "tissue": "Tendons/Ligaments"}
    }

    def __init__(self, base_freq: float = 432.0):
        self.base_freq = base_freq

    def get_chakra_torus_tensor(self, chakra_name: str) -> torch.Tensor:
        """Generates a 13D SO(13) state vector for a specified chakra center."""
        if chakra_name not in self.CHAKRA_FREQUENCY_MAP:
            raise ValueError(f"Unknown Chakra: {chakra_name}")
            
        data = self.CHAKRA_FREQUENCY_MAP[chakra_name]
        freq = data["freq_hz"]
        
        vector = np.zeros(13, dtype=np.float64)
        for d in range(13):
            # Helical phase progression across subtle energetic octaves
            angle = (d + 1) * (freq / self.base_freq) * (2 * np.pi / 13)
            vector[d] = np.sin(angle) * (1.0 + 0.1 * data["nadi_count"] % 5)

        return torch.tensor(vector, dtype=torch.float64)

    def map_full_energetic_lattice(self) -> List[Dict[str, Any]]:
        """Maps all 7 Chakras, 12 Meridians, and Human Toroidal Nodes into spatial structs."""
        lattice_nodes = []
        
        # Build Chakra spatial nodes
        for idx, (name, details) in enumerate(self.CHAKRA_FREQUENCY_MAP.items()):
            tensor_13d = self.get_chakra_torus_tensor(name)
            lattice_nodes.append({
                "id": f"chakra_{idx+1}",
                "name": name,
                "category": "Chakra",
                "frequency_hz": details["freq_hz"],
                "target_layer": details["layer"],
                "color_rgb": details["color_rgb"],
                "tensor_sample": tensor_13d[:3].tolist()
            })
            
        # Build Meridian / Anatomical Tissue nodes
        for idx, (m_name, m_details) in enumerate(self.MERIDIAN_SYSTEM_MAP.items()):
            lattice_nodes.append({
                "id": f"meridian_{idx+1}",
                "name": f"{m_name} Meridian",
                "category": "Meridian/Anatomy",
                "element": m_details["element"],
                "polarity": m_details["type"],
                "target_tissue": m_details["tissue"],
                "target_layer": 10
            })

        return lattice_nodes