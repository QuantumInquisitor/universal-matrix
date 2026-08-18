#!/usr/bin/env python3
"""
Universal Playing Field: Discrete Geodesic Orbit Propagator & Decay Simulator
Models the dynamic trajectory and orbital decay of a particle traversing
the discrete 114-node spatial lattice gradient without assuming a gravity force.
"""

import sys
import os
import math
import json

# Ensure local library paths route cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL: 'calculator.py' must be present in the same directory.")
    sys.exit(1)


class GeodesicSimulator:
    def __init__(self, time_step=0.01):
        """Initializes system invariants and the configuration metrics matrix."""
        self.total_nodes = mc.M_TOTAL          # 114 Target Grid Base
        self.time_step = time_step
        self.alpha = mc.ALPHA_GEOMETRIC        # Invariant spatial scale factor
        
        # Load baseline dimensions matching config layer standards
        self.major_radius = 50.0
        self.minor_radius = 15.0

    def _get_node_potential(self, node_id: int) -> float:
        """Calculates localized field potential from active 64-bit hardware bitmasks."""
        bit_offset = (node_id * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_offset) & 1
        
        # Enforce 3-6-9 frequency scaling multipliers
        vortex_scale = 3.0 if node_id % 3 == 0 else (6.0 if node_id % 6 == 0 else 1.0)
        if node_id % 9 == 0: vortex_scale = 9.0
        
        # Combine states with the exact alpha geometric scaling coefficient
        potential = (up_bit * 2.0 - down_bit * 0.5) * self.alpha * vortex_scale
        return float(potential)

    def _find_nearest_lattice_node(self, x: float, y: float, z: float) -> int:
        """Snaps continuous 3D coordinates back to the closest discrete node ID (0-113)."""
        best_node = 0
        min_distance = float('inf')
        
        for node_id in range(self.total_nodes):
            # Basic geometric torus projection approximation tracking
            theta = (2.0 * math.pi * node_id) / self.total_nodes
            phi = (2.0 * math.pi * (node_id * mc.S_AXIS)) / mc.N_CORE
            
            tx = (self.major_radius + self.minor_radius * math.cos(phi)) * math.cos(theta)
            ty = (self.major_radius + self.minor_radius * math.cos(phi)) * math.sin(theta)
            tz = self.minor_radius * math.sin(phi)
            
            dist = math.sqrt((x - tx)**2 + (y - ty)**2 + (z - tz)**2)
            if dist < min_distance:
                min_distance = dist
                best_node = node_id
                
        return best_node

    def propagate_orbit(self, steps=100, init_pos=(50.0, 0.0, 15.0), init_vel=(0.0, 120.0, 0.0)) -> dict:
        """Simulates path trajectories and tracking logs as orbital degradation occurs."""
        px, py, pz = init_pos
        vx, vy, vz = init_vel
        
        trajectory_log = []
        
        for step in range(steps):
            # Step 1: Identify which discrete frequency gate the object is flying through
            current_node = self._find_nearest_lattice_node(px, py, pz)
            potential = self._get_node_potential(current_node)
            
            # Step 2: Compute particle drift vectors directed toward the zero-point center
            r = math.sqrt(px**2 + py**2 + pz**2)
            if r == 0: r = 1.0
            
            # Acceleration is dictated strictly by register bits and alpha metrics
            accel_magnitude = (potential / (r**2)) * 1000.0
            ax = -(px / r) * accel_magnitude
            ay = -(py / r) * accel_magnitude
            az = -(pz / r) * accel_magnitude
            
            # Step 3: Implement discrete quantum decay coefficients (Relativistic Decay Metric)
            decay_factor = 1.0 - (self.alpha * 0.01)
            vx = (vx + ax * self.time_step) * decay_factor
            vy = (vy + ay * self.time_step) * decay_factor
            vz = (vz + az * self.time_step) * decay_factor
            
            # Update continuous space positions
            px += vx * self.time_step
            py += vy * self.time_step
            pz += vz * self.time_step
            
            # Log telemetry updates every 10 steps to prevent log bloating
            if step % 10 == 0:
                trajectory_log.append({
                    "step": step,
                    "closest_node_id": current_node,
                    "field_potential": round(potential, 6),
                    "position": (round(px, 3), round(py, 3), round(pz, 3)),
                    "velocity_magnitude": round(math.sqrt(vx**2 + vy**2 + vz**2), 3)
                })
                
        return {
            "termination_status": "PROCURATION_COMPLETE",
            "initial_conditions": {"position": init_pos, "velocity": init_vel},
            "final_decay_state": {"node_id": current_node, "radius": round(r, 4)},
            "telemetry_stream": trajectory_log
        }


def main():
    print("🛸 Initializing Invariant Geodesic Orbit Propagation & Relativistic Decay Engine...")
    simulator = GeodesicSimulator()
    
    print("   Launching test particle tracking array through 114-node field limits...")
    results = simulator.propagate_orbit(steps=100)
    
    print("\\n------------------------------------------------------------")
    print("🚀 DISCRETE GEODESIC PROPAGATION STATUS: COMPLETED")
    print(f"   Initial Vector Coordinate Shell: {results['initial_conditions']['position']}")
    print(f"   Final Matrix Collision State   : Locked to Node {results['final_decay_state']['node_id']} (Radius: {results['final_decay_state']['radius']}mm)")
    print("------------------------------------------------------------")
    
    print("\\nSample Orbit Propagation Logs (10-Step Intervals):")
    for entry in results["telemetry_stream"][:3]:
        print(f"   Step {entry['step']}: Position {entry['position']} -> Intersecting Node {entry['closest_node_id']} (Velocity: {entry['velocity_magnitude']})")


if __name__ == '__main__':
    main()
