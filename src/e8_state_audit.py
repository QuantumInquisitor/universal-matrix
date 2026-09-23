"""Audit of candidate Matrix state spaces against the E8 geometry layer.

The repository contains several objects with eight components.  Component
count alone is not enough to identify an E8 representation.

In particular, the SU(3) electric field has eight adjoint components because
dim su(3) = 8.  Those components already transform through SU(3) conjugation
and are not reinterpreted here as an E8 state.

This module therefore keeps a separate eight-coordinate Cartan/root-space state
for the finite E8 Weyl action.  That state is a representation-space candidate,
not a new physical degree of freedom.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from .higher_dimensional_geometry import e8_reflect, e8_roots_scaled


class E8StateFit(StrEnum):
    """Conservative classification of current repository state candidates."""

    NO_FIT = "no_fit"
    WEYL_SPACE_ONLY = "weyl_space_only"
    FULL_E8_REPRESENTATION = "full_e8_representation"


@dataclass(frozen=True)
class E8StateAuditEntry:
    name: str
    component_count: int | None
    fit: E8StateFit
    reason: str


def e8_state_audit() -> tuple[E8StateAuditEntry, ...]:
    """Return the current explicit state-space compatibility ledger."""
    return (
        E8StateAuditEntry(
            name="canonical_core_address",
            component_count=None,
            fit=E8StateFit.NO_FIT,
            reason=(
                "The exact canonical state is a Z_108 address with polarity "
                "structure, not an eight-dimensional linear vector."
            ),
        ),
        E8StateAuditEntry(
            name="stella_register_vertex_pair",
            component_count=6,
            fit=E8StateFit.NO_FIT,
            reason=(
                "The 8 x 8 register is an ordered pair of two three-coordinate "
                "cube vertices. Its count of eight vertex choices is not an "
                "eight-dimensional vector representation."
            ),
        ),
        E8StateAuditEntry(
            name="su3_electric_components",
            component_count=8,
            fit=E8StateFit.NO_FIT,
            reason=(
                "These eight components are coordinates in the SU(3) adjoint "
                "Lie algebra and already obey SU(3) gauge-conjugation dynamics."
            ),
        ),
        E8StateAuditEntry(
            name="h4_e8_coefficient_coordinates",
            component_count=8,
            fit=E8StateFit.WEYL_SPACE_ONLY,
            reason=(
                "These coordinates realize the rank-eight E8 root/Cartan space "
                "and support the finite Weyl reflection action exactly."
            ),
        ),
    )


Rational8 = tuple[
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
    Fraction,
]


@dataclass(frozen=True)
class E8CartanState:
    """Eight-coordinate internal state carrying only the E8 Weyl action.

    This type intentionally does not claim a full 248-dimensional E8 Lie-algebra
    representation.  It is suitable for root-space and Weyl-symmetry tests.
    """

    coordinates: Rational8

    def __post_init__(self) -> None:
        if len(self.coordinates) != 8:
            raise ValueError("E8 Cartan state must contain exactly eight coordinates")
        object.__setattr__(
            self,
            "coordinates",
            tuple(Fraction(component) for component in self.coordinates),
        )

    @property
    def squared_norm(self) -> Fraction:
        return sum(
            (component * component for component in self.coordinates),
            Fraction(0),
        )

    def central_mirror(self) -> "E8CartanState":
        return E8CartanState(tuple(-component for component in self.coordinates))

    def reflect_in_standard_root(self, root: tuple[int, ...]) -> "E8CartanState":
        """Apply one exact E8 Weyl reflection using a standard scaled root."""
        if root not in frozenset(e8_roots_scaled()):
            raise ValueError("root must belong to the standard E8 root system")

        root_fraction = tuple(Fraction(component) for component in root)
        dot_state_root = sum(
            (
                component * root_component
                for component, root_component in zip(
                    self.coordinates,
                    root_fraction,
                    strict=True,
                )
            ),
            Fraction(0),
        )
        root_norm = sum(
            (component * component for component in root_fraction),
            Fraction(0),
        )
        coefficient = 2 * dot_state_root / root_norm
        reflected = tuple(
            component - coefficient * root_component
            for component, root_component in zip(
                self.coordinates,
                root_fraction,
                strict=True,
            )
        )
        return E8CartanState(reflected)


def standard_root_state(root: tuple[int, ...]) -> E8CartanState:
    """Return one standard E8 root as a Cartan-state vector."""
    if root not in frozenset(e8_roots_scaled()):
        raise ValueError("root must belong to the standard E8 root system")
    return E8CartanState(tuple(Fraction(component) for component in root))


def root_reflection_matches_geometry(
    vector: tuple[int, ...],
    root: tuple[int, ...],
) -> bool:
    """Verify the Cartan-state reflection agrees with the geometry root action."""
    state_result = standard_root_state(vector).reflect_in_standard_root(root)
    geometry_result = e8_reflect(vector, root)
    return state_result.coordinates == tuple(Fraction(value) for value in geometry_result)


if any(
    entry.fit is E8StateFit.FULL_E8_REPRESENTATION
    for entry in e8_state_audit()
):
    raise RuntimeError(
        "no current Matrix state has established a full E8 representation"
    )
