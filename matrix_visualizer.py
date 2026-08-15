"""
"""
The Universal Playing Field - Real-Time Matrix Visualizer v4.1
Generates an active, sequential vector path animation mapping the 114-node origin.

Isolates the 3-6-9 structural control vectors dynamically from the material track.
License: GNU Affero General Public License v3 (AGPL-3.0)
Copyright (c) 2026 Waters Legacy Trust. All Rights Reserved.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def get_node_coordinates(num_nodes=114):
    """Calculates absolute (x, y) coordinates for nodes evenly spaced on a circle perimeter."""
    angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)
    # Rotate by pi/2 so node 1 starts at the absolute top vertical axis
    x = np.sin(angles)
    y = np.cos(angles)
    return x, y

def digital_root(n):
    """Calculates the digital root reduction (vortex arithmetic index)."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9

def build_vector_manifest(num_nodes=114):
    """Pre-computes and segregates all vector tracks to feed the animation engine sequential indices."""
    material_tracks = []
    control_tracks = []
    
    for i in range(num_nodes):
        node_num = i + 1
        target_node = (node_num * 2) % num_nodes
        if target_node == 0:
            target_node = num_nodes
            
        start_idx = node_num - 1
        end_idx = target_node - 1
        d_root = digital_root(node_num)
        
        vector_data = (start_idx, end_idx)
        if d_root in (3, 6, 9):
            control_tracks.append(vector_data)
        else:
            material_tracks.append(vector_data)
            
    # Sequential execution path: material infinity circuit renders first, then 3-6-9 control vectors
    return material_tracks + control_tracks, len(material_tracks)

def animate_matrix():
    num_nodes = 114
    x, y = get_node_coordinates(num_nodes)
    all_vectors, split_index = build_vector_manifest(num_nodes)
    
    fig = plt.figure(figsize=(12, 12), facecolor='#0d1117') # Clean GitHub dark theme UI
    ax = plt.axes()
    ax.set_facecolor('#0d1117')
    
    # Render static background node coordinates
    ax.scatter(x, y, color='#ffffff', s=25, zorder=3, alpha=0.9, edgecolors='#388bfd', linewidths=0.5)
    
    # Every 6th node text mapping alignment coordinate cleanly around the boundary faces
    for i in range(0, num_nodes, 6):
        ax.text(x[i] * 1.08, y[i] * 1.08, str(i + 1), 
                color='#c9d1d9', fontsize=10, ha='center', va='center', weight='bold')
                
    # Place placeholders for lines to feed frame adjustments dynamically
    lines = []
    for idx, (start, end) in enumerate(all_vectors):
        if idx < split_index:
            color, lw, alpha = '#388bfd', 0.8, 0.45  # Royal Blue Material Track
        else:
            color, lw, alpha = '#ff3366', 1.5, 0.85  # Crimson Tesla Control Loops
            
        ln, = ax.plot([], [], color=color, linewidth=lw, alpha=alpha, zorder=2)
        lines.append(ln)

    ax.set_title("The Universal Playing Field: Real-Time 114-Node Grid Construction", 
                 color='#ffffff', fontsize=15, pad=25, weight='bold')
    plt.axis('equal')
    plt.axis('off')
    
    def init():
        """Initializes empty canvas segments."""
        for ln in lines:
            ln.set_data([], [])
        return lines

    def update(frame):
        """Sequentially triggers visibility line segments frame-by-frame."""
        start_idx, end_idx = all_vectors[frame]
        lines[frame].set_data([x[start_idx], x[end_idx]], [y[start_idx], y[end_idx]])
        return lines

    print("[SYSTEM] Compiling computational coordinate map loops...")
    print(f"[SYSTEM] Total rendering sequence: {len(all_vectors)} discrete path vector transformations.")
    
    # Blit=True handles raw frame buffers dynamically for smooth local refresh processing loops
    ani = animation.FuncAnimation(fig, update, init_func=init, frames=len(all_vectors), 
                                  interval=45, blit=True, repeat=True)
    plt.show()

if __name__ == "__main__":
    animate_matrix()
