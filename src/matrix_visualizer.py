import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import calculator as mc
from lattice_quantum_engine import LatticeQuantumEngine

class Nested14TorusQuantumVisualizer:
    def __init__(self):
        self.fig = plt.figure(figsize=(14, 10), facecolor='black')
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='black')
        self.total_nodes = mc.TOTAL_NODES
        self.core_nodes = mc.N_CORE
        
        # Instantiate Quantum Engine for Live Wave-Function Collapse Data
        self.quantum_engine = LatticeQuantumEngine()
        
        # Build 14 Nested Torus Shells
        self.num_layers = 14
        self.time = 0.0
        
        self.ax.set_axis_off()
        self.fig.canvas.manager.set_window_title('Universal Matrix - 14-Layer Fractal Torus & Quantum Lattice Visualizer')

    def _generate_nested_layer_nodes(self, layer_idx, time_shift):
        # Scale radii geometrically across 14 nested layers
        phi_scale = mc.GOLDEN_RATIO_RESONANCE ** (layer_idx / 4.0)
        R = 0.5 * phi_scale
        r = 0.18 * phi_scale
        
        coords = []
        nodes_per_layer = self.core_nodes // 2  # Distribution across layers
        
        for i in range(nodes_per_layer):
            theta = 2 * np.pi * i / nodes_per_layer + (layer_idx * 0.1) + time_shift
            phi = 2 * np.pi * ((i * 2) % nodes_per_layer) / nodes_per_layer + (layer_idx * 0.05)
            
            x = (R + r * np.cos(phi)) * np.cos(theta)
            y = (R + r * np.cos(phi)) * np.sin(theta)
            z = r * np.sin(phi)
            coords.append([x, y, z])
            
        return np.array(coords)

    def animate(self, frame):
        self.ax.clear()
        self.ax.set_axis_off()
        self.time += 0.02
        
        # Run Quantum Wave-Function Superposition & Collapse
        q_states = self.quantum_engine.run_superposition_cascade(flux_input=np.sin(self.time))
        
        # Dynamic Camera Orbit
        self.ax.view_init(elev=20 + 10 * np.sin(self.time * 0.4), azim=frame * 0.4)
        
        # Render 14 Concentric Torus Shells
        for layer in range(self.num_layers):
            layer_nodes = self._generate_nested_layer_nodes(layer, self.time * (1.0 + layer * 0.05))
            
            # Layer Wireframe Ring Visualization
            alpha_layer = max(0.05, 0.35 - (layer * 0.02))
            
            # Determine Node Colors & Probability Sizes from Quantum Engine
            colors = []
            sizes = []
            for idx, pt in enumerate(layer_nodes):
                node_id = (idx + layer * 7) % self.total_nodes
                prob = q_states[node_id] if node_id < len(q_states) else 0.01
                
                if (node_id + 1) % 3 == 0:
                    colors.append('#FF0055')  # 3-6-9 Tesla Controls (Crimson)
                    sizes.append(40 + prob * 120)
                else:
                    colors.append('#0088FF')  # Material Infinity Circuit (Royal Blue)
                    sizes.append(10 + prob * 60)
            
            # Scatter Plot for current Torus Layer
            x, y, z = layer_nodes[:, 0], layer_nodes[:, 1], layer_nodes[:, 2]
            self.ax.scatter(x, y, z, c=colors, s=sizes, alpha=alpha_layer + 0.3, edgecolors='white', linewidths=0.1)
            
            # Render Inter-Layer Doubling Vectors
            if layer < self.num_layers - 1:
                step = max(1, len(layer_nodes) // 6)
                for v in range(0, len(layer_nodes), step):
                    p1 = layer_nodes[v]
                    p2 = layer_nodes[(v * 2) % len(layer_nodes)]
                    self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 
                                 color='#FF0055' if v % 3 == 0 else '#0044AA', 
                                 alpha=alpha_layer, linewidth=0.5)

        # Plot Outer Hypercube Gate Face Nodes (Nodes 108-113)
        gate_dist = 4.5
        gates = np.array([
            [gate_dist, 0, 0], [-gate_dist, 0, 0],
            [0, gate_dist, 0], [0, -gate_dist, 0],
            [0, 0, gate_dist], [0, 0, -gate_dist]
        ])
        
        self.ax.scatter(gates[:, 0], gates[:, 1], gates[:, 2], c='#00FFFF', s=120, marker='s', alpha=0.9, label='External Gates')
        for g in gates:
            self.ax.plot([0, g[0]], [0, g[1]], [0, g[2]], color='#00FFFF', alpha=0.12, linestyle='--')

        self.ax.set_title(f'14-LAYER FRACTAL TORUS FIELD | Quantum Cascade Active | Time: {self.time:.2f}s', color='white', fontsize=11, pad=10)

    def run(self):
        anim = FuncAnimation(self.fig, self.animate, frames=720, interval=30, blit=False)
        plt.show()

if __name__ == '__main__':
    vis = Nested14TorusQuantumVisualizer()
    vis.run()
