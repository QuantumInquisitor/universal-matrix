"""Audit existing engine amplitudes as possible E8 radial degrees.

The goal is to avoid assigning a second meaning to an already committed state
variable merely to make the E8 Cartan norm dynamical.

Every candidate below already participates in another subsystem. Reusing it as
an E8 radius would therefore identify two logically distinct variables without
an independent derivation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class E8RadialFit(StrEnum):
    NO_FIT_ALREADY_COMMITTED = "no_fit_already_committed"
    OPEN_NEW_DEGREE_REQUIRED = "open_new_degree_required"


@dataclass(frozen=True)
class E8RadialAuditEntry:
    quantity: str
    fit: E8RadialFit
    reason: str


def e8_radial_degree_audit() -> tuple[E8RadialAuditEntry, ...]:
    """Return the current conservative audit of candidate radial variables."""
    return (
        E8RadialAuditEntry(
            quantity="matter_amplitude",
            fit=E8RadialFit.NO_FIT_ALREADY_COMMITTED,
            reason=(
                "Matter amplitude already controls the radial mode, localized "
                "matter structure, and matter-sector energy."
            ),
        ),
        E8RadialAuditEntry(
            quantity="port_circulation_amplitude",
            fit=E8RadialFit.NO_FIT_ALREADY_COMMITTED,
            reason=(
                "Port amplitude already sets Vesica, Tree, and scale-current "
                "circulation strength."
            ),
        ),
        E8RadialAuditEntry(
            quantity="nested_oscillatory_amplitude",
            fit=E8RadialFit.NO_FIT_ALREADY_COMMITTED,
            reason=(
                "Nested oscillatory amplitude already belongs to scale and "
                "polarity hierarchy dynamics."
            ),
        ),
        E8RadialAuditEntry(
            quantity="neutral_content_scalar",
            fit=E8RadialFit.NO_FIT_ALREADY_COMMITTED,
            reason=(
                "The neutral content scalar already has its own field equation, "
                "continuity role, and matter coupling."
            ),
        ),
        E8RadialAuditEntry(
            quantity="scale_level",
            fit=E8RadialFit.NO_FIT_ALREADY_COMMITTED,
            reason=(
                "Scale level is an address/hierarchy coordinate, not a continuous "
                "E8 Cartan radius."
            ),
        ),
        E8RadialAuditEntry(
            quantity="new_e8_radial_amplitude",
            fit=E8RadialFit.OPEN_NEW_DEGREE_REQUIRED,
            reason=(
                "Distinct E8 radial dynamics would require a new independently "
                "motivated degree of freedom rather than reusing an existing one."
            ),
        ),
    )


def existing_quantity_can_supply_e8_radius() -> bool:
    """Return whether an already-present quantity survives the no-duplication audit."""
    return any(
        entry.fit is not E8RadialFit.NO_FIT_ALREADY_COMMITTED
        and entry.quantity != "new_e8_radial_amplitude"
        for entry in e8_radial_degree_audit()
    )


if existing_quantity_can_supply_e8_radius():
    raise RuntimeError(
        "no existing engine quantity should currently be promoted to E8 radius"
    )
