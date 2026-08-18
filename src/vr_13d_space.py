#!/usr/bin/env python3
"""
Universal Field Engine — 13-Dimensional Spatial Projection (v6.0 Peer-Review Standard)
Anchored directly to the 64-bit integer invariants and alpha_geometric constraints.
"""

import sys
import os
import math
import numpy as np
from ursina import *

# Ensure local imports locate calculator dependencies cleanly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    from calculator import STREAM_UP, STREAM_DOWN, DELTA_S, ALPHA_GEOMETRIC
except ImportError:
    # Strict fallback initializations matching Section V register invariants if run standalone
    STREAM_UP = int("0000000000000000000000000000000000000111010110111100110100010101", 2)
    STREAM_DOWN = int("0000000000000000000000000000000000111010110111100110100010110001", 2)
    DELTA_S = STREAM_DOWN - STREAM_UP
    ALPHA_GEOMETRIC = 1.0 / (54.0 * (math.pi ** 2))

class Space13DVR(Ursina):
    def __init__(self):
        super().__init__(title="Universal Field Engine — 13-Dimensional Spatial Projection", vsync=True)
        
        # Configure deep-space visual profile
        Sky(color=color.black)
        window.fps_counter.enabled = True
        self.player = EditorCamera()
        self.player.position = (0, 0, -5)

        # Initialize tracking matrices
        self.node_entities = []
        self.rotation_matrix_13d = np.eye(13)  # Start with an unrotated 13D Identity Matrix
        self.active_dimension_dial = 3         # Default higher dimension control focus
        self.base_angle = 0.0

        print("🧠 Synthesizing 13-Dimensional Hyper-Node Vector Space from 64-Bit Bitmasks...")
        self.generate_and_project_13d_matrix()
        print("🟢 13D VR Engine Active! Use numbers 4-9 to select a higher dimension, and hold 'Q'/'E' to rotate it.")

    def generate_and_project_13d_matrix(self):
        """
        Generates nodes based on discrete bit patterns in a 13-dimensional vector space,
        applies a full 13D rotation tensor, and cascades the projection down using ALPHA_GEOMETRIC.
        """
        # Clear out old entities to redraw the spatial coordinates
        for entity in self.node_entities:
            destroy(entity)
        self.node_entities.clear()

        # Generate a balanced distribution governed by 64-bit integer register patterns
        for i in range(114):
            # Programmatically extract local node-bit states to drive deterministic initialization
            # Bitwise isolation masks determine discrete structural distribution vectors
            bit_shift_offset = (i * 7) % 64
            up_bit = (STREAM_UP >> bit_shift_offset) & 1
            down_bit = (STREAM_DOWN >> bit_shift_offset) & 1
            delta_bit = (DELTA_S >> bit_shift_offset) & 1

            # Base phase distributions bound to vortex constants
            phi = math.acos(1 - 2 * (i + 0.5) / 114)
            theta = math.pi * (1.0 + math.sqrt(5.0)) * i
            
            # Construct coordinate values for all 13 dimensions from register footprints
            vec_13d = np.zeros(13)
            for d in range(13):
                # Integer bit modulation step ensures base-independent spatial seeding
                bit_mod_weight = 1.0 + (up_bit * 0.1) - (down_bit * 0.1) + (delta_bit * 0.05)
                phasing_factor = (i * (d + 1) * 137.5) * (math.pi / 180.0) * bit_mod_weight
                
                if d % 2 == 0:
                    vec_13d[d] = math.sin(phi) * math.cos(theta + phasing_factor)
                else:
                    vec_13d[d] = math.cos(phi) * math.sin(phasing_factor)

            # Apply our active 13-dimensional rotation tensor matrix
            rotated_vec_13d = np.dot(self.rotation_matrix_13d, vec_13d)

            # Cascade Projection: Repeatedly project from 13D -> 12D -> 11D ... down to 3D
            # Each cascade layer uses ALPHA_GEOMETRIC to systematically scale spatial attenuation
            current_vector = rotated_vec_13d
            for d in range(12, 2, -1):
                # Stereographic projection step bounded by the geometric compression loop limit
                scale_weight = 1.0 / (2.0 - current_vector[d])
                current_vector = current_vector[:d] * scale_weight * (ALPHA_GEOMETRIC * 16.5)

            # Extract renderable 3D Cartesian coordinates cleanly via absolute array indexing
            x_3d = current_vector[0]
            y_3d = current_vector[1]
            z_3d = current_vector[2]

            # Differentiate the 3-6-9 control vectors visually (Symmetry Tracking)
            if i % 3 == 0:
                node_color = color.crimson
                node_scale = 0.12
            else:
                node_color = color.azure
                node_scale = 0.06

            # Render the 13D slice as an interactive node inside the VR view space
            node = Entity(
                model='sphere',
                color=node_color,
                scale=node_scale,
                position=(x_3d, y_3d, z_3d)
            )
            self.node_entities.append(node)

    def apply_higher_dimensional_rotation(self, dim_a, dim_b, angle_rad):
        """Constructs a precise localized 13D Givens rotation matrix frame."""
        g_rot = np.eye(13)
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        g_rot[dim_a, dim_a] = c
        g_rot[dim_a, dim_b] = -s
        g_rot[dim_b, dim_a] = s
        g_rot[dim_b, dim_b] = c
        # Update the main system matrix tensor over time
        self.rotation_matrix_13d = np.dot(self.rotation_matrix_13d, g_rot)

    def update(self):
        """Continuous input polling loop executed every frame."""
        # 1. Listen for user picking which higher dimension they want to manipulate
        for num in range(4, 10):
            if held_keys[str(num)]:
                self.active_dimension_dial = num - 1
                print(f"🎯 Selected Higher Dimension Axis: {num}")

        # 2. Rotate the selected higher-dimensional axis when Q or E are held
        rotation_triggered = False
        if held_keys['e']:
            self.apply_higher_dimensional_rotation(0, self.active_dimension_dial, time.dt * 0.5)
            rotation_triggered = True
        if held_keys['q']:
            self.apply_higher_dimensional_rotation(0, self.active_dimension_dial, -time.dt * 0.5)
            rotation_triggered = True

        # Redraw the system layout only if a higher spatial vector shifted
        if rotation_triggered:
            self.generate_and_project_13d_matrix()

        # Apply a gentle baseline spin to the standard 3D viewing box over time
        self.base_angle += time.dt * 5
        for entity in self.node_entities:
            entity.rotation_y = self.base_angle

if __name__ == "__main__":
    app = Space13DVR()
    app.run()
