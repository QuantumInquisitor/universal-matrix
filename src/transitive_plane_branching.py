"""Typed plane overlap and possibility branching for the Omniverse candidate.

This module answers one narrow creator question: how can a state change its
named plane or branch into possibilities without silently moving to a
different recursive universe scale?

The address is a product of three independent coordinates:

    (recursive universe, named plane, possibility path).

A plane transition changes only the named plane and must follow one declared
overlap edge.  A possibility branch changes only the possibility path by one
outcome token.  Recursive scale changes only the universe path.  Mixed-axis
moves fail closed.

The branch law transports the same dimensionless ``content`` used by the
finite-graph continuity law in :mod:`src.vesica_tree_circulation`.  Mirrored
outcomes use integer labels ``-k`` and ``+k`` while ``0`` is neutral.  A
mirror-symmetric branch requires equal weights for each signed pair.  The
number of pairs is open, so the smallest branch has three outcomes and a
six-plus-one branch can be represented by three pairs and a neutral center.

These are exact software and finite-graph statements under the declared
model.  Plane names and the example Chapter 8 overlap map preserve conceptual
provenance; they do not establish extra physical dimensions, quantum effects,
consciousness dynamics, spirits, or parallel universes as empirical facts.
"""

from __future__ import annotations

import math
import re
from collections import deque
from dataclasses import dataclass
from enum import StrEnum

from .sevenfold_seed_contract import VesicaUniverseAddress, mirror_vesica_address
from .vesica_tree_circulation import (
    DirectedCurrent,
    FlowChannel,
    graph_divergence,
    maximum_residual,
)

_TOLERANCE = 1e-12
_PLANE_KEY = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*\Z")


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _outcome_token(value: int, name: str = "outcome") -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return value


@dataclass(frozen=True, order=True)
class PlaneId:
    """Open, canonical identifier for one named plane in a declared topology."""

    key: str

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or _PLANE_KEY.fullmatch(self.key) is None:
            raise ValueError("plane key must be a lowercase snake-case identifier")


MATERIAL_PLANE = PlaneId("material")
MENTAL_PLANE = PlaneId("mental")
DREAM_PLANE = PlaneId("dream")
ASTRAL_PLANE = PlaneId("astral")
ETHERIC_PLANE = PlaneId("etheric")
SPIRIT_PLANE = PlaneId("spirit")
PSYCHIC_PLANE = PlaneId("psychic")
PROBABILITY_PLANE = PlaneId("probability")

CHAPTER_EIGHT_TRANSITIVE_PLANES = frozenset((ASTRAL_PLANE, ETHERIC_PLANE, DREAM_PLANE))


@dataclass(frozen=True, order=True)
class PossibilityAddress:
    """A path of signed outcome tokens, independent of recursive scale depth."""

    path: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.path, tuple):
            raise TypeError("possibility path must be a tuple")
        for outcome in self.path:
            _outcome_token(outcome)

    @property
    def depth(self) -> int:
        return len(self.path)

    def child(self, outcome: int) -> PossibilityAddress:
        """Append one outcome without changing plane or universe scale."""
        return PossibilityAddress(self.path + (_outcome_token(outcome),))


def mirror_possibility_address(address: PossibilityAddress) -> PossibilityAddress:
    """Exchange every positive/negative outcome while preserving neutral zero."""
    if not isinstance(address, PossibilityAddress):
        raise TypeError("address must be a PossibilityAddress")
    return PossibilityAddress(tuple(-outcome for outcome in address.path))


@dataclass(frozen=True, order=True)
class PlaneAddress:
    """One state in universe-scale x named-plane x possibility space."""

    universe: VesicaUniverseAddress
    plane: PlaneId
    possibility: PossibilityAddress = PossibilityAddress()

    def __post_init__(self) -> None:
        if not isinstance(self.universe, VesicaUniverseAddress):
            raise TypeError("universe must be a VesicaUniverseAddress")
        if not isinstance(self.plane, PlaneId):
            raise TypeError("plane must be a PlaneId")
        if not isinstance(self.possibility, PossibilityAddress):
            raise TypeError("possibility must be a PossibilityAddress")

    @property
    def scale_depth(self) -> int:
        return self.universe.depth

    @property
    def branch_depth(self) -> int:
        return self.possibility.depth

    def on_plane(self, plane: PlaneId) -> PlaneAddress:
        """Change only the named-plane coordinate."""
        return PlaneAddress(self.universe, plane, self.possibility)

    def branch(self, outcome: int) -> PlaneAddress:
        """Change only the possibility coordinate by one branch step."""
        return PlaneAddress(self.universe, self.plane, self.possibility.child(outcome))


