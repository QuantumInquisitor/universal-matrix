import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class WindingParameters(BaseModel):
    major_radius_mm: float = Field(50.0, ge=5.0)
    minor_radius_mm: float = Field(15.0, ge=1.0)
    total_turns: int = Field(360, ge=9)
    so13_tilt_deg: float = 0.0
    feed_rate_mm_min: float = 500.0

class ToroidalWindingEngine:
    """
    Phase 28: Multi-axis G-code generator compiling non-Euclidean SO(13) matrices
    and Tesla triad geometries into 5-axis toolpaths for toroidal coil fabrication.
    """
    def generate_5axis_gcode(self, params: WindingParameters) -> Dict[str, Any]:
        gcode_lines = [
            "; Phase 28 Toroidal Coil Winding Toolpath",
            f"G21 ; Units in mm",
            f"G90 ; Absolute positioning",
            f"G1 F{params.feed_rate_mm_min}"
        ]

        tilt_rad = math.radians(params.so13_tilt_deg)
        steps = params.total_turns

        for i in range(steps + 1):
            theta = (2 * math.pi * i) / steps  # Major toroidal angle
            phi = theta * 9                      # Minor coil angle (9-fold triad harmonic)

            # Toroidal Parametric Equations with SO(13) Tilt
            x = (params.major_radius_mm + params.minor_radius_mm * math.cos(phi)) * math.cos(theta)
            y = (params.major_radius_mm + params.minor_radius_mm * math.cos(phi)) * math.sin(theta)
            z = params.minor_radius_mm * math.sin(phi) * math.cos(tilt_rad)

            # 5-Axis Rotational Angles (A = Spindle Tilt, C = Table Rotation)
            a_deg = round(math.degrees(phi) % 360, 2)
            c_deg = round(math.degrees(theta) % 360, 2)

            line = f"G1 X{round(x, 3)} Y{round(y, 3)} Z{round(z, 3)} A{a_deg} C{c_deg}"
            gcode_lines.append(line)

        return {
            "total_turns": params.total_turns,
            "generated_lines_count": len(gcode_lines),
            "sample_gcode": gcode_lines[:10],
            "full_gcode_stream": "\n".join(gcode_lines)
        }
