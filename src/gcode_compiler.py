#!/usr/bin/env python3
"""
Universal Playing Field: G-Code Compiler Module (v5.0 Manufacturing Spec)
Maps discrete 114-node toroidal geometric vectors into standardized 
CNC hardware toolpaths using G0, G1, and G2 interpolation tracks.
"""

import math
import os
import sys

# Ensure the local path can import the core engine components cleanly
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
        :param feed_rate: Tool velocity in mm/min (G1/G2 execution speed).
        :param retract_height: Z-axis rapid positioning buffer (safe travel height).
        :param working_depth: Z-axis tool engagement depth during coiling.
        """
        self.feed_rate = feed_rate
        self.retract_height = retract_height
        self.working_depth = working_depth
        
        # Pull geometric constraints from the verified core module
        self.total_nodes = mc.M_TOTAL      # 114 Total Positions
        self.core_nodes = mc.N_CORE        # 108 Internal Track Loop
        self.boundary_nodes = mc.B_BOUNDARY  # 6 External Face Gates
        
        # Dimensions for physical coil projection (in millimeters)
        self.major_radius = 50.0  # Center of torus to center of coil tube
        self.minor_radius = 15.0  # Outer profile radius of the winding tube

    def _project_node_to_3d(self, node_index):
        """
        Projects a discrete integer node index from the Z_114 ring topology 
        into continuous 3D Euclidean coordinates across a toroidal shell.
        """
        # Calculate angular division stepping sequentially around the major ring circumference
        theta = (2.0 * math.pi * node_index) / self.total_nodes
        
        # Map localized winding rotation using the 3-6-9 structural frequency
        phi = (2.0 * math.pi * (node_index * mc.S_AXIS)) / self.core_nodes
        
        # Parametric equations tracking the spatial shell mapping
        x = (self.major_radius + self.minor_radius * math.cos(phi)) * math.cos(theta)
        y = (self.major_radius + self.minor_radius * math.cos(phi)) * math.sin(theta)
        z = self.minor_radius * math.sin(phi)
        
        return round(x, 4), round(y, 4), round(z, 4)

    def generate_toroidal_gcode(self, output_filename="toroid_toolpath.gcode"):
        """
        Compiles the discrete vector matrix paths into an optimized, physical
        G-Code instruction text file ready for industrial CNC hardware loading.
        """
        lines = [
            "; ========================================================",
            ";   UNIVERSAL PLAYING FIELD: TOROIDAL COIL MANUFACTURING TOOLPATH",
            ";   GENERATED FROM LOGIC ENGINE MASTER FRAMEWORK SPEC v5.0",
            "; ========================================================",
            "G21 ; Set system units to Millimeters",
            "G90 ; Set machine instruction to Absolute Coordinates",
            f"G0 Z{self.retract_height:.4f} ; Move spindle to safe clearing buffer height",
            "M03 S2000 ; Initialize spindle motor rotation if tracking standard carving routing",
            ""
        ]

        print(f"Compiling toolpath array for {self.total_nodes}-Node Matrix layout...")
        
        # Step 1: Track the structural sequencing across the entire 114-node absolute boundary
        for i in range(self.total_nodes):
            x, y, z = self._project_node_to_3d(i)
            
            # Map specific logic triggers based on matrix array intersections
            is_boundary_gate = (i % (self.total_nodes / self.boundary_nodes)) == 0
            
            if i == 0:
                # Rapid travel positioning to initial coordinate anchor location
                lines.append(f"; Initialize primary coordinate entry point (Node {i})")
                lines.append(f"G0 X{x:.4f} Y{y:.4f} Z{self.retract_height:.4f}")
                lines.append(f"G1 Z{z + self.working_depth:.4f} F{self.feed_rate // 2} ; Engage tool head")
            else:
                if is_boundary_gate:
                    lines.append(f"\n; Crossing External Hypercube Boundary Face Gate (Node {i})")
                    # Use helical interpolation arc approximation to secure geometry stability
                    lines.append(f"G2 X{x:.4f} Y{y:.4f} Z{z + self.working_depth:.4f} R{self.minor_radius:.4f} F{self.feed_rate}")
                else:
                    # Execute linear interpolation trace pathing across the core loop axis
                    lines.append(f"G1 X{x:.4f} Y{y:.4f} Z{z + self.working_depth:.4f} F{self.feed_rate}")

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
        with open(output_path, "w") as file:
            file.write("\n".join(lines))
            
        print(f"SUCCESS: Automated CNC toolpath file compiled cleanly.")
        print(f"Target Output Path Destination: {output_path}")
        return output_path


def main():
    compiler = GCodeCompiler()
    compiler.generate_toroidal_gcode()


if __name__ == "__main__":
    main()