def mirror_plane_address(address: PlaneAddress) -> PlaneAddress:
    """Apply the central universe mirror and signed possibility mirror together."""
    if not isinstance(address, PlaneAddress):
        raise TypeError("address must be a PlaneAddress")
    return PlaneAddress(
        mirror_vesica_address(address.universe),
        address.plane,
        mirror_possibility_address(address.possibility),
    )


class AddressRelation(StrEnum):
    """The one coordinate changed by an admissible elementary move."""

    SAME_STATE = "same_state"
    RECURSIVE_SCALE = "recursive_scale"
    PLANE_TRANSITION = "plane_transition"
    POSSIBILITY_BRANCH = "possibility_branch"


def _paths_are_adjacent(first: tuple[int, ...], second: tuple[int, ...]) -> bool:
    return (
        len(second) == len(first) + 1
        and second[:-1] == first
        or len(first) == len(second) + 1
        and first[:-1] == second
    )


def classify_address_relation(source: PlaneAddress, target: PlaneAddress) -> AddressRelation:
    """Classify a one-axis move and reject mixed or nonadjacent changes."""
    if not isinstance(source, PlaneAddress) or not isinstance(target, PlaneAddress):
        raise TypeError("source and target must be PlaneAddress values")

    universe_changed = source.universe != target.universe
    plane_changed = source.plane != target.plane
    possibility_changed = source.possibility != target.possibility
    change_count = sum((universe_changed, plane_changed, possibility_changed))

    if change_count == 0:
        return AddressRelation.SAME_STATE
    if change_count != 1:
        raise ValueError("an elementary move must change exactly one address coordinate")
    if universe_changed:
        if not _paths_are_adjacent(source.universe.path, target.universe.path):
            raise ValueError("a recursive-scale move must join adjacent universe depths")
        return AddressRelation.RECURSIVE_SCALE
    if plane_changed:
        return AddressRelation.PLANE_TRANSITION
    if not _paths_are_adjacent(source.possibility.path, target.possibility.path):
        raise ValueError("a possibility branch must join adjacent branch depths")
    return AddressRelation.POSSIBILITY_BRANCH


class PlaneLinkKind(StrEnum):
    """Declared geometric meaning of a direct plane adjacency."""

    OVERLAP = "overlap"
    COEXISTENT = "coexistent"


@dataclass(frozen=True, order=True)
class PlaneLink:
    """One undirected, explicitly declared adjacency between named planes."""

    first: PlaneId
    second: PlaneId
    kind: PlaneLinkKind = PlaneLinkKind.OVERLAP

    def __post_init__(self) -> None:
        if not isinstance(self.first, PlaneId) or not isinstance(self.second, PlaneId):
            raise TypeError("plane-link endpoints must be PlaneId values")
        if self.first == self.second:
            raise ValueError("a plane link must join two distinct planes")
        if not isinstance(self.kind, PlaneLinkKind):
            raise TypeError("kind must be a PlaneLinkKind")
        if self.second < self.first:
            first, second = self.second, self.first
            object.__setattr__(self, "first", first)
            object.__setattr__(self, "second", second)

    @property
    def endpoints(self) -> frozenset[PlaneId]:
        return frozenset((self.first, self.second))

    def other(self, plane: PlaneId) -> PlaneId:
        if plane == self.first:
            return self.second
        if plane == self.second:
            return self.first
        raise ValueError("plane is not an endpoint of this link")


@dataclass(frozen=True)
class PlaneTransition:
    """A content current across one overlap at fixed universe and possibility."""

    source: PlaneAddress
    target: PlaneAddress
    current: float
    link: PlaneLink

    def __post_init__(self) -> None:
        if (
            classify_address_relation(self.source, self.target)
            is not AddressRelation.PLANE_TRANSITION
        ):
            raise ValueError("a plane transition must change only the named-plane coordinate")
        if frozenset((self.source.plane, self.target.plane)) != self.link.endpoints:
            raise ValueError("the declared link does not connect the transition planes")
        object.__setattr__(self, "current", _finite(self.current, "current"))

    @property
    def edge(self) -> DirectedCurrent[PlaneAddress]:
        return DirectedCurrent(
            self.source,
            self.target,
            self.current,
            FlowChannel.PLANE_TRANSITION,
        )


