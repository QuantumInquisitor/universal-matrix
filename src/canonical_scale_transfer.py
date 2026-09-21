"""Canonical-locked alternating inter-scale transfer.

This experimental module sharpens the neutral-crossing scale-transfer model by
adding two structural assumptions:

1. adjacent nested scale layers alternate orientation,

       epsilon_l = (-1)^l,

   so the same clock phase corresponds to opposite signed toroidal orientation
   on neighboring layers;

2. the maximum dimensionless transfer rotation per routing tick is identified
   with the exact canonical polarity-clock increment,

       Delta phi = pi / 18.

The second assumption is a normalization candidate, not a theorem. It removes a
free transfer coefficient only if future comparison with experiment supports
that canonical locking.

For a nearest-neighbor pair (a_l, a_{l+1}), conservation of

    C = a_l^2 + a_{l+1}^2

under a linear continuous exchange law requires a skew-symmetric generator.
Therefore the most general two-state conservative generator has the form

        [ 0  -g ]
    A = [       ],
        [ g   0 ]

which exponentiates to a rotation. The phase and scale-parity hypotheses then
set the signed one-tick angle to

    delta_l(phi) = epsilon_l * (pi/18) * sin(phi).

Consequences:
- transfer vanishes at polarity extrema;
- transfer is strongest at neutral crossings;
- adjacent scale edges alternate signed orientation;
- reversing the transition carrier reverses the transfer;
- pair and chain quadratic content remain conserved exactly up to floating
  arithmetic.

This is an experimental bridge layer. It does not establish that physical
energy, gravity, electromagnetism, or real toroidal fields follow this law.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

try:
    from .canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK
    from .scale_transfer import quadratic_content
except ImportError:
    from canonical_polarity_clock import POLARITY_PHASE_PER_ROUTING_TICK
    from scale_transfer import quadratic_content


def scale_orientation(layer_index: int) -> int:
    """Return the alternating orientation epsilon_l = (-1)^l."""
    if layer_index < 0:
        raise ValueError("layer_index must be non-negative")
    return 1 if layer_index % 2 == 0 else -1


def alternating_polarity_carrier(phase: float, layer_index: int) -> float:
    """Signed inward/outward carrier with alternating scale orientation."""
    return scale_orientation(layer_index) * math.cos(phase)


def alternating_transfer_carrier(phase: float, layer_index: int) -> float:
    """Quadrature transfer carrier with alternating scale orientation."""
    return scale_orientation(layer_index) * math.sin(phase)


def canonical_transfer_angle(
    phase: float,
    lower_layer_index: int,
    tick_fraction: float = 1.0,
) -> float:
    """Return the canonical-locked inter-scale rotation angle.

    tick_fraction=1 corresponds to one complete routing tick. Fractional values
    are useful for symmetric operator splitting.
    """
    if tick_fraction < 0:
        raise ValueError("tick_fraction must be non-negative")
    return (
        POLARITY_PHASE_PER_ROUTING_TICK
        * alternating_transfer_carrier(phase, lower_layer_index)
        * tick_fraction
    )


def canonical_transfer_pair(
    lower_amplitude: float,
    upper_amplitude: float,
    phase: float,
    lower_layer_index: int,
    tick_fraction: float = 1.0,
) -> tuple[float, float]:
    """Apply one canonical-locked conservative adjacent-scale rotation."""
    angle = canonical_transfer_angle(
        phase,
        lower_layer_index,
        tick_fraction=tick_fraction,
    )
    c = math.cos(angle)
    s = math.sin(angle)
    return (
        c * lower_amplitude - s * upper_amplitude,
        s * lower_amplitude + c * upper_amplitude,
    )


def canonical_transfer_chain(
    amplitudes: Sequence[float],
    edge_phases: Sequence[float],
    tick_fraction: float = 1.0,
) -> list[float]:
    """Apply a symmetric nearest-neighbor canonical-locked transfer sweep.

    edge_phases[l] controls the edge between scale layers l and l+1.

    The forward/reverse half-sweep is time symmetric and every local map is
    orthogonal, so the global quadratic content is conserved.
    """
    values = [float(a) for a in amplitudes]
    phases = [float(p) for p in edge_phases]

    if len(phases) != max(0, len(values) - 1):
        raise ValueError("edge_phases must have len(amplitudes)-1 entries")
    if tick_fraction < 0:
        raise ValueError("tick_fraction must be non-negative")

    half = 0.5 * tick_fraction

    for i, phase in enumerate(phases):
        values[i], values[i + 1] = canonical_transfer_pair(
            values[i],
            values[i + 1],
            phase,
            lower_layer_index=i,
            tick_fraction=half,
        )

    for i in range(len(phases) - 1, -1, -1):
        values[i], values[i + 1] = canonical_transfer_pair(
            values[i],
            values[i + 1],
            phases[i],
            lower_layer_index=i,
            tick_fraction=half,
        )

    return values


def conservation_residual(
    before: Sequence[float],
    after: Sequence[float],
) -> float:
    """Return C_after - C_before for the quadratic scale content."""
    if len(before) != len(after):
        raise ValueError("before and after must have the same length")
    return quadratic_content(after) - quadratic_content(before)
