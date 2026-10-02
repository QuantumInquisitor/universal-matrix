"""Continuous lifted central-mirror control, not a physical folding law.

The existing stella mirror is reached by simultaneous rotations in XY and ZW.
The embedded 3D geometry stays isometric in 4D; dimensions 5..13 are zero padding.
Its XYZ projection loses depth halfway to the mirror. Common rigid motion
preserves pre-existing collisions and does not implement relative hinge motion,
spherical inversion, scale transfer, or independent recursive dynamics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class LiftedMirrorControl:
    """Phase 0 -> 1 -> 2 is original -> central mirror -> original."""

    phase: float
    dimensions: int = 4

    def __post_init__(self):
        if isinstance(self.phase, (bool, complex)):
            raise ValueError("phase must be a finite real number in [0, 2]")
        phase = float(self.phase)
        if not math.isfinite(phase) or not 0 <= phase <= 2:
            raise ValueError("phase must be a finite real number in [0, 2]")
        if isinstance(self.dimensions, bool) or not isinstance(self.dimensions, int):
            raise ValueError("dimensions must be an integer from 4 to 13")
        if not 4 <= self.dimensions <= 13:
            raise ValueError("dimensions must be an integer from 4 to 13")
        object.__setattr__(self, "phase", phase)

    @property
    def cosine_sine(self):
        # Exact landmarks avoid reporting a tiny spurious depth at a flat view.
        landmarks = {
            0.0: (1.0, 0.0),
            0.5: (0.0, 1.0),
            1.0: (-1.0, 0.0),
            1.5: (0.0, -1.0),
            2.0: (1.0, 0.0),
        }
        return landmarks.get(
            self.phase, (math.cos(math.pi * self.phase), math.sin(math.pi * self.phase))
        )

    def jacobian(self):
        c, s = self.cosine_sine
        return (
            (c, -s, 0.0),
            (s, c, 0.0),
            (0.0, 0.0, c),
            (0.0, 0.0, s),
            *((0.0, 0.0, 0.0) for _ in range(self.dimensions - 4)),
        )

    def map_vector(self, vector):
        try:
            values = tuple(vector)
            if len(values) != 3 or any(isinstance(x, (bool, complex)) for x in values):
                raise ValueError
            values = tuple(float(x) for x in values)
            if not all(math.isfinite(x) for x in values):
                raise ValueError
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("vector must contain three finite real coordinates") from error
        result = tuple(
            math.fsum(a * b for a, b in zip(row, values, strict=True)) for row in self.jacobian()
        )
        if not all(math.isfinite(x) for x in result):
            raise ValueError("mapped coordinates exceed the finite numerical range")
        return result

    def map_point(self, point):
        return self.map_vector(point)

    @property
    def projected_determinant(self):
        return self.cosine_sine[0]

    @property
    def projected_rank(self):
        return 2 if self.phase in (0.5, 1.5) else 3

    @property
    def intrinsic_volume_scale(self):
        """sqrt(det(A.T A)) = 1 analytically; A is the rectangular Jacobian."""
        return 1.0