@dataclass(frozen=True)
class PlaneTopology:
    """Finite overlap graph; indirect travel must use an explicit graph path."""

    planes: tuple[PlaneId, ...]
    links: tuple[PlaneLink, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.planes, tuple) or not isinstance(self.links, tuple):
            raise TypeError("planes and links must be tuples")
        if any(not isinstance(plane, PlaneId) for plane in self.planes):
            raise TypeError("every topology node must be a PlaneId")
        if any(not isinstance(link, PlaneLink) for link in self.links):
            raise TypeError("every topology edge must be a PlaneLink")
        if len(set(self.planes)) != len(self.planes):
            raise ValueError("topology planes must be unique")
        plane_set = set(self.planes)
        if any(not link.endpoints <= plane_set for link in self.links):
            raise ValueError("every link endpoint must belong to the topology")
        endpoint_sets = [link.endpoints for link in self.links]
        if len(set(endpoint_sets)) != len(endpoint_sets):
            raise ValueError("only one direct link may join a plane pair")

    def link_between(self, first: PlaneId, second: PlaneId) -> PlaneLink | None:
        endpoints = frozenset((first, second))
        return next((link for link in self.links if link.endpoints == endpoints), None)

    def neighbors(self, plane: PlaneId) -> tuple[PlaneId, ...]:
        if plane not in self.planes:
            raise ValueError("plane does not belong to this topology")
        return tuple(sorted(link.other(plane) for link in self.links if plane in link.endpoints))

    def shortest_route(self, source: PlaneId, target: PlaneId) -> tuple[PlaneId, ...]:
        """Return a deterministic shortest overlap path, including both endpoints."""
        if source not in self.planes or target not in self.planes:
            raise ValueError("route endpoints must belong to this topology")
        if source == target:
            return (source,)

        queue = deque((source,))
        predecessor: dict[PlaneId, PlaneId | None] = {source: None}
        while queue:
            plane = queue.popleft()
            for neighbor in self.neighbors(plane):
                if neighbor in predecessor:
                    continue
                predecessor[neighbor] = plane
                if neighbor == target:
                    route = [target]
                    while predecessor[route[-1]] is not None:
                        route.append(predecessor[route[-1]])  # type: ignore[arg-type]
                    return tuple(reversed(route))
                queue.append(neighbor)
        raise ValueError("no declared overlap route connects the requested planes")

    def transition(
        self,
        source: PlaneAddress,
        target: PlaneAddress,
        current: float,
    ) -> PlaneTransition:
        if not isinstance(source, PlaneAddress) or not isinstance(target, PlaneAddress):
            raise TypeError("source and target must be PlaneAddress values")
        if (
            source.universe != target.universe
            or source.possibility != target.possibility
            or source.plane == target.plane
        ):
            raise ValueError("a direct plane transition must change only the plane coordinate")
        link = self.link_between(source.plane, target.plane)
        if link is None:
            raise ValueError("plane transition requires a declared direct overlap")
        return PlaneTransition(source, target, current, link)


def route_plane_current(
    topology: PlaneTopology,
    source: PlaneAddress,
    target_plane: PlaneId,
    current: float,
) -> tuple[PlaneTransition, ...]:
    """Route current through every required intermediary at one fixed address."""
    current = _finite(current, "current")
    route = topology.shortest_route(source.plane, target_plane)
    addresses = tuple(source.on_plane(plane) for plane in route)
    return tuple(
        topology.transition(first, second, current)
        for first, second in zip(addresses, addresses[1:], strict=False)
    )


def chapter_eight_overlap_topology() -> PlaneTopology:
    """Return the minimal overlap map explicitly stated in Chapter 8.

    The map records conceptual provenance only.  In particular, the psychic
    plane remains an isolated named node because the chapter names it but does
    not give it one of the explicit overlap relations encoded here.
    """
    planes = tuple(
        sorted(
            (
                MATERIAL_PLANE,
                MENTAL_PLANE,
                DREAM_PLANE,
                ASTRAL_PLANE,
                ETHERIC_PLANE,
                SPIRIT_PLANE,
                PSYCHIC_PLANE,
                PROBABILITY_PLANE,
            )
        )
    )
    crossings = (
        (DREAM_PLANE, ETHERIC_PLANE),
        (DREAM_PLANE, ASTRAL_PLANE),
        (DREAM_PLANE, MENTAL_PLANE),
        (DREAM_PLANE, SPIRIT_PLANE),
        (PROBABILITY_PLANE, ETHERIC_PLANE),
        (PROBABILITY_PLANE, ASTRAL_PLANE),
        (PROBABILITY_PLANE, MENTAL_PLANE),
        (PROBABILITY_PLANE, SPIRIT_PLANE),
        (MATERIAL_PLANE, ASTRAL_PLANE),
        (MATERIAL_PLANE, ETHERIC_PLANE),
        (ETHERIC_PLANE, SPIRIT_PLANE),
    )
    return PlaneTopology(planes, tuple(PlaneLink(*crossing) for crossing in crossings))


