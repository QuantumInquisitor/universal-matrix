"""Prescribed breathing overlay with material-area and similarity controls.

No period, actuation law, or coupling to the Q-ball breathing trace is inferred.
All lengths including the core offset thickness scale together.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .lynchpin_finite_panel_control import deformation_metrics, panel_vertices


@dataclass(frozen=True)
class BreathingCycle:
    amplitude: float = 0.1

    def __post_init__(self):
        if isinstance(self.amplitude, (bool, complex)):
            raise ValueError("amplitude must be finite and in [0,1)")
        value = float(self.amplitude)
        if not math.isfinite(value) or not 0 <= value < 1:
            raise ValueError("amplitude must be finite and in [0,1)")
        object.__setattr__(self, "amplitude", value)

    def state(self, phase: float) -> dict:
        if isinstance(phase, (bool, complex)):
            raise ValueError("phase must be finite and in [0,1]")
        phase = float(phase)
        if not math.isfinite(phase) or not 0 <= phase <= 1:
            raise ValueError("phase must be finite and in [0,1]")
        sine, cosine = math.sin(2 * math.pi * phase), math.cos(2 * math.pi * phase)
        if phase in (0.0, 0.25, 0.5, 0.75, 1.0):
            sine, cosine = {
                0.0: (0.0, 1.0),
                0.25: (1.0, 0.0),
                0.5: (0.0, -1.0),
                0.75: (-1.0, 0.0),
                1.0: (0.0, 1.0),
            }[phase]
        scale = 1 + self.amplitude * sine
        rate = 2 * math.pi * self.amplitude * cosine
        return dict(
            scale=scale,
            scale_rate_per_phase=rate,
            similarity_volume_ratio=scale**3,
            similarity_density_ratio=scale**-3,
            relative_current_density_ratio=scale**-2,
            minimum_cycle_scale=1 - self.amplitude,
        )

    def panel(self, phase: float, dimensions: int, panel: int, collar: float = 0.15) -> dict:
        state = self.state(phase)
        scale = state["scale"]
        deformation = deformation_metrics(phase, dimensions, panel)
        area_ratio = scale**2 * deformation["area_ratio"]
        return dict(
            vertices=(scale * panel_vertices(phase, dimensions, panel, collar)).tolist(),
            principal_stretches=[scale * x for x in deformation["principal_stretches"]],
            area_ratio=area_ratio,
            material_surface_density_ratio=1 / area_ratio,
            total_core_thickness=0.02 * scale,
            density_scope="uniform material density relative to reference panel; no exchange",
        )

    def similarity_lab_current(
        self, phase: float, position, reference_current, reference_density: float = 1.0
    ):
        """Uniform 3D breathing-cell control: advection plus Piola-scaled current.

        This checks breathing alone, not the nonuniform panel fold or a complete
        flow network. The reference current here is a constant vector.
        """
        position, current = np.asarray(position), np.asarray(reference_current)
        if (
            position.shape != (3,)
            or current.shape != (3,)
            or np.iscomplexobj(position)
            or np.iscomplexobj(current)
            or not np.all(np.isfinite(position))
            or not np.all(np.isfinite(current))
        ):
            raise ValueError("finite real three-vectors required")
        if (
            isinstance(reference_density, (bool, complex))
            or not math.isfinite(reference_density)
            or reference_density < 0
        ):
            raise ValueError("finite nonnegative reference density required")
        state = self.state(phase)
        scale, rate = state["scale"], state["scale_rate_per_phase"]
        density = reference_density / scale**3
        velocity = (rate / scale) * position
        return density * velocity + current / scale**2
