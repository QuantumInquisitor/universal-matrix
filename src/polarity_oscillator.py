"""Phase-driven polarity oscillator tied to the canonical T_54 involution.

This experimental layer implements the hypothesis that polarity is primarily a
property of an oscillatory transition rather than a permanently attached label.

Let phi be an unwrapped phase. Define the half-cycle parity

    h(phi) = floor(phi / pi) mod 2.

Then the canonical state is

    n(phi) = n0 + 54*h(phi) mod 108
    sigma(phi) = sigma0 * (-1)^h(phi).

Therefore every half-cycle applies the canonical polarity operator

    Q(n, sigma) = (n+54, -sigma),

and a full 2*pi cycle gives Q^2 = I.

A continuous carrier

    p(phi) = cos(phi)

provides a smooth inward/outward field orientation:
    p > 0  -> outward-like
    p < 0  -> inward-like
    p = 0  -> neutral crossing.

The discrete sigma is a coarse label of the continuous carrier and is not used
to force an instantaneous physical field jump.

This is an experimental dynamical adapter, not a canonical theorem or an
established physical law.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Iterable

try:
    from . import canonical_kernel as ck
except ImportError:
    import canonical_kernel as ck


TAU = 2.0 * math.pi


def half_cycle_index(phase: float) -> int:
    """Return the half-cycle index with robust snapping at exact pi boundaries.

    Routing-tick evolution reaches mathematical boundaries such as pi after a
    finite number of pi/18 increments. Floating addition can place the stored
    value a few ulps below the exact boundary, so values numerically equal to an
    integer multiple of pi are snapped before flooring.
    """
    quotient = phase / math.pi
    nearest = round(quotient)
    if math.isclose(quotient, nearest, rel_tol=0.0, abs_tol=1e-12):
        quotient = float(nearest)
    return math.floor(quotient)


def half_cycle_parity(phase: float) -> int:
    return half_cycle_index(phase) % 2


def polarity_carrier(phase: float) -> float:
    """Continuous signed inward/outward carrier in [-1, 1]."""
    return math.cos(phase)


def transition_carrier(phase: float) -> float:
    """Maximum at neutral crossings, zero at polarity extrema."""
    return math.sin(phase)


def discrete_polarity(phase: float, initial_polarity: int = 1) -> int:
    if initial_polarity not in (-1, 1):
        raise ValueError("initial_polarity must be -1 or +1")
    return initial_polarity * (-1 if half_cycle_parity(phase) else 1)


def canonical_polarity_state(
    base_node: int,
    phase: float,
    initial_polarity: int = 1,
) -> tuple[int, int]:
    """Return (node, sigma) after the phase-selected T54 involution."""
    parity = half_cycle_parity(phase)
    node = ck.translate(base_node, ck.POLARITY_STEP * parity)
    sigma = discrete_polarity(phase, initial_polarity)
    return node, sigma


@dataclass
class PolarityOscillator:
    base_node: int
    phase: float = 0.0
    angular_rate: float = 1.0
    amplitude: float = 1.0
    initial_polarity: int = 1

    def __post_init__(self) -> None:
        self.base_node %= ck.N_CORE
        if self.angular_rate < 0:
            raise ValueError("angular_rate must be non-negative")
        if self.amplitude < 0:
            raise ValueError("amplitude must be non-negative")
        if self.initial_polarity not in (-1, 1):
            raise ValueError("initial_polarity must be -1 or +1")

    @property
    def node(self) -> int:
        return canonical_polarity_state(
            self.base_node,
            self.phase,
            self.initial_polarity,
        )[0]

    @property
    def polarity(self) -> int:
        return canonical_polarity_state(
            self.base_node,
            self.phase,
            self.initial_polarity,
        )[1]

    @property
    def carrier(self) -> float:
        return polarity_carrier(self.phase)

    @property
    def oriented_amplitude(self) -> float:
        return self.amplitude * self.carrier

    @property
    def neutral_crossing_strength(self) -> float:
        return abs(transition_carrier(self.phase))

    def advance(self, dt: float, phase_drive: float = 0.0) -> None:
        if dt < 0:
            raise ValueError("dt must be non-negative")
        self.phase += dt * (self.angular_rate + phase_drive)

    def snapshot(self) -> dict[str, float | int | str]:
        direction = (
            "outward"
            if self.carrier > 0
            else "inward"
            if self.carrier < 0
            else "neutral"
        )
        return {
            "base_node": self.base_node,
            "node": self.node,
            "phase": self.phase,
            "polarity": self.polarity,
            "carrier": self.carrier,
            "oriented_amplitude": self.oriented_amplitude,
            "neutral_crossing_strength": self.neutral_crossing_strength,
            "direction": direction,
            "model_status": "experimental_phase_driven_polarity",
        }


def gauge_covariant_phase_drive(
    source_phase: float,
    target_phase: float,
    link_phase: float,
    coupling: float,
) -> float:
    """Sinusoidal phase drive using a gauge-invariant phase difference."""
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    delta = target_phase - source_phase + link_phase
    return coupling * math.sin(delta)


def coupled_phase_drives(
    phases: Iterable[float],
    link_phases: Iterable[float],
    coupling: float,
) -> list[float]:
    """Nearest-neighbor open-chain gauge-covariant phase drives.

    link_phases[i] belongs to the oriented link i -> i+1.
    """
    phases = list(phases)
    links = list(link_phases)
    if len(links) != max(0, len(phases) - 1):
        raise ValueError("link_phases must have len(phases)-1 entries")
    if coupling < 0:
        raise ValueError("coupling must be non-negative")

    drives = [0.0] * len(phases)
    for i, theta in enumerate(links):
        d = gauge_covariant_phase_drive(
            phases[i],
            phases[i + 1],
            theta,
            coupling,
        )
        drives[i] += d
        drives[i + 1] -= d
    return drives
