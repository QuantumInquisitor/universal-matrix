# LEGACY / COMPATIBILITY MODULE
# This module preserves an earlier experimental interface and may use historical
# SO(13), 114-node, 3/6/9, toroidal, biological, or related terminology.
# Those labels are not part of the current canonical Universal Matrix kernel
# unless separately migrated, documented, and tested. See ARCHITECTURE.md and
# docs/DOCUMENTATION_STATUS.md for current authority.

import math
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class AcousticFieldConfig(BaseModel):
    base_frequency_hz: float = Field(40000.0, ge=20.0, le=100000.0) # Default 40 kHz ultrasound
    transducer_count: int = Field(16, ge=1, le=128)
    so13_phase_angle_rad: float = 0.0
    triad_harmonic_index: int = Field(9, ge=1, le=9)

class AcousticResonanceSynthesizer:
    """
    Phase 36: Ultrasonic transducer array phase delay generator converting
    SO(13) tensors and Tesla triad harmonics into acoustic pressure fields.
    """
    def synthesize_phase_delays(self, config: AcousticFieldConfig) -> Dict[str, Any]:
        phase_delays_rad = []
        wavelength_m = 343.0 / config.base_frequency_hz  # Speed of sound / frequency

        for i in range(config.transducer_count):
            # Spatial offset phase delay formula
            spatial_phase = (2 * math.pi * i * (wavelength_m / 4.0)) / wavelength_m
            harmonic_offset = (config.triad_harmonic_index / 9.0) * math.pi
            total_delay = (spatial_phase + config.so13_phase_angle_rad + harmonic_offset) % (2 * math.pi)
            phase_delays_rad.append(round(total_delay, 4))

        return {
            "status": "ACOUSTIC_PHASE_SYNTHESIZED",
            "base_frequency_hz": config.base_frequency_hz,
            "transducer_count": config.transducer_count,
            "wavelength_meters": round(wavelength_m, 6),
            "phase_delays_radians": phase_delays_rad,
            "peak_pressure_node_calculated": True
        }
