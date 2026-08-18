#!/usr/bin/env python3
"""
Universal Playing Field: Discrete Light-Cone Ray Tracer & Deflection Engine
Models optical wave vectors splitting and refracting across the 114-node grid.
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


class LightConeSimulator:
    def __init__(self):
        """Initializes system invariants and matrix configuration bounds."""
        self.total_nodes = mc.M_TOTAL          # 114 System Base
        self.alpha = mc.ALPHA_GEOMETRIC        # Invariant spatial scale factor
        self.major_radius = 50.0
        self.minor_radius = 15.0

    def _get_node_refraction_index(self, node_id: int) -> float:
        """Computes localized optical density metrics from active 64-bit registers."""
        bit_offset = (node_id * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_offset) & 1
        
        # Check for 3-6-9 vortex control triad nodes
        is_tesla = (node_id % 3 == 0) or (node_id % 6 == 0) or (node_id % 9 == 0)
        multiplier = 4.5 if is_tesla else 1.0
        
        # Base refraction index scales with alpha_geometric properties
        index = 1.0 + (up_bit * 0.08 - down_bit * 0.02) * self.alpha * multiplier
        return float(index)

    def simulate_light_ray(self, entrance_angle_rad=0.0, wavelength_nm=550.0) -> dict:
        """Traces an optical vector path across the discrete frequency node wells."""
        current_angle = entrance_angle_rad
        path_history = []
        
        # Trace the ray profile as it processes sequentially across key node regions
        for node_id in range(self.total_nodes):
            # Isolate the 6 external boundary face gates
            is_gate = (node_id % 19 == 0)
            n_index = self._get_node_refraction_index(node_id)
            
            # Compute chromatic vector deflection (shorter wavelengths refract more)
            chromatic_scaler = (550.0 / wavelength_nm) ** 2
            deflection_delta = (n_index - 1.0) * math.sin(current_angle) * chromatic_scaler
            
            # Update wave vector heading parameters
            current_angle += deflection_delta
            
            # Log vector telemetry data at boundary intersections
            if is_gate or node_id % 9 == 0:
                path_history.append({
                    "node_intersected": node_id,
                    "classification": "Boundary Face Gate" if is_gate else "Core Vortex Mesh",
                    "refraction_index": round(n_index, 6),
                    "deflection_radians": round(deflection_delta, 6),
                    "current_heading_rad": round(current_angle, 6)
                })
                
        total_net_deflection = current_angle - entrance_angle_rad
        return {
            "wavelength_tracked_nm": wavelength_nm,
            "total_net_deflection_deg": round(math.degrees(total_net_deflection), 4),
            "final_heading_rad": round(current_angle, 6),
            "optical_telemetry_stream": path_history
        }


def main():
    print("🔮 Initializing Discrete Light-Cone Ray Tracer & Deflection Simulator...")
    tracer = LightConeSimulator()
    
    print("   Tracking optical ray arrays through the 114-node field gradient...")
    green_ray = tracer.simulate_light_ray(entrance_angle_rad=0.5, wavelength_nm=532.0)
    violet_ray = tracer.simulate_light_ray(entrance_angle_rad=0.5, wavelength_nm=405.0)
    
    print("\\n------------------------------------------------------------")
    print("🚀 DISCRETE OPTICAL DEFLECTION STATUS: EVALUATED")
    print(f"   Green Light (532nm) Net Deflection : {green_ray['total_net_deflection_deg']} degrees")
    print(f"   Violet Light (405nm) Net Deflection: {violet_ray['total_net_deflection_deg']} degrees")
    print("------------------------------------------------------------")
    
    print("\\nSample Optical Refraction Stream (Green Light):")
    for entry in green_ray["optical_telemetry_stream"][:3]:
        print(f"   Node {entry['node_intersected']} ({entry['classification']}): Index {entry['refraction_index']} -> Heading: {entry['current_heading_rad']} rad")


if __name__ == '__main__':
    main()
