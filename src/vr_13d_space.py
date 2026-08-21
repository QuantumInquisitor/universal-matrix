import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import calculator as mc
from lattice_quantum_engine import LatticeQuantumEngine

# Fallback for Golden Ratio Resonance
PHI = getattr(mc, 'GOLDEN_RATIO_RESONANCE', getattr(mc, 'PHI', (1.0 + np.sqrt(5.0)) / 2.0))

class VR13DTorusSpace:
    def __init__(self):
        self.fig = plt.figure(figsize=(14, 10), facecolor='black')
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='black')
        
        self.total_nodes = getattr(mc, 'TOTAL_NODES', 114)
        self.core_nodes = getattr(mc, 'N_CORE', 108)
        self.quantum_engine = LatticeQuantumEngine()
        
        # 14 Toroidal Layers & 13 Dimensions Setup
        self.num_layers = 14
        self.active_layer = 0  # 0 = All Layers, 1-14 = Specific Layer focus
        self.active_dims = [0, 1, 2, 3]  # Active 13D axis keys (4-9)
        self.hyper_scale = 1.0
        self.time = 0.0

        # Event Key Bindings for VR / Keyboard Stepping
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax.set_axis_off()
        self.fig.canvas.manager.set_window_title('Universal Matrix - VR 13D 14-Layer Torus Space')

    def on_key_press(self, event):
        if event.key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            val = int(event.key)
            if val <= 3:
                self.active_layer = val
            else:
                self.active_dims = [(val + i) % 13 for i in range(4)]
        elif event.key == 'up':
            self.active_layer = min(14, self.active_layer + 1)
        elif event.key == 'down':
            self.active_layer = max(0, self.active_layer - 1)
        elif event.key == 'q':
            self.hyper_scale *= 1.15
        elif event.key == 'e':
            self.hyper_scale /= 1.15

    def _generate_13d_torus_layer(self, layer_idx):
        phi_scale = (PHI ** (layer_idx / 4.0)) * self.hyper_scale
        R, r = 0.6 * phi_scale, 0.22 * phi_scale
        
        nodes_13d = []
        for i in range(self.core_nodes // 2):
            theta = 2 * np.pi * i / (self.core_nodes // 2)
            phi = 2 * np.pi * ((i * 2) % (self.core_nodes // 2)) / (self.core_nodes // 2)
            
            x = (R + r * np.cos(phi)) * np.cos(theta)
            y = (R + r * np.cos(phi)) * np.sin(theta)
            z = r * np.sin(phi)
            
            vec_13d = [0.0] * 13
            vec_13d[0], vec_13d[1], vec_13d[2] = x, y, z
            for d in range(3, 13):
                vec_13d[d] = 0.05 * np.sin(theta * (d + 1))
            nodes_13d.append(vec_13d)
            
        return np.array(nodes_13d)

    def _apply_13d_rotations(self, nodes_13d, t):
        rotated = nodes_13d.copy()
        d1, d2 = self.active_dims[0], self.active_dims[1]
        c, s = np.cos(t), np.sin(t)
        
        x1, x2 = rotated[:, d1].copy(), rotated[:, d2].copy()
        rotated[:, d1] = x1 * c - x2 * s
        rotated[:, d2] = x1 * s + x2 * c
        return rotated

    def _get_quantum_states(self, flux_val):
        if hasattr(self.quantum_engine, 'run_superposition_cascade'):
            return self.quantum_engine.run_superposition_cascade(flux_input=flux_val)
        elif hasattr(self.quantum_engine, 'simulate_superposition'):
            return self.quantum_engine.simulate_superposition(flux_input=flux_val)
        elif hasattr(self.quantum_engine, 'step'):
            return self.quantum_engine.step()
        else:
            return getattr(self.quantum_engine, 'state', {i: 1.0 / 114 for i in range(114)})

    def animate(self, frame):
        self.ax.clear()
        self.ax.set_axis_off()
        self.time += 0.03
        
        q_states = self._get_quantum_states(np.sin(self.time))
        self.ax.view_init(elev=20 + 10 * np.sin(self.time * 0.3), azim=frame * 0.5)

        render_layers = range(1, 15) if self.active_layer == 0 else [self.active_layer]

        for layer in render_layers:
            raw_13d = self._generate_13d_torus_layer(layer - 1)
            rot_13d = self._apply_13d_rotations(raw_13d, self.time * (1.0 + layer * 0.03))
            
            coords_3d = rot_13d[:, :3]
            alpha_layer = 0.9 if self.active_layer == layer else max(0.1, 0.4 - (layer * 0.02))
            
            colors, sizes = [], []
            for idx, pt in enumerate(coords_3d):
                node_id = (idx + layer * 7) % self.total_nodes
                prob = q_states[node_id] if isinstance(q_states, dict) and node_id in q_states else 0.01
                if (node_id + 1) % 3 == 0:
                    colors.append('#FF0055')
                    sizes.append(50 + prob * 100)
                else:
                    colors.append('#0088FF')
                    sizes.append(15 + prob * 50)
                    
            self.ax.scatter(coords_3d[:, 0], coords_3d[:, 1], coords_3d[:, 2], 
                            c=colors, s=sizes, alpha=alpha_layer, edgecolors='white', linewidths=0.2)

        focus_str = f'LAYER {self.active_layer} FOCUS' if self.active_layer > 0 else 'ALL 14 LAYERS ACTIVE'
        self.ax.set_title(f'VR 13D SPACE | {focus_str} | Controls: 4-9 (13D Planes), Q/E (Scale), UP/DN (Step Layers)', 
                          color='white', fontsize=10, pad=10)

    def run(self):
        anim = FuncAnimation(self.fig, self.animate, frames=720, interval=25, blit=False)
        plt.show()

if __name__ == '__main__':
    space = VR13DTorusSpace()
    space.run()
    
    import numpy as np
import torch
from src.russell_periodic_mapper import RussellPeriodicEngine

class VR13DSpatialEngine:
    """
    13-Dimensional Spatial Projection Engine rendering 14 nested Toroidal planes
    mapped dynamically to Walter Russell's periodic elemental frequencies.
    """
    def __init__(self, num_nodes=114, dim=13):
        self.num_nodes = num_nodes
        self.dim = dim
        self.russell_engine = RussellPeriodicEngine(base_freq=432.0)
        self.node_mappings = self.russell_engine.map_matrix_nodes_to_periodic_grid(num_nodes)
        self.active_layer = 0  # 0 = All 14 Layers, 1-14 = Specific Torus Focus

    def get_layer_spatial_transform(self, layer_idx: int):
        """
        Derives gyroscopic rotation tensors and element color palettes
        based on active Torus Layer T_1 -> T_14.
        """
        # Map Torus Layer focus to atomic element scale
        z_target = max(1, min(118, layer_idx * 8))
        elem_props = self.russell_engine.calculate_element_properties(z_target)
        
        tilt_deg = elem_props["gyroscopic_tilt_deg"]
        freq_hz = elem_props["resonant_frequency_hz"]
        
        # Color spectrum shifting based on gyroscopic tilt (0 deg = Cyan, 90 deg = Crimson Peak)
        tilt_factor = tilt_deg / 90.0
        color_rgb = (
            float(tilt_factor),                  # Red channel (peaks at 90 deg Carbon)
            float(1.0 - abs(tilt_factor - 0.5)), # Green channel
            float(1.0 - tilt_factor)             # Blue channel (peaks at 0 deg Inert)
        )

        return {
            "layer_idx": layer_idx,
            "gyroscopic_tilt_deg": tilt_deg,
            "resonant_frequency_hz": freq_hz,
            "element_classification": elem_props["classification"],
            "color_rgb": color_rgb
        }

    def render_13d_to_vr_mesh(self, state_matrix: torch.Tensor):
        """
        Projects 13D SO(13) Givens rotation state vectors down to 3D Cartesian VR coordinates,
        weighted by active layer gyroscopic tilt angles.
        """
        if isinstance(state_matrix, torch.Tensor):
            state_np = state_matrix.cpu().numpy() if state_matrix.is_cuda else state_matrix.numpy()
        else:
            state_np = np.array(state_matrix)

        # 13D -> 3D Stereographic Projection Kernel
        coords_3d = state_np[:, :3] / (1.0 + np.abs(state_np[:, 3:4]))
        
        frame_data = []
        for i in range(min(len(coords_3d), self.num_nodes)):
            node_info = self.node_mappings[i]
            frame_data.append({
                "node_id": i,
                "position": coords_3d[i].tolist() if i < len(coords_3d) else [0.0, 0.0, 0.0],
                "tilt_deg": node_info.get("gyroscopic_tilt_deg", 0.0),
                "freq_hz": node_info.get("resonant_frequency_hz", 432.0),
                "type": node_info.get("node_type", "Internal Vortex Core")
            })

        return frame_data

import numpy as np
import torch
from src.russell_periodic_mapper import RussellPeriodicEngine
from src.dna_bio_mapper import DNABioMapper

class VR13DSpatialEngine:
    """
    13-Dimensional Spatial Projection Engine rendering 14 nested Toroidal planes
    mapped dynamically to Walter Russell's periodic elemental frequencies and DNA biological meshes.
    """
    def __init__(self, num_nodes=114, dim=13):
        self.num_nodes = num_nodes
        self.dim = dim
        self.russell_engine = RussellPeriodicEngine(base_freq=432.0)
        self.dna_mapper = DNABioMapper(base_freq=432.0)
        self.node_mappings = self.russell_engine.map_matrix_nodes_to_periodic_grid(num_nodes)
        self.active_layer = 0  # 0 = All 14 Layers, 8 = DNA/Biological Layer Focus

    def get_layer_spatial_transform(self, layer_idx: int):
        """
        Derives gyroscopic rotation tensors and element color palettes
        based on active Torus Layer T_1 -> T_14.
        """
        z_target = max(1, min(118, layer_idx * 8))
        elem_props = self.russell_engine.calculate_element_properties(z_target)
        
        tilt_deg = elem_props["gyroscopic_tilt_deg"]
        freq_hz = elem_props["resonant_frequency_hz"]
        
        tilt_factor = tilt_deg / 90.0
        color_rgb = (
            float(tilt_factor),
            float(1.0 - abs(tilt_factor - 0.5)),
            float(1.0 - tilt_factor)
        )

        return {
            "layer_idx": layer_idx,
            "gyroscopic_tilt_deg": tilt_deg,
            "resonant_frequency_hz": freq_hz,
            "element_classification": elem_props["classification"],
            "color_rgb": color_rgb
        }

    def render_dna_sequence_mesh(self, dna_sequence: str):
        """
        Renders a genetic sequence as a 3D stereographic double-helix mesh
        focused on Torus Layer 8 (Biological Crystallography).
        """
        tensor_13d = self.dna_mapper.sequence_to_13d_tensor(dna_sequence)
        seq_clean = dna_sequence.upper()
        
        mesh_nodes = []
        for idx, base in enumerate(seq_clean):
            base_info = self.dna_mapper.map_base_to_frequency(base)
            pos_3d = tensor_13d[idx, :3].tolist()
            
            # Hydrogen bond color signature: 2 bonds = Cyan/Blue, 3 bonds = Crimson/Red
            bonds = base_info["hydrogen_bonds"]
            color_rgb = (1.0, 0.2, 0.2) if bonds == 3 else (0.2, 0.8, 1.0)
            
            mesh_nodes.append({
                "sequence_index": idx,
                "base": base,
                "position": pos_3d,
                "hydrogen_bonds": bonds,
                "frequency_hz": base_info["weighted_frequency_hz"],
                "color_rgb": color_rgb,
                "target_layer": 8
            })

        return {
            "active_layer": 8,
            "sequence_length": len(seq_clean),
            "mesh_nodes": mesh_nodes
        }

    def render_13d_to_vr_mesh(self, state_matrix: torch.Tensor):
        if isinstance(state_matrix, torch.Tensor):
            state_np = state_matrix.cpu().numpy() if state_matrix.is_cuda else state_matrix.numpy()
        else:
            state_np = np.array(state_matrix)

        coords_3d = state_np[:, :3] / (1.0 + np.abs(state_np[:, 3:4]))
        
        frame_data = []
        for i in range(min(len(coords_3d), self.num_nodes)):
            node_info = self.node_mappings[i]
            frame_data.append({
                "node_id": i,
                "position": coords_3d[i].tolist() if i < len(coords_3d) else [0.0, 0.0, 0.0],
                "tilt_deg": node_info.get("gyroscopic_tilt_deg", 0.0),
                "freq_hz": node_info.get("resonant_frequency_hz", 432.0),
                "type": node_info.get("node_type", "Internal Vortex Core")
            })

        return frame_data