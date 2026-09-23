"""Minimal gauge-compatible scalar coupling for the E8 Cartan/Weyl layer.

The only E8 quantity used here is the quadratic Cartan norm ||h||^2.  It is
invariant under every Weyl reflection.  The coupling multiplies that invariant
by an already gauge-invariant scalar observable from another engine sector.

No direct E8 action is applied to U(1), SU(2), or SU(3) fields.  This preserves
their established gauge transformation laws and keeps the E8 coordinate as an
optional internal singlet with respect to those gauge groups.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .e8_state_audit import E8CartanState


@dataclass(frozen=True)
class E8ScalarCoupling:
    """Candidate scalar interaction coefficient."""

    strength: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.strength):
            raise ValueError("strength must be finite")


def e8_quadratic_invariant(state: E8CartanState) -> float:
    """Return the exact Cartan norm converted to a finite scalar."""
    value = float(state.squared_norm)
    if not math.isfinite(value):
        raise ValueError("E8 invariant must be finite")
    return value


def invariant_scalar_coupling(
    state: E8CartanState,
    gauge_invariant_scalar: float,
    coupling: E8ScalarCoupling,
) -> float:
    """Return g ||h||^2 O for an already gauge-invariant scalar O."""
    observable = float(gauge_invariant_scalar)
    if not math.isfinite(observable):
        raise ValueError("gauge_invariant_scalar must be finite")
    return coupling.strength * e8_quadratic_invariant(state) * observable


def scalar_coupling_is_weyl_invariant(
    state: E8CartanState,
    root: tuple[int, ...],
    gauge_invariant_scalar: float,
    coupling: E8ScalarCoupling,
) -> bool:
    """Check invariance of the candidate coupling under one E8 Weyl reflection."""
    before = invariant_scalar_coupling(state, gauge_invariant_scalar, coupling)
    after_state = state.reflect_in_standard_root(root)
    after = invariant_scalar_coupling(after_state, gauge_invariant_scalar, coupling)
    return before == after
