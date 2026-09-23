"""Topology audit for the currently defined Sri Yantra contract.

The existing multidimensional module contains exact enclosure inventories,
cyclic local-member labels, an outer-to-inner shell order, and candidate
spherical and spiral-cone charts. It does not yet contain a sourced complete
intersection graph for all 43 triangular cells.

This module therefore tests only topology that is actually declared:
- the 72 abstract component locations across all nine enclosures;
- cyclic adjacency within each multi-member enclosure;
- the eight adjacent-enclosure shell interfaces;
- injectivity of the current spherical and spiral-cone candidate charts.

Unknown historical generator-intersection multiplicities are kept explicitly
unknown rather than inferred from component counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from .sri_yantra_multidimensional import (
    AvaranaId,
    CANONICAL_AVARANAS,
    SPIRAL_CONE_REALIZATION,
    FlowSense,
    RealizedYantraState,
    YantraFiberAddress,
    YantraLocation,
    candidate_spherical_shell_point,
    candidate_spiral_cone_point,
)
from .sevenfold_seed_contract import VesicaUniverseAddress
from .transitive_plane_branching import MATERIAL_PLANE, PlaneAddress


class IncidenceKnowledge(StrEnum):
    EXACT_DECLARED = "exact_declared"
    UNKNOWN_NOT_ENCODED = "unknown_not_encoded"


@dataclass(frozen=True)
class IncidenceAuditEntry:
    relation: str
    status: IncidenceKnowledge
    reason: str


def all_locations() -> tuple[YantraLocation, ...]:
    """Enumerate every abstract local component in the nine enclosures."""
    return tuple(
        YantraLocation(spec.identifier, member)
        for spec in CANONICAL_AVARANAS
        for member in range(spec.component_count)
    )


def total_location_count() -> int:
    """Return the total abstract component count across all enclosure kinds."""
    return len(all_locations())


def enclosure_interfaces() -> tuple[tuple[AvaranaId, AvaranaId], ...]:
    """Return the exact outer-to-inner path of adjacent enclosures."""
    identifiers = tuple(spec.identifier for spec in CANONICAL_AVARANAS)
    return tuple(zip(identifiers, identifiers[1:], strict=False))


def cyclic_neighbors(location: YantraLocation) -> tuple[YantraLocation, ...]:
    """Return same-enclosure cyclic neighbors from the declared member labelling."""
    count = location.member_count
    if count == 1:
        return ()
    if count == 2:
        return (YantraLocation(location.avarana, 1 - location.member),)
    return (
        YantraLocation(location.avarana, (location.member - 1) % count),
        YantraLocation(location.avarana, (location.member + 1) % count),
    )


def cyclic_edge_count() -> int:
    """Count undirected edges of all declared same-enclosure member cycles."""
    total = 0
    for spec in CANONICAL_AVARANAS:
        count = spec.component_count
        if count == 1:
            continue
        if count == 2:
            total += 1
        else:
            total += count
    return total


def incidence_audit() -> tuple[IncidenceAuditEntry, ...]:
    """Return the conservative topology-knowledge ledger."""
    return (
        IncidenceAuditEntry(
            "avarana_order",
            IncidenceKnowledge.EXACT_DECLARED,
            "Nine enclosures are explicitly ordered from outer boundary to bindu.",
        ),
        IncidenceAuditEntry(
            "same_enclosure_cyclic_member_adjacency",
            IncidenceKnowledge.EXACT_DECLARED,
            "Every enclosure member already has a cyclic integer label.",
        ),
        IncidenceAuditEntry(
            "adjacent_enclosure_shell_interfaces",
            IncidenceKnowledge.EXACT_DECLARED,
            "Shell currents explicitly join only consecutive enclosures.",
        ),
        IncidenceAuditEntry(
            "complete_43_triangle_intersection_graph",
            IncidenceKnowledge.UNKNOWN_NOT_ENCODED,
            "The current contract stores counts but no exact triangle-intersection incidence matrix.",
        ),
        IncidenceAuditEntry(
            "generator_pair_intersection_multiplicities",
            IncidenceKnowledge.UNKNOWN_NOT_ENCODED,
            "The four-up and five-down generator inventory does not specify exact pairwise intersections.",
        ),
        IncidenceAuditEntry(
            "historical_plane_spherical_meru_topological_equivalence",
            IncidenceKnowledge.UNKNOWN_NOT_ENCODED,
            "Exact coordinates and incidence-preserving maps for the historical realizations are not yet encoded.",
        ),
    )


def _default_base() -> PlaneAddress:
    """Return a stable existing base address without changing plane semantics."""
    return PlaneAddress(VesicaUniverseAddress(), MATERIAL_PLANE)


def spherical_location_points(
    phase: Fraction = Fraction(0),
) -> tuple[tuple[YantraLocation, tuple[float, float, float]], ...]:
    """Embed every abstract location in the current spherical shell chart."""
    base = _default_base()
    return tuple(
        (
            location,
            candidate_spherical_shell_point(
                YantraFiberAddress(base=base, location=location, phase=phase)
            ),
        )
        for location in all_locations()
    )


def spiral_cone_location_points(
    phase: Fraction = Fraction(0),
    radial_scale: float = 1.0,
    axial_height: float = 1.0,
) -> tuple[tuple[YantraLocation, tuple[float, float, float]], ...]:
    """Embed every abstract location in the current spiral-cone candidate chart."""
    base = _default_base()
    return tuple(
        (
            location,
            candidate_spiral_cone_point(
                RealizedYantraState(
                    address=YantraFiberAddress(base=base, location=location, phase=phase),
                    realization=SPIRAL_CONE_REALIZATION,
                    flow=FlowSense.STATIONARY,
                    handedness=1,
                ),
                radial_scale=radial_scale,
                axial_height=axial_height,
            ),
        )
        for location in all_locations()
    )


def _quantized_point(point: tuple[float, float, float], digits: int = 12) -> tuple[float, ...]:
    return tuple(round(component, digits) for component in point)


def chart_is_injective(points) -> bool:
    """Check whether every abstract location receives a distinct chart point."""
    embedded = tuple(_quantized_point(point) for _, point in points)
    return len(set(embedded)) == len(embedded)


def spherical_chart_is_injective() -> bool:
    return chart_is_injective(spherical_location_points())


def spiral_cone_chart_is_injective() -> bool:
    return chart_is_injective(spiral_cone_location_points())


def topology_change_detected_in_valid_candidate_charts() -> bool:
    """Return whether current valid candidate charts collapse declared locations."""
    return not (spherical_chart_is_injective() and spiral_cone_chart_is_injective())


if total_location_count() != 72:
    raise RuntimeError("the current nine-enclosure inventory must contain 72 abstract locations")
if len(enclosure_interfaces()) != 8:
    raise RuntimeError("nine ordered enclosures must have eight adjacent shell interfaces")
if topology_change_detected_in_valid_candidate_charts():
    raise RuntimeError("valid candidate charts must preserve all declared abstract locations")
