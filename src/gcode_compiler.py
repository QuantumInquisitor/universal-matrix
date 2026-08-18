#!/usr/bin/env python3
"""
Universal Playing Field: G-Code Compiler Module (v6.0 Manufacturing Spec)
Maps discrete 114-node toroidal geometric vectors into standardized 
CNC hardware toolpaths using G0, G1, and G2 interpolation tracks.
"""

import math
import os
import sys

# Ensure local paths load calculator dependencies cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL: 'calculator.py' must be present in the same directory.")
    sys.exit(1)


class GCodeCompiler:
    def __init__(self, feed_rate=1200, retract_height=5.0, working_depth=-1.5):
        """
        Initializes manufacturing feed rates and coordinate constraints.
        """
        self.feed_rate = feed_rate
        self.retract_height = retract_height
        self.working_depth = working_depth
        
        # Pull geometric constraints from the verified core 64-bit module
        self.total_nodes = mc.M_TOTAL        # 114 Total Positions
        self.core_nodes = mc.N_CORE          # 108 Internal Track Loop
        self.boundary_nodes = mc.B_BOUNDARY  # 6 External Face Gates
        
        # Dimensions for physical coil projection (in millimeters)
        self.major_radius = 50.0  # Center of torus to center of coil tube
        self.minor_radius = 15.0  # Outer profile radius of the winding tube
        
        # Track our 21-step jumping constant specified in Section 2.2
        self.infinity_step = 21

    def _project_node_to_3d(self, node_index):
        """
        Projects a discrete integer node index into continuous 3D coordinates,
        modulated at the hardware layer by the 64-bit register bitmasks and alpha_geometric.
        """
        # Extract bit-level state weights to enforce deterministic physical thickness shifts
        bit_shift_offset = (node_index * 7) % 64
        up_bit = (mc.STREAM_UP >> bit_shift_offset) & 1
        down_bit = (mc.STREAM_DOWN >> bit_shift_offset) & 1
        
        # Modulate the physical tube radius based on bit states scaled via ALPHA_GEOMETRIC
        bit_compression_factor = (up_bit * 0.05) - (down_bit * 0.05)
        dynamic_minor_radius = self.minor_radius * (1.0 + bit_compression_factor * (mc.ALPHA_GEOMETRIC * 10.0))

        # Calculate angular division stepping sequentially around the major circumference
        theta = (2.0 * math.pi * node_index) / self.total_nodes
        
        # Map localized winding rotation using the 3-6-9 structural frequency
        phi = (2.0 * math.pi * (node_index * mc.S_AXIS)) / self.core_nodes
        
        # Parametric equations tracking the spatial shell mapping
        x = (self.major_radius + dynamic_minor_radius * math.cos(phi)) * math.cos(theta)
        y = (self.major_radius + dynamic_minor_radius * math.cos(phi)) * math.sin(theta)
        z = dynamic_minor_radius * math.sin(phi)
        
        return round(x, 4), round(y, 4), round(z, 4)

    def generate_toroidal_gcode(self, output_filename="toroid_toolpath.gcode"):
        """
        Compiles the discrete 21-step Material Infinity routing matrices into an 
        optimized G-Code text file ready for industrial CNC hardware loading.
        """
        lines = [
            "; ========================================================",
            ";   UNIVERSAL PLAYING FIELD: TOROIDAL COIL MANUFACTURING TOOLPATH",
            ";   GENERATED FROM LOGIC ENGINE MASTER FRAMEWORK SPEC v6.0",
            ";   CRITICAL CONSTRAINT: 3-PHASE INTERLOCKING 21-STEP PATHING",
            "; ========================================================",
            "G21 ; Set system units to Millimeters",
            "G90 ; Set machine instruction to Absolute Coordinates",
            f"G0 Z{self.retract_height:.4f} ; Move spindle to safe clearing buffer height",
            "M03 S2000 ; Initialize spindle motor rotation",
            ""
        ]

        print(f"Compiling complete 3-Phase Material Infinity toolpath loop for {self.total_nodes}-Node Matrix...")
        
        # Generate a balanced non-sequential sequence via 3 interlocking 21-step sub-coils
        node_execution_sequence = []
        for phase_offset in range(3):
            current_node = phase_offset
            for _ in range(self.total_nodes // 3):  # 38 nodes per phase layer
                node_execution_sequence.append(current_node)
                current_node = (current_node + self.infinity_step) % self.total_nodes

        # Step 1: Track the path sequence through our calculated coprime map array
        for idx, node_id in enumerate(node_execution_sequence):
            x, y, z = self._project_node_to_3d(node_id)
            
            # Use strict integer floor division to eliminate micro-rounding controller drift
            is_boundary_gate = (node_id % (self.total_nodes // self.boundary_nodes)) == 0
            
            if idx == 0:
                lines.append(f"; Initialize primary coordinate entry point (Material Origin: Node {node_id})")
                lines.append(f"G0 X{x:.4f} Y{y:.4f} Z{self.retract_height:.4f}")
                lines.append(f"G1 Z{z + self.working_depth:.4f} F{self.feed_rate // 2} ; Engage tool head")
            else:
                # Add layout markers when changing to a new sub-coil winding layer
                if idx % 38 == 0:
                    lines.append(f"\n; Transitioning to Interlocking Winding Phase Layer (Node {node_id})")
                
                if is_boundary_gate:
                    lines.append(f"\n; Intersecting External Face Gate (Node {node_id}) -> Executing Geometric Helical Step")
                    lines.append(f"G2 X{x:.4f} Y{y:.4f} Z{z + self.working_depth:.4f} R{self.minor_radius:.4f} F{self.feed_rate}")
                else:
                    lines.append(f"G1 X{x:.4f} Y{y:.4f} Z{z + self.working_depth:.4f} F{self.feed_rate} ; Move to Node {node_id}")

        # Step 2: Finalize path geometry loop by closing the circuit vector back to Node 0
        x0, y0, z0 = self._project_node_to_3d(0)
        lines.append(f"\n; Complete absolute vector loop circuit link back to origin")
        lines.append(f"G1 X{x0:.4f} Y{y0:.4f} Z{z0 + self.working_depth:.4f} F{self.feed_rate}")
        
        # Step 3: Append structural teardown sequence blocks
        lines.extend([
            "",
            "; Hardware Safe Termination Sequence",
            f"G0 Z{self.retract_height:.4f} ; Safely extract tool head out of processing volume",
            "M05             ; Power off spindle motor assembly",
            "M30             ; End of program loop sequence execution",
            "; ========================================================"
        ])

        # Write data to external target file destination path
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            
        print(f"SUCCESS: Automated CNC toolpath file compiled cleanly.")
        print(f"Target Output Path Destination: {output_path}")
        return output_path


def main():
    compiler = GCodeCompiler()
    compiler.generate_toroidal_gcode()


if __name__ == "__main__":
    main()
