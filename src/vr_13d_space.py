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
    