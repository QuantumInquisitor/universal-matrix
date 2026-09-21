"""Conservative neutral-crossing transfer between adjacent scale layers.

This experimental adapter uses the polarity transition carrier

    s(phi) = sin(phi)

to control transfer between neighboring scale amplitudes.

For a pair of signed amplitudes (a_l, a_u), one timestep applies an orthogonal
rotation

    [a_l']   [ cos d  -sin d ] [a_l]
    [a_u'] = [ sin d   cos d ] [a_u]

with

    d = kappa * sin(phi) * dt.

Consequences:
- transfer vanishes at polarity extrema, where sin(phi)=0;
- transfer is maximal at neutral crossings, where |sin(phi)|=1;
- reversing the transition direction reverses the rotation;
- the quadratic invariant a_l^2 + a_u^2 is conserved exactly up to floating
  arithmetic.

If physical energy is proportional to amplitude squared, this supplies a
reversible inter-scale energy-exchange candidate without creating or destroying
the conserved norm.

The sign convention is:
    sin(phi) > 0  -> lower-scale amplitude rotates toward upper scale;
    sin(phi) < 0  -> reverse direction.

That direction convention is an experimental orientation choice, not a
canonical theorem.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def crossing_carrier(phase: float) -> float:
    return math.sin(phase)


def transfer_angle(phase: float, coupling: float, dt: float) -> float:
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    if dt < 0:
        raise ValueError("dt must be non-negative")
    return coupling * crossing_carrier(phase) * dt


def transfer_pair(
    lower_amplitude: float,
    upper_amplitude: float,
    phase: float,
    coupling: float,
    dt: float,
) -> tuple[float, float]:
    """Apply one reversible conservative adjacent-scale transfer."""
    angle = transfer_angle(phase, coupling, dt)
    c = math.cos(angle)
    s = math.sin(angle)
    return (
        c * lower_amplitude - s * upper_amplitude,
        s * lower_amplitude + c * upper_amplitude,
    )


def quadratic_content(amplitudes: Sequence[float]) -> float:
    return math.fsum(float(a) * float(a) for a in amplitudes)


def transfer_chain(
    amplitudes: Sequence[float],
    edge_phases: Sequence[float],
    coupling: float,
    dt: float,
) -> list[float]:
    """Apply conservative nearest-neighbor rotations across a scale chain.

    edge_phases[i] controls the edge between layers i and i+1.

    A symmetric forward/reverse sweep is used to reduce ordering bias while
    keeping every local map orthogonal.
    """
    values = [float(a) for a in amplitudes]
    phases = [float(p) for p in edge_phases]

    if len(phases) != max(0, len(values) - 1):
        raise ValueError("edge_phases must have len(amplitudes)-1 entries")
    if coupling < 0:
        raise ValueError("coupling must be non-negative")
    if dt < 0:
        raise ValueError("dt must be non-negative")

    half_dt = 0.5 * dt

    for i, phase in enumerate(phases):
        values[i], values[i + 1] = transfer_pair(
            values[i],
            values[i + 1],
            phase,
            coupling,
            half_dt,
        )

    for i in range(len(phases) - 1, -1, -1):
        values[i], values[i + 1] = transfer_pair(
            values[i],
            values[i + 1],
            phases[i],
            coupling,
            half_dt,
        )

    return values


def directional_label(phase: float, tolerance: float = 1e-12) -> str:
    carrier = crossing_carrier(phase)
    if abs(carrier) <= tolerance:
        return "no-scale-transfer"
    return "micro-to-macro" if carrier > 0 else "macro-to-micro"
