import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ShaderUniformsPayload(BaseModel):
    so13_rotation_angle_rad: float = 0.0
    field_frequency_hz: float = Field(432000000.0, ge=1.0)
    toroidal_coherence: float = Field(0.85, ge=0.0, le=1.0)
    element_plane_tilt_deg: float = 0.0

class PlasmaShaderCompiler:
    """
    Phase 27: GLSL volumetric plasma shader uniform compiler translating SO(13) matrix
    tensors and atomic element plane tilts into real-time WebGL shader parameters.
    """
    def compile_uniforms(self, payload: ShaderUniformsPayload) -> Dict[str, Any]:
        # Compute plasma emission color temperature (RGB vector) based on atomic plane tilt
        tilt_rad = math.radians(payload.element_plane_tilt_deg)
        r_spectrum = round(0.5 + 0.5 * math.cos(tilt_rad), 4)
        g_spectrum = round(0.5 + 0.5 * math.sin(tilt_rad), 4)
        b_spectrum = round(payload.toroidal_coherence, 4)

        # Waveguide turbulence velocity factor
        waveguide_velocity = round((payload.field_frequency_hz / 1e6) * 0.01, 4)

        return {
            "u_time_scale": waveguide_velocity,
            "u_so13_angle": round(payload.so13_rotation_angle_rad, 4),
            "u_plasma_color": [r_spectrum, g_spectrum, b_spectrum],
            "u_coherence_density": round(payload.toroidal_coherence * 2.5, 4),
            "glsl_fragment_snippet": (
                "uniform float u_time_scale;\n"
                "uniform vec3 u_plasma_color;\n"
                "void main() { gl_FragColor = vec4(u_plasma_color, u_coherence_density); }"
            )
        }