@dataclass(frozen=True)
class PossibilityBranch:
    """One mirror-symmetric split at fixed universe scale and named plane."""

    parent: PlaneAddress
    through_current: float
    weights: tuple[tuple[int, float], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.parent, PlaneAddress):
            raise TypeError("parent must be a PlaneAddress")
        current = _finite(self.through_current, "through_current")
        if current < 0.0:
            raise ValueError("through_current must be nonnegative")
        object.__setattr__(self, "through_current", current)
        if not isinstance(self.weights, tuple) or not self.weights:
            raise ValueError("weights must be a nonempty tuple")

        normalized: list[tuple[int, float]] = []
        for item in self.weights:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError("every branch weight must be an (outcome, weight) tuple")
            outcome, weight = item
            normalized.append((_outcome_token(outcome), _finite(weight, "branch weight")))
        normalized.sort()
        if any(weight < 0.0 for _, weight in normalized):
            raise ValueError("branch weights must be nonnegative")
        if len({outcome for outcome, _ in normalized}) != len(normalized):
            raise ValueError("branch outcomes must be unique")
        weight_map = dict(normalized)
        if 0 not in weight_map or len(weight_map) < 3:
            raise ValueError("a symmetric branch needs neutral zero and at least one pair")
        if set(weight_map) != {-outcome for outcome in weight_map}:
            raise ValueError("branch outcomes must be closed under sign mirroring")
        if any(
            not math.isclose(weight, weight_map[-outcome], rel_tol=0.0, abs_tol=_TOLERANCE)
            for outcome, weight in normalized
        ):
            raise ValueError("mirrored outcomes must have equal weights")
        if not math.isclose(
            math.fsum(weight_map.values()),
            1.0,
            rel_tol=0.0,
            abs_tol=_TOLERANCE,
        ):
            raise ValueError("branch weights must sum to one")
        object.__setattr__(self, "weights", tuple(normalized))

    @property
    def children(self) -> tuple[PlaneAddress, ...]:
        return tuple(self.parent.branch(outcome) for outcome, _ in self.weights)

    @property
    def nodes(self) -> tuple[PlaneAddress, ...]:
        return (self.parent,) + self.children

    @property
    def outward_edges(self) -> tuple[DirectedCurrent[PlaneAddress], ...]:
        return tuple(
            DirectedCurrent(
                self.parent,
                self.parent.branch(outcome),
                self.through_current * weight,
                FlowChannel.POSSIBILITY_BRANCH,
            )
            for outcome, weight in self.weights
        )

    @property
    def return_edges(self) -> tuple[DirectedCurrent[PlaneAddress], ...]:
        return tuple(
            DirectedCurrent(
                edge.target,
                edge.source,
                edge.current,
                FlowChannel.POSSIBILITY_RETURN,
            )
            for edge in self.outward_edges
        )

    @property
    def closed_edges(self) -> tuple[DirectedCurrent[PlaneAddress], ...]:
        return self.outward_edges + self.return_edges

    @property
    def branch_cut_flux(self) -> float:
        return math.fsum(edge.current for edge in self.outward_edges)

    @property
    def balance_residual(self) -> float:
        return maximum_residual(graph_divergence(self.nodes, self.closed_edges))


def symmetric_possibility_branch(
    parent: PlaneAddress,
    through_current: float = 1.0,
    pair_count: int = 1,
    neutral_share: float | None = None,
) -> PossibilityBranch:
    """Build equal mirror pairs plus a neutral outcome.

    With ``pair_count=1`` this gives three outcomes.  With ``pair_count=3`` it
    gives six signed outcomes plus neutral.  If ``neutral_share`` is omitted,
    all ``2 * pair_count + 1`` outcomes receive equal weight.
    """
    if not isinstance(pair_count, int) or isinstance(pair_count, bool) or pair_count < 1:
        raise ValueError("pair_count must be a positive integer")
    if neutral_share is None:
        neutral_share = 1.0 / (2 * pair_count + 1)
    neutral_share = _finite(neutral_share, "neutral_share")
    if not 0.0 <= neutral_share <= 1.0:
        raise ValueError("neutral_share must be in [0, 1]")
    signed_share = (1.0 - neutral_share) / (2 * pair_count)
    weights = tuple(
        (outcome, neutral_share if outcome == 0 else signed_share)
        for outcome in range(-pair_count, pair_count + 1)
    )
    return PossibilityBranch(parent, through_current, weights)


def mirror_possibility_branch(branch: PossibilityBranch) -> PossibilityBranch:
    """Mirror the parent and every signed child while preserving branch current."""
    if not isinstance(branch, PossibilityBranch):
        raise TypeError("branch must be a PossibilityBranch")
    return PossibilityBranch(
        mirror_plane_address(branch.parent),
        branch.through_current,
        tuple((-outcome, weight) for outcome, weight in branch.weights),
    )
