#!/usr/bin/env python3
"""
Universal Playing Field: Interactive 3D Spatial Visualizer (v5.0 Core Spec)
Renders the 114-node ring topology, counter-rotating vector loops, 
6-node hypercube boundary cage, and live interactive Axiom VI macro-flux controls.
"""

import math
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# Ensure local path can import the verified matrix core cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL ERROR: 'calculator.py' must be present in the same directory.")
    sys.exit(1)


class MatrixVisualizer:
    def __init__(self):
        # Establish base spatial geometry projections (in mm)
        self.major_radius = 40.0
        self.minor_radius = 12.0
        
        # Pull parameters directly from your verified calculator
        self.total_nodes = mc.M_TOTAL          # 114 Nodes
        self.singularity_axis = mc.S_AXIS      # 9 Axis
        self.boundary_count = mc.B_BOUNDARY  # 6 Face Gates
        
        # Track active runtime variables
        self.current_psi = 13.5               # Starting baseline macro-flux
        self.rotation_phase = 0.0             # Continuous animation ticker
        
    def _calculate_node_coordinates(self, index, psi_val, phase_offset=0.0):
        """
        Projects discrete matrix indices onto a continuous 3D toroidal spatial manifold,
        dynamically factoring in Axiom VI macro-flux scaling contractions.
        """
        # Calculate angular trace stepping around the major circumference ring
        theta = (2.0 * math.pi * index) / self.total_nodes + phase_offset
        
        # Calculate localized internal winding rotation using the 3-6-9 frequency axis
        phi = (2.0 * math.pi * (index * self.singularity_axis)) / mc.N_CORE
        
        # Process live Axiom VI structural contribution as an atmospheric scaling modifier
        _, ext_contrib = mc.calculate_axiom_6(psi_val)
        dynamic_dilation = 1.0 + (ext_contrib / 100.0)
        
        # Parametric spatial equations modified by live external flux pressure
        x = (self.major_radius + self.minor_radius * math.cos(phi) * dynamic_dilation) * math.cos(theta)
        y = (self.major_radius + self.minor_radius * math.cos(phi) * dynamic_dilation) * math.sin(theta)
        z = self.minor_radius * math.sin(phi) * dynamic_dilation
        
        return x, y, z

    def launch_visualizer(self):
        """Initializes the matplotlib interactive window canvas and widget loops."""
        # Set up a dark, modern space themed visualization frame
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        fig.canvas.manager.set_window_title('Universal Playing Field: Node Visualizer v5.0')
        
        # Adjust main canvas boundaries to leave dedicated clean space for the UI sliders
        plt.subplots_adjust(bottom=0.2)
        
        # Define graphic handles for live data tracking updates
        self.scatter_inward = ax.scatter([], [], [], c='cyan', s=25, label='Inward Compression (-) [54 Nodes]', depthshade=True)
        self.scatter_outward = ax.scatter([], [], [], c='crimson', s=25, label='Outward Expansion (+) [54 Nodes]', depthshade=True)
        self.scatter_gates = ax.scatter([], [], [], c='yellow', s=120, marker='H', label='Hypercube Face Gate [6 Nodes]', edgecolors='white')
        self.cage_lines, = ax.plot([], [], [], c='orange', linestyle=':', alpha=0.6, label='Boundary Container Shield')

        # Configuration logic for axes styling constraints
        ax.set_xlim(-60, 60)
        ax.set_ylim(-60, 60)
        ax.set_zlim(-30, 30)
        ax.set_xlabel('Spatial Axis X (mm)', color='gray')
        ax.set_ylabel('Spatial Axis Y (mm)', color='gray')
        ax.set_zlabel('Spatial Axis Z (mm)', color='gray')
        ax.set_title('Interactive 114-Node Grid Topology (v5.0 Core Framework)', fontsize=14, pad=20, color='white')
        ax.legend(loc='upper right', framealpha=0.2)
        ax.grid(True, alpha=0.1)

        # Create an interactive UI slider panel beneath the main graphic area
        ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor='#222222')
        psi_slider = Slider(ax_slider, 'Macro-Flux (Psi)', 0.0, 100.0, valinit=self.current_psi, valfmt='%1.1f Psi', color='orange')

        def on_slider_change(val):
            """Updates internal target framework pressure when user slides the controller."""
            self.current_psi = val

        psi_slider.on_changed(on_slider_change)

        def update_animation_frame(frame):
            """Core rendering loop logic executed on every ticks refresh step."""
            # Increment spatial rotation velocity angle to visualize counter-rotations
            self.rotation_phase += 0.015
            
            inward_x, inward_y, inward_z = [], [], []
            outward_x, outward_y, outward_z = [], [], []
            gate_x, gate_y, gate_z = [], [], []

            # Process coordinates for every individual slot on the 114 node grid
            for i in range(self.total_nodes):
                # Check for 6-node hypercube boundary face matches
                is_boundary_gate = (i % (self.total_nodes / self.boundary_count)) == 0
                
                if is_boundary_gate:
                    # Anchor the 6 external boundary box nodes firmly in absolute position slots
                    x, y, z = self._calculate_node_coordinates(i, self.current_psi, phase_offset=0.0)
                    gate_x.append(x)
                    gate_y.append(y)
                    gate_z.append(z)
                else:
                    # Even node indices represent our internal inward electric compression tracks
                    if i % 2 == 0:
                        x, y, z = self._calculate_node_coordinates(i, self.current_psi, phase_offset=-self.rotation_phase)
                        inward_x.append(x)
                        inward_y.append(y)
                        inward_z.append(z)
                    # Odd node indices represent our internal outward electromagnetic expansion tracks
                    else:
                        x, y, z = self._calculate_node_coordinates(i, self.current_psi, phase_offset=self.rotation_phase)
                        outward_x.append(x)
                        outward_y.append(y)
                        outward_z.append(z)

            # Update live point locations across the screen graphics pipeline
            self.scatter_inward._offsets3d = (inward_x, inward_y, inward_z)
            self.scatter_outward._offsets3d = (outward_x, outward_y, outward_z)
            self.scatter_gates._offsets3d = (gate_x, gate_y, gate_z)
            
            # Connect the 6 external boundary nodes to form a geometric shield ring cage box
            if gate_x:
                closed_cage_x = gate_x + [gate_x[0]]
                closed_cage_y = gate_y + [gate_y[0]]
                closed_cage_z = gate_z + [gate_z[0]]
                self.cage_lines.set_data(closed_cage_x, closed_cage_y)
                self.cage_lines.set_3d_properties(closed_cage_z)

            # Keep the 3D viewing perspective slowly drifting for maximum structural depth perception
            ax.view_init(elev=25 + 5 * math.sin(self.rotation_phase * 0.5), azim=frame * 0.2)
            return self.scatter_inward, self.scatter_outward, self.scatter_gates, self.cage_lines

        # Anchor animation loop tracking constraints
        anim = FuncAnimation(fig, update_animation_frame, interval=20, blit=False, cache_frame_data=False)
        plt.show()


def main():
    visualizer = MatrixVisualizer()
    visualizer.launch_visualizer()


if __name__ == '__main__':
    main()
