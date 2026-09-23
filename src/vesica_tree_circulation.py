"""Conservative circulation on Vesica ports and Flower-derived Tree routes.

This module answers one narrow creator question: what can circulate through a
Vesica and its inner/outer Tree while obeying a declared local conservation
law?

The conserved state is deliberately named ``content``.  It is a dimensionless
scalar placeholder, not an automatic identification with physical energy,
charge, consciousness, information, ether, or matter.

For a directed graph with edge current J_(a,b), the adopted convention is

    div J(a) = sum_b J_(a,b) - sum_b J_(b,a)

and the discrete continuity equation is

    d content(a) / dt + div J(a) = 0.

Every internal edge contributes once with each sign, so total content is
conserved exactly up to floating arithmetic.

The local Vesica cross-section has two axial edges through its neutral center
and two boundary-return channels.  Equal axial current with complementary
return currents is divergence free at both cusps and the neutral center.  This
is a minimal toroidal cross-section candidate, not evidence that a physical
Vesica or universe is a torus.

The Flower-derived Tree uses a normalized outward radial flow, its exact
inward reverse, and optional closed same-ring weave currents.  Recursive scale
transfer is represented by a separate address edge so it cannot be confused
with spatial Tree routing or with separately typed transitive-plane branching.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from .sevenfold_seed_contract import VesicaUniverseAddress
from .universe_port_engine import (
    AxialCoordinate,
    FlowerTreeGeometry,
    TreePillar,
    UniversePortState,
    axial_to_cartesian,
    hex_distance,
    tree_from_flower,
    tree_pillar,
)

_TOLERANCE = 1e-12


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive_time_step(dt: float) -> float:
    dt = _finite(dt, "dt")
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    return dt


def _clean_zero(value: float) -> float:
    return 0.0 if abs(value) <= _TOLERANCE else value


class FlowChannel(StrEnum):
    """Distinct current channels used by the circulation contract."""

    VESICA_AXIS_IN = "vesica_axis_in"
    VESICA_AXIS_OUT = "vesica_axis_out"
    VESICA_RETURN_UPPER = "vesica_return_upper"
    VESICA_RETURN_LOWER = "vesica_return_lower"
    TREE_OUTER = "tree_outer"
    TREE_INNER = "tree_inner"
    TREE_WEAVE = "tree_weave"
    PLANE_TRANSITION = "plane_transition"
    POSSIBILITY_BRANCH = "possibility_branch"
    POSSIBILITY_RETURN = "possibility_return"


@dataclass(frozen=True)
class DirectedCurrent[NodeT: Hashable]:
    """One oriented graph edge with a signed dimensionless content current."""

    source: NodeT
    target: NodeT
    current: float
    channel: FlowChannel

    def __post_init__(self) -> None:
        if self.source == self.target:
            raise ValueError("a current edge must connect distinct nodes")
        object.__setattr__(self, "current", _finite(self.current, "current"))

    def reversed(self) -> DirectedCurrent[NodeT]:
        """Reverse the edge while preserving its signed current value."""
        return DirectedCurrent(self.target, self.source, self.current, self.channel)


def graph_divergence[NodeT: Hashable](
    nodes: Sequence[NodeT],
    currents: Sequence[DirectedCurrent[NodeT]],
) -> dict[NodeT, float]:
    """Return outgoing minus incoming current at every graph node."""
    ordered_nodes = tuple(nodes)
    if len(set(ordered_nodes)) != len(ordered_nodes):
        raise ValueError("graph nodes must be unique")
    node_set = set(ordered_nodes)
    divergence = dict.fromkeys(ordered_nodes, 0.0)
    for edge in currents:
        if edge.source not in node_set or edge.target not in node_set:
            raise ValueError("every current endpoint must belong to the graph")
        divergence[edge.source] += edge.current
        divergence[edge.target] -= edge.current
    return divergence


def total_content[NodeT: Hashable](content: Mapping[NodeT, float]) -> float:
    """Return the total scalar content on a finite graph."""
    return math.fsum(_finite(value, "content") for value in content.values())


def continuity_step[NodeT: Hashable](
    nodes: Sequence[NodeT],
    content: Mapping[NodeT, float],
    currents: Sequence[DirectedCurrent[NodeT]],
    dt: float,
) -> dict[NodeT, float]:
    """Advance content by one explicit step of dQ/dt + div(J) = 0."""
    dt = _positive_time_step(dt)
    ordered_nodes = tuple(nodes)
    if set(content) != set(ordered_nodes):
        raise ValueError("content must contain exactly the graph nodes")
    divergence = graph_divergence(ordered_nodes, currents)
    return {
        node: _finite(content[node], "content") - dt * divergence[node] for node in ordered_nodes
    }


def continuity_residual[NodeT: Hashable](
    nodes: Sequence[NodeT],
    old_content: Mapping[NodeT, float],
    new_content: Mapping[NodeT, float],
    currents: Sequence[DirectedCurrent[NodeT]],
    dt: float,
) -> dict[NodeT, float]:
    """Return (Q_new-Q_old)/dt + div(J) at each node."""
    dt = _positive_time_step(dt)
    ordered_nodes = tuple(nodes)
    if set(old_content) != set(ordered_nodes) or set(new_content) != set(ordered_nodes):
        raise ValueError("old and new content must contain exactly the graph nodes")
    divergence = graph_divergence(ordered_nodes, currents)
    return {
        node: (
            _finite(new_content[node], "new content") - _finite(old_content[node], "old content")
        )
        / dt
        + divergence[node]
        for node in ordered_nodes
    }


def maximum_residual[NodeT: Hashable](values: Mapping[NodeT, float]) -> float:
    """Return the largest absolute value in a finite residual map."""
    return max((abs(_finite(value, "residual")) for value in values.values()), default=0.0)


class PortNode(StrEnum):
    """The two Vesica cusps and their neutral midpoint."""

    CUSP_A = "cusp_a"
    NEUTRAL = "neutral"
    CUSP_B = "cusp_b"


PORT_NODES = (PortNode.CUSP_A, PortNode.NEUTRAL, PortNode.CUSP_B)


@dataclass(frozen=True)
class VesicaCirculation:
    """One closed cusp-neutral-cusp circulation with two return channels."""

    through_current: float
    return_split: float
    edges: tuple[DirectedCurrent[PortNode], ...]

    @property
    def divergence(self) -> dict[PortNode, float]:
        return graph_divergence(PORT_NODES, self.edges)

    @property
    def balance_residual(self) -> float:
        return maximum_residual(self.divergence)


def vesica_circulation(
    through_current: float,
    return_split: float = 0.5,
) -> VesicaCirculation:
    """Build the minimal closed flow through a Vesica cross-section.

    ``return_split`` assigns the returning current between the two lens-side
    channels.  Any split in [0, 1] remains locally conservative because the
    two return currents sum to the axial through-current.
    """
    current = _finite(through_current, "through_current")
    split = _finite(return_split, "return_split")
    if not 0.0 <= split <= 1.0:
        raise ValueError("return_split must be in [0, 1]")
    edges = (
        DirectedCurrent(
            PortNode.CUSP_A,
            PortNode.NEUTRAL,
            current,
            FlowChannel.VESICA_AXIS_IN,
        ),
        DirectedCurrent(
            PortNode.NEUTRAL,
            PortNode.CUSP_B,
            current,
            FlowChannel.VESICA_AXIS_OUT,
        ),
        DirectedCurrent(
            PortNode.CUSP_B,
            PortNode.CUSP_A,
            split * current,
            FlowChannel.VESICA_RETURN_UPPER,
        ),
        DirectedCurrent(
            PortNode.CUSP_B,
            PortNode.CUSP_A,
            (1.0 - split) * current,
            FlowChannel.VESICA_RETURN_LOWER,
        ),
    )
    return VesicaCirculation(current, split, edges)


@dataclass(frozen=True)
class RecursiveScaleCurrent:
    """A signed current on one parent-child address edge.

    Positive current is directed from parent to child.  Negative current is
    directed from child to parent.  This is scale recursion, not spatial Tree
    routing and not transitive-plane branching.
    """

    parent: VesicaUniverseAddress
    child: VesicaUniverseAddress
    current: float

    def __post_init__(self) -> None:
        if self.child.depth != self.parent.depth + 1:
            raise ValueError("a scale edge must join adjacent address depths")
        if self.child.path[:-1] != self.parent.path:
            raise ValueError("the child address must extend the parent address")
        object.__setattr__(self, "current", _finite(self.current, "current"))

    @property
    def source(self) -> VesicaUniverseAddress | None:
        if self.current > 0.0:
            return self.parent
        if self.current < 0.0:
            return self.child
        return None

    @property
    def target(self) -> VesicaUniverseAddress | None:
        if self.current > 0.0:
            return self.child
        if self.current < 0.0:
            return self.parent
        return None


@dataclass(frozen=True)
class CanonicalPortCirculation:
    """Clock-locked local circulation and quadrature scale transfer."""

    state: UniversePortState
    amplitude: float
    local: VesicaCirculation
    scale: RecursiveScaleCurrent

    @property
    def quadrature_content(self) -> float:
        return self.local.through_current**2 + self.scale.current**2

    @property
    def quadrature_residual(self) -> float:
        return self.quadrature_content - self.amplitude**2


def canonical_port_circulation(
    state: UniversePortState,
    amplitude: float = 1.0,
    return_split: float = 0.5,
) -> CanonicalPortCirculation:
    """Couple one active port to the canonical polarity/transfer quadrature."""
    amplitude = _finite(amplitude, "amplitude")
    if amplitude < 0.0:
        raise ValueError("amplitude must be nonnegative")
    if not state.active:
        raise ValueError("canonical circulation requires an active port aperture")

    # Clean the dimensionless carriers before scaling so floating noise at an
    # exact quarter turn cannot grow into a false current at large amplitude.
    local_current = amplitude * _clean_zero(state.polarity_carrier)
    scale_current = amplitude * _clean_zero(state.transfer_carrier)
    parent = VesicaUniverseAddress(state.address.path[:-1])
    scale = RecursiveScaleCurrent(parent, state.address, scale_current)
    return CanonicalPortCirculation(
        state=state,
        amplitude=amplitude,
        local=vesica_circulation(local_current, return_split),
        scale=scale,
    )


def outward_tree_weights(
    geometry: FlowerTreeGeometry,
) -> tuple[tuple[tuple[AxialCoordinate, AxialCoordinate], float], ...]:
    """Split unit content conservatively from the center to the outer ring."""
    outgoing: dict[AxialCoordinate, list[AxialCoordinate]] = {node: [] for node in geometry.nodes}
    for source, target in geometry.outward_routes:
        outgoing[source].append(target)

    received = dict.fromkeys(geometry.nodes, 0.0)
    received[(0, 0)] = 1.0
    weights: dict[tuple[AxialCoordinate, AxialCoordinate], float] = {}
    for depth in range(geometry.rings):
        for source in (node for node in geometry.nodes if hex_distance(node) == depth):
            targets = tuple(sorted(outgoing[source]))
            if not targets:
                raise RuntimeError("an interior Tree node has no outward route")
            share = received[source] / len(targets)
            for target in targets:
                route = source, target
                weights[route] = share
                received[target] += share

    boundary_total = math.fsum(
        received[node] for node in geometry.nodes if hex_distance(node) == geometry.rings
    )
    if not math.isclose(boundary_total, 1.0, rel_tol=0.0, abs_tol=_TOLERANCE):
        raise RuntimeError("normalized outward Tree flow failed to reach the boundary")
    return tuple((route, weights[route]) for route in geometry.outward_routes)


def ring_cycle_routes(
    geometry: FlowerTreeGeometry,
    ring: int,
    handedness: int = 1,
) -> tuple[tuple[AxialCoordinate, AxialCoordinate], ...]:
    """Orient one same-radius Flower ring as a closed cycle."""
    if (
        not isinstance(ring, int)
        or isinstance(ring, bool)
        or ring not in range(1, geometry.rings + 1)
    ):
        raise ValueError("ring must select one noncentral Flower ring")
    if not isinstance(handedness, int) or isinstance(handedness, bool) or handedness not in (-1, 1):
        raise ValueError("handedness must be -1 or 1")

    nodes = [node for node in geometry.nodes if hex_distance(node) == ring]
    ordered = sorted(
        nodes,
        key=lambda node: math.atan2(*reversed(axial_to_cartesian(node))),
        reverse=handedness < 0,
    )
    routes = tuple(
        (source, ordered[(index + 1) % len(ordered)]) for index, source in enumerate(ordered)
    )
    expected = {
        frozenset(edge) for edge in geometry.transverse_edges if hex_distance(edge[0]) == ring
    }
    if {frozenset(route) for route in routes} != expected:
        raise RuntimeError("transverse Flower edges did not form one closed ring")
    return routes


@dataclass(frozen=True)
class TreeCirculation:
    """Matched outer/inner Tree currents plus closed transverse weave loops."""

    geometry: FlowerTreeGeometry
    radial_current: float
    weave_current: float
    weave_handedness: int
    outward_edges: tuple[DirectedCurrent[AxialCoordinate], ...]
    inward_edges: tuple[DirectedCurrent[AxialCoordinate], ...]
    weave_edges: tuple[DirectedCurrent[AxialCoordinate], ...]

    @property
    def edges(self) -> tuple[DirectedCurrent[AxialCoordinate], ...]:
        return self.outward_edges + self.inward_edges + self.weave_edges

    @property
    def divergence(self) -> dict[AxialCoordinate, float]:
        return graph_divergence(self.geometry.nodes, self.edges)

    @property
    def balance_residual(self) -> float:
        return maximum_residual(self.divergence)

    def radial_cut_flux(self, depth: int) -> float:
        """Return outward current crossing the cut from depth to depth+1."""
        if (
            not isinstance(depth, int)
            or isinstance(depth, bool)
            or depth not in range(self.geometry.rings)
        ):
            raise ValueError("depth must select an interior radial cut")
        return math.fsum(
            edge.current for edge in self.outward_edges if hex_distance(edge.source) == depth
        )

    def boundary_flux_by_pillar(self) -> dict[TreePillar, float]:
        """Resolve the normalized outward boundary current by three pillars."""
        flux = dict.fromkeys(TreePillar, 0.0)
        for edge in self.outward_edges:
            if hex_distance(edge.target) == self.geometry.rings:
                flux[tree_pillar(edge.target)] += edge.current
        return flux


def tree_circulation(
    rings: int = 2,
    radial_current: float = 1.0,
    weave_current: float = 0.0,
    weave_handedness: int = 1,
) -> TreeCirculation:
    """Build a divergence-free circulation on a Flower-derived Tree.

    The inner Tree is the exact reverse of the normalized outer Tree.  Optional
    same-ring weave currents are closed cycles, so they add circulation without
    adding or removing content at a node.
    """
    radial_current = _finite(radial_current, "radial_current")
    weave_current = _finite(weave_current, "weave_current")
    geometry = tree_from_flower(rings)
    weights = outward_tree_weights(geometry)
    outward = tuple(
        DirectedCurrent(source, target, radial_current * weight, FlowChannel.TREE_OUTER)
        for (source, target), weight in weights
    )
    inward = tuple(
        DirectedCurrent(target, source, radial_current * weight, FlowChannel.TREE_INNER)
        for (source, target), weight in weights
    )
    weave = tuple(
        DirectedCurrent(source, target, weave_current, FlowChannel.TREE_WEAVE)
        for ring in range(1, geometry.rings + 1)
        for source, target in ring_cycle_routes(geometry, ring, weave_handedness)
    )
    return TreeCirculation(
        geometry=geometry,
        radial_current=radial_current,
        weave_current=weave_current,
        weave_handedness=weave_handedness,
        outward_edges=outward,
        inward_edges=inward,
        weave_edges=weave,
    )
