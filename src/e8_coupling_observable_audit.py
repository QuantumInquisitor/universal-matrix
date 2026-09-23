"""Audit candidate scalar observables for the E8 invariant coupling.

If the E8 Cartan coordinate is restricted to the 240-root orbit, every root has
the same quadratic norm.  Therefore a coupling g ||h||^2 O cannot distinguish
which root orientation is present.

This module classifies the immediate consequence for existing scalar
observables: on a fixed root orbit the E8 factor is a constant multiplier and
the interaction is parameter-renormalization-like rather than a new
orientation-sensitive E8 dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .e8_state_audit import standard_root_state
from .higher_dimensional_geometry import e8_roots_scaled


class ObservableCouplingStatus(StrEnum):
    PARAMETER_RENORMALIZATION = "parameter_renormalization"
    SOURCE_SHIFT = "source_shift"
    DISTINCT_DYNAMICS_CANDIDATE = "distinct_dynamics_candidate"
    REQUIRES_NEW_E8_DEGREE = "requires_new_e8_degree"


@dataclass(frozen=True)
class ObservableCouplingAudit:
    observable: str
    status: ObservableCouplingStatus
    reason: str


def root_orbit_quadratic_invariants() -> tuple[float, ...]:
    """Return the distinct ||h||^2 values across all standard E8 roots."""
    return tuple(
        sorted(
            {
                float(standard_root_state(root).squared_norm)
                for root in e8_roots_scaled()
            }
        )
    )


def candidate_observable_audit() -> tuple[ObservableCouplingAudit, ...]:
    """Classify the first gauge-invariant scalar coupling candidates."""
    return (
        ObservableCouplingAudit(
            observable="u1_matter_norm",
            status=ObservableCouplingStatus.PARAMETER_RENORMALIZATION,
            reason=(
                "For fixed-root ||h||^2, coupling to |Phi|^2 has the same "
                "local field dependence as a shift of the U(1)-sector mass term."
            ),
        ),
        ObservableCouplingAudit(
            observable="su2_matter_norm",
            status=ObservableCouplingStatus.PARAMETER_RENORMALIZATION,
            reason=(
                "For fixed-root ||h||^2, coupling to Psi^dagger Psi has the same "
                "field dependence as a shift of the SU(2)-matter mass parameter."
            ),
        ),
        ObservableCouplingAudit(
            observable="su3_matter_norm",
            status=ObservableCouplingStatus.PARAMETER_RENORMALIZATION,
            reason=(
                "For fixed-root ||h||^2, coupling to Psi^dagger Psi has the same "
                "field dependence as a shift of the SU(3)-matter mass parameter."
            ),
        ),
        ObservableCouplingAudit(
            observable="gauge_energy_density",
            status=ObservableCouplingStatus.PARAMETER_RENORMALIZATION,
            reason=(
                "For fixed-root ||h||^2, multiplying a gauge kinetic or Wilson "
                "energy density only rescales its existing coupling coefficient."
            ),
        ),
        ObservableCouplingAudit(
            observable="neutral_reciprocity_or_content_scalar",
            status=ObservableCouplingStatus.SOURCE_SHIFT,
            reason=(
                "A linear scalar coupling with fixed-root ||h||^2 acts as a "
                "constant source or offset unless the E8 amplitude itself varies."
            ),
        ),
        ObservableCouplingAudit(
            observable="e8_orientation_sensitive_effect",
            status=ObservableCouplingStatus.REQUIRES_NEW_E8_DEGREE,
            reason=(
                "A Weyl-invariant scalar cannot distinguish members of one Weyl "
                "orbit. Orientation-sensitive dynamics requires either an E8-"
                "covariant partner or a new radial/amplitude degree of freedom."
            ),
        ),
    )


def admits_distinct_fixed_root_scalar_coupling() -> bool:
    """Return whether the audited fixed-root scalar couplings add new E8 dynamics."""
    return any(
        entry.status is ObservableCouplingStatus.DISTINCT_DYNAMICS_CANDIDATE
        for entry in candidate_observable_audit()
    )


if root_orbit_quadratic_invariants() != (8.0,):
    raise RuntimeError("all standard E8 roots must have the same quadratic norm")
if admits_distinct_fixed_root_scalar_coupling():
    raise RuntimeError(
        "no current fixed-root scalar coupling should be promoted as distinct E8 dynamics"
    )
