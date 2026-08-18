#!/usr/bin/env python3
"""
Universal Playing Field: G-Code Compiler Module (v6.1 JSON-Config Enabled)
Maps discrete 114-node toroidal geometric vectors into standardized 
CNC hardware toolpaths using a centralized global configuration file matrix.
"""

import math
import os
import sys
import json

# Ensure local paths load calculator dependencies cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL: 'calculator.py' must be present in the same directory.")
    sys.exit(1)


class GCodeCompiler:
    def __init__(self):
        """
        Dynamically reads localized manufacturing and dimension presets 
        from the centralized global config/settings.json matrix file.
        """
        # Resolve path tracking to root configuration location
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(root_dir, 'config', 'settings.json')
        
        # Load and parse json array states securely
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("WARNING: Central settings.json missing or malformed. Activating standalone fail-safes.")
            config = {
                "torus_dimensions": {"major_radius": 50.0, "minor_radius": 15.0},
                "manufacturing_presets": {"feed_rate": 1200, "retract_height": 5.0, "working_depth": -1.5, "infinity_step": 21}
            }

        # Initialize configurations directly from single configuration layer mappings
        self.feed_rate = config["manufacturing_presets"]["feed_rate"]
        self.retract_height = config["manufacturing_presets"]["retract_height"]
        self.working_depth = config["manufacturing_presets"]["working_depth"]
        self.infinity_step = config["manufacturing_presets"]["infinity_step"]
        
        self.major_radius = config["torus_dimensions"]["major_radius"]
        self.minor_radius = config["torus_dimensions"]["minor_radius"]
        
        # Pull core invariants from the verified math layer script
        self.total_nodes = mc.M_TOTAL        # 114 Total Positions
        self.core_nodes = mc.N_CORE          # 108 Internal Track Loop
        self.boundary_nodes = mc.B_BOUNDARY  # 6 External Face Gates

    def _project_node_to_3d(self, node_index):
        """Projects a discrete integer node index into continuous 3D coordinates."""
        bit_shift_offset = (node_index * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_shift_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_shift_offset) & 1
        
        bit_compression_factor = (up_bit * 0.05) - (down_bit * 0.05)
        dynamic_minor_radius = self.minor_radius * (1.0 + bit_compression_factor * (mc.ALPHA_GEOMETRIC * 10.0))

        theta = (2.0 * math.pi * node_index) / self.total_nodes
        phi = (2.0 * math.pi * (node_index * mc.S_AXIS)) / self.core_nodes
        
        x = (self.major_radius + dynamic_minor_radius * math.cos(phi)) * math.cos(theta)
        y = (self.major_radius + dynamic_minor_radius * math.cos(phi)) * math.sin(theta)
        z = dynamic_minor_radius * math.sin(phi)
        
        return round(x, 4), round(y, 4), round(z, 4)

    def generate_toroidal_gcode(self, output_filename="toroid_toolpath.gcode"):
        """Compiles the discrete 3-phase interlocking 21-step matrix toolpaths."""
        lines = [
            "; ========================================================",
            ";   UNIVERSAL PLAYING FIELD: TOROIDAL COIL MANUFACTURING TOOLPATH",
            ";   GENERATED FROM LOGIC ENGINE MASTER FRAMEWORK SPEC v6.1",
            ";   CRITICAL CONSTRAINT: 3-PHASE INTERLOCKING 21-STEP PATHING",
            "; ========================================================",
            "G21 ; Set system units to Millimeters",
            "G90 ; Set machine instruction to Absolute Coordinates",
            f"G0 Z{self.retract_height:.4f} ; Move spindle to safe clearing buffer height",
            "M03 S2000 ; Initialize spindle motor rotation",
            ""
        ]

        print(f"Compiling complete 3-Phase Material Infinity toolpath loop for {self.total_nodes}-Node Matrix...")
        
        node_execution_sequence = []
        for phase_offset in range(3):
            current_node = phase_offset
            for _ in range(self.total_nodes // 3):
                node_execution_sequence.append(current_node)
                current_node = (current_node + self.infinity_step) % self.total_nodes

        for idx, node_id in enumerate(node_execution_sequence):
            x, y, z = self._project_node_to_3d(node_id)
            is_boundary_gate = (node_id % (self.total_nodes // self.boundary_nodes)) == 0
            
            if idx == 0:
                lines.append(f"; Initialize primary coordinate entry point (Material Origin: Node {node_id})")
                lines.append(f"G0 X{x:.4f} Y{y:.4f} Z{self.retract_height:.4f}")
                lines.append(f"G1 Z{z + self.working_depth:.4f} F{self.feed_rate // 2} ; Engage tool head")
            else:
                if idx % 38 == 0:
                    lines.append(f"\n; Transitioning to Interlocking Winding Phase Layer (Node {node_id})")
                
                if is_boundary_gate:
                    lines.append(f"\n; Intersecting External Face Gate (Node {node_id}) -> Executing Geometric Helical Step")
                    lines.append(f"G2 X{x:.4f} Y{y:.4f} Z{z + self.working_depth:.4f} R{self.minor_radius:.4f} F{self.feed_rate}")
                else:
                    lines.append(f"G1 X{x:.4f} Y{y:.4f} Z{z + self.working_depth:.4f} F{self.feed_rate} ; Move to Node {node_id}")

        x0, y0, z0 = self._project_node_to_3d(0)
        lines.append(f"\n; Complete absolute vector loop circuit link back to origin")
        lines.append(f"G1 X{x0:.4f} Y{y0:.4f} Z{z0 + self.working_depth:.4f} F{self.feed_rate}")
        
        lines.extend([
            "",
            "; Hardware Safe Termination Sequence",
            f"G0 Z{self.retract_height:.4f} ; Safely extract tool head out of processing volume",
            "M05             ; Power off spindle motor assembly",
            "M30             ; End of program loop sequence execution",
            "; ========================================================"
        ])

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            
        print(f"SUCCESS: Automated CNC toolpath file compiled cleanly via configuration matrix values.")
        return output_path


def main():
    compiler = GCodeCompiler()
    compiler.generate_toroidal_gcode()


if __name__ == "__main__":
    main()
