"""Optional one-dimensional ideal cylindrical-pipe pressure modes.

Open ends have zero acoustic pressure; closed ends have zero axial pressure
gradient. No end correction, mean flow, losses, material fit or atom model.
"""

import json
import math
from dataclasses import dataclass

import numpy as np

MAX_INTERVALS = 256


def _positive(value, name):
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value):
        raise ValueError(f"{name} must be a positive finite real scalar")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a positive finite real scalar") from error
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be a positive finite real scalar")
    return result


def _count(value, name, minimum, maximum):
    if (isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or
            not minimum <= value <= maximum):
        raise ValueError(f"{name} must be an integer in {minimum}..{maximum}")
    return int(value)


@dataclass(frozen=True)
class PipeModes:
    frequencies_hz: np.ndarray
    positions_m: np.ndarray
    pressure_modes: np.ndarray
    dimensionless_eigenvalues: np.ndarray


@dataclass(frozen=True)
class PipeAcoustics:
    """Declared length [m] and sound speed [m/s]; endpoint choices are explicit."""

    length_m: float
    sound_speed_m_s: float
    left_end: str = "open"
    right_end: str = "open"

    def __post_init__(self):
        for name in ("length_m", "sound_speed_m_s"):
            object.__setattr__(self, name, _positive(getattr(self, name), name))
        if self.left_end not in ("open", "closed") or self.right_end not in ("open", "closed"):
            raise ValueError("each endpoint must be 'open' or 'closed'")
        scale = self.sound_speed_m_s / self.length_m
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("sound-speed/length scale must be finite and resolved")

    def analytic_frequencies_hz(self, count=3):
        count = _count(count, "count", 1, MAX_INTERVALS)
        if self.left_end == self.right_end:
            start = 1 if self.left_end == "open" else 0
            factors = np.arange(start, start + count, dtype=float) / 2
        else:
            factors = (2 * np.arange(count, dtype=float) + 1) / 4
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            frequencies = (self.sound_speed_m_s / self.length_m) * factors
        if not np.isfinite(frequencies).all() or np.any(frequencies[factors > 0] <= 0):
            raise ValueError("frequencies must be finite and resolved")
        return frequencies

    def finite_element_modes(self, *, intervals=64, count=3):
        """Linear consistent-mass FEM on x/L in [0,1], bounded dense solve.

        Pressure modes are arbitrary amplitudes normalized by integral p^2 d(x/L).
        A closed/closed pipe explicitly includes the static constant mode first.
        Frequencies near the mesh cutoff need refinement and are not accuracy-certified.
        """
        intervals = _count(intervals, "intervals", 2, MAX_INTERVALS)
        count = _count(count, "count", 1, MAX_INTERVALS)
        indices = np.arange(0 if self.left_end == "closed" else 1,
                            intervals + (self.right_end == "closed"))
        if count > len(indices):
            raise ValueError("count exceeds unconstrained finite-element degrees of freedom")
        stiffness = np.zeros((intervals + 1, intervals + 1))
        mass = np.zeros_like(stiffness)
        for node in range(intervals):
            stiffness[node:node+2, node:node+2] += intervals * np.array([[1, -1], [-1, 1]])
            mass[node:node+2, node:node+2] += np.array([[2, 1], [1, 2]]) / (6 * intervals)
        k, m = stiffness[np.ix_(indices, indices)], mass[np.ix_(indices, indices)]
        lower = np.linalg.cholesky(m)
        inverse = np.linalg.solve(lower, np.eye(len(indices)))
        symmetric = inverse @ k @ inverse.T
        if self.left_end == self.right_end == "closed":
            constant = lower.T @ np.ones(len(indices))
            constant /= np.linalg.norm(constant)
            reflector = constant.copy()
            reflector[0] += 1
            complement = (np.eye(len(indices)) - 2 * np.outer(reflector, reflector) /
                          np.dot(reflector, reflector))[:, 1:]
            values, vectors = np.linalg.eigh(complement.T @ symmetric @ complement)
            vectors = np.column_stack((constant, complement @ vectors))
        else:
            values, vectors = np.linalg.eigh(symmetric)
        tolerance = 64 * np.finfo(float).eps * len(indices) * np.max(np.abs(values))
        if not np.isfinite(values).all() or np.any(values <= tolerance):
            raise ValueError("positive acoustic eigenvalues are numerically unresolved")
        if self.left_end == self.right_end == "closed":
            values = np.r_[0.0, values]
        values, vectors = values[:count], vectors[:, :count]
        modes = np.zeros((intervals + 1, count))
        modes[indices] = np.linalg.solve(lower.T, vectors)
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            frequencies = (self.sound_speed_m_s / self.length_m) * (np.sqrt(values) / (2 * math.pi))
        if not np.isfinite(frequencies).all() or np.any(frequencies[values > 0] <= 0):
            raise ValueError("frequencies must be finite and resolved")
        positions = np.linspace(0, self.length_m, intervals + 1)
        if np.any(np.diff(positions) <= 0):
            raise ValueError("physical mesh spacing is numerically unresolved")
        return PipeModes(frequencies, positions, modes, values)


def main():
    report = []
    for left, right in (("open", "open"), ("closed", "open"), ("closed", "closed")):
        pipe = PipeAcoustics(1.0, 343.0, left, right)
        report.append({"left_end": left, "right_end": right,
                       "analytic_hz": pipe.analytic_frequencies_hz().tolist(),
                       "fem_128_hz": pipe.finite_element_modes(intervals=128).frequencies_hz.tolist()})
    print(json.dumps({"scope": "synthetic ideal cylinder; no measured instrument fit",
                      "length_m": 1.0, "sound_speed_m_s": 343.0, "modes": report}, indent=2))


if __name__ == "__main__":
    main()
