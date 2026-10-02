"""Chosen paired-helix rotation under the existing canonical tick phase.

Lengths are synthetic coordinate units. No physical tick duration, flow,
material dynamics, or uniquely reconstructed geometry is inferred.
"""

import math
from dataclasses import dataclass
from numbers import Real

import numpy as np

from .canonical_polarity_clock import polarity_phase_from_tick


def _real(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real scalar")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite real scalar") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite real scalar")
    return result


def rotation(angle):
    """Proper rotation about the local helix axis, in radians."""
    angle = _real(angle, "angle")
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def clock_rotation(tick):
    """Use the unchanged canonical phase for signed integer elapsed ticks."""
    if isinstance(tick, (bool, np.bool_)) or not isinstance(tick, (int, np.integer)):
        raise ValueError("tick must be an integer")
    return rotation(polarity_phase_from_tick(int(tick)))


@dataclass(frozen=True)
class PairedHelixClock:
    radius: float = 0.4
    pitch: float = 0.3
    tilt_rad: float = 0.49
    azimuth_rad: float = -0.27

    def __post_init__(self):
        for name in ("radius", "pitch", "tilt_rad", "azimuth_rad"):
            object.__setattr__(self, name, _real(getattr(self, name), name))
        if self.radius <= 0:
            raise ValueError("radius must be positive")

    @property
    def orientation(self):
        """Chosen fixed proper rotation from helix-local to display coordinates."""
        c, s = math.cos(self.tilt_rad), math.sin(self.tilt_rad)
        return rotation(self.azimuth_rad) @ np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

    def strand(self, parameter, label):
        """Local strand positions; parameter is a scalar or nonempty 1D sequence."""
        if (
            isinstance(label, (bool, np.bool_))
            or not isinstance(label, (int, np.integer))
            or label not in (0, 1)
        ):
            raise ValueError("strand label must be integer 0 or 1")
        try:
            raw = np.asarray(parameter, dtype=object)
        except (ValueError, TypeError) as error:
            raise ValueError("parameter must be a real scalar or nonempty 1D sequence") from error
        if raw.ndim > 1 or raw.size == 0:
            raise ValueError("parameter must be a real scalar or nonempty 1D sequence")
        u = np.array([_real(value, "parameter") for value in raw.flat]).reshape(raw.shape)
        try:
            with np.errstate(over="raise", invalid="raise"):
                points = np.stack(
                    (
                        self.radius * np.cos(u + label * math.pi),
                        self.radius * np.sin(u + label * math.pi),
                        (self.pitch / (2 * math.pi)) * u,
                    ),
                    axis=-1,
                )
        except FloatingPointError as error:
            raise ValueError("strand positions must be finite and resolved") from error
        if not np.isfinite(points).all():
            raise ValueError("strand positions must be finite and resolved")
        return points

    def frame(self, tick, parameters):
        """Two labeled strands at elapsed tick; no node-label phase inference.

        Returns (2, 3) for one material parameter, or (2, N, 3) for N parameters.
        """
        action = clock_rotation(tick)
        material = np.stack([self.strand(parameters, label) for label in (0, 1)])
        try:
            with np.errstate(over="raise", invalid="raise"):
                result = material @ action.T @ self.orientation.T
        except FloatingPointError as error:
            raise ValueError("frame positions must be finite and resolved") from error
        if not np.isfinite(result).all():
            raise ValueError("frame positions must be finite and resolved")
        return result
