"""
The Universal Playing Field - Matrix Visualizer v4.0
Generates the geometric 114-node vector mapping and Tesla 3-6-9 triads.
Visually charts the discrete doubling circuit and control nodes around the origin.

License: GNU Affero General Public License v3 (AGPL-3.0)
Copyright (c) 2026 Waters Legacy Trust. All Rights Reserved.
"""

import numpy as np
import matplotlib.pyplot as plt

def get_node_coordinates(num_nodes=114):
    """Calculates (x, y) coordinates for nodes evenly spaced around a circle."""
    angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)
    # Rotating by pi/2 so node 1 starts at the absolute top of the field
    x = np.sin(angles)
    y = np.cos(angles)
    return x, y

def digital_root(n):
    """Calculates the digital root (vortex math reduction) of a node number."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9

def plot_vortex_114():
    num_nodes = 114
    x, y = get_node_coordinates(num_nodes)
    
    plt.figure(figsize=(12, 12), facecolor='#0d1117') # Matching GitHub dark theme
    ax = plt.axes()
    ax.set_facecolor('#0d1117')
    
    # 1. Plot the 114 absolute matrix coordinates
    plt.scatter(x, y, color='#ffffff', s=20, zorder=3, alpha=0.8)
    
    # 2. Draw active vector connections based on Vortex Math principles
    for i in range(num_nodes):
        node_num = i + 1
        # Modular doubling rule across the 114 network perimeter
        target_node = (node_num * 2) % num_nodes
        if target_node == 0:
            target_node = num_nodes
        
        start_idx = node_num - 1
        end_idx = target_node - 1
        
        # Isolate the 3-6-9 Tesla control vectors from the material doubling track
        d_root = digital_root(node_num)
        if d_root in[3, 6, 9]:
            color = '#ff3366'      # Crimson: Higher dimensional control triad
            linewidth = 1.2
            alpha = 0.7
        else:
            color = '#388bfd'      # Royal Blue: Material infinity/doubling circuit
            linewidth = 0.6
            alpha = 0.4
            
        plt.plot([x[start_idx], x[end_idx]], [y[start_idx], y[end_idx]], 
                 color=color, alpha=alpha, linewidth=linewidth, zorder=2)

    # 3. Label key node pathways cleanly to track vector flow
    for i in range(0, num_nodes, 6): # Every 6th node to align with the 6 outer gate faces
        plt.text(x[i] * 1.07, y[i] * 1.07, str(i + 1), 
                 color='#c9d1d9', fontsize=10, ha='center', va='center', weight='bold')

    plt.title("The Universal Playing Field: 114-Node Vortex Matrix Grid", color='#ffffff', fontsize=16, pad=20, weight='bold')
    plt.axis('equal')
    plt.axis('off')
    
    print("[SYSTEM] Vector grid calculated successfully. Rendering 114-node field canvas...")
    plt.show()

if __name__ == "__main__":
    plot_vortex_114()
