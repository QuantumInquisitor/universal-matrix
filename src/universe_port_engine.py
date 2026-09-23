"""Exact Flower geometry and candidate dynamics for recursive universe ports.

The geometric part of this module follows a deliberately narrow contract:

* a circle is a vessel with a distinct interior;
* a contained Seed is one central circle plus six equal surrounding circles;
* every adjacent pair of Seed circles defines a Vesica universe domain and port;
* the largest circle centered in that Vesica is its internal recursion vessel;
* every recursion vessel contains a complete, smaller Seed and therefore twelve
  further ports.

The equal-circle Flower grows outward without changing circle radius.  The
contained recursion grows inward by a factor of four in vessel radius: Seed
circles have half their container's radius, and the circle inscribed at a
Vesica midpoint has half the Seed-circle radius.  Keeping these operations
separate prevents outward Flower growth from being confused with inward scale
nesting.

The polarity clock, 108-state routing, and Terryen negative-space cavity are
candidate adapters layered onto the exact geometry.  They are useful testable
models, not evidence that a mathematical port is a physical universe, black
hole, gravity mechanism, ether, or cosmological structure.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .canonical_kernel import polarity, route
from .canonical_polarity_clock import polarity_phase_from_tick
from .canonical_scale_transfer import (
    alternating_polarity_carrier,
    alternating_transfer_carrier,
    scale_orientation,
)
from .sevenfold_seed_contract import (
    VesicaUniverseAddress,
    mirror_vesica_address,
    seed_vesicas,
)
from .terryen_negative_space import (
    NegativeSpaceWindow,
    cech_topology,
    terryen_negative_space_window,
)

Point2D = tuple[float, float]
AxialCoordinate = tuple[int, int]
DirectedRoute = tuple[AxialCoordinate, AxialCoordinate]

SEED_CIRCLE_SCALE = 0.5
VESICA_INSCRIBED_SCALE = 0.5
CONTAINED_RECURSION_SCALE = SEED_CIRCLE_SCALE * VESICA_INSCRIBED_SCALE
VESICAS_PER_SEED = 12

_TOLERANCE = 1e-12
_SEED_AXIAL_COORDINATES: tuple[AxialCoordinate, ...] = (
    (0, 0),
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (0, -1),
    (1, -1),
)
_HEX_DIRECTIONS: tuple[AxialCoordinate, ...] = (
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (0, -1),
    (1, -1),
)


def _point2d(point: tuple[float, float]) -> Point2D:
    if len(point) != 2:
        raise ValueError("a planar point must have two coordinates")
    values = (float(point[0]), float(point[1]))
    if not all(math.isfinite(value) for value in values):
        raise ValueError("point coordinates must be finite")
    return values


def _distance(left: Point2D, right: Point2D) -> float:
    return math.hypot(left[0] - right[0], left[1] - right[1])


def _validate_orientation(orientation: int) -> None:
    if (
        not isinstance(orientation, int)
        or isinstance(orientation, bool)
        or orientation not in (-1, 1)
    ):
        raise ValueError("orientation must be -1 or 1")


def _validate_nonnegative_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


@dataclass(frozen=True)
class CircleVessel:
    """A planar circular shell and its distinct interior domain."""

    center: Point2D = (0.0, 0.0)
    radius: float = 1.0

    def __post_init__(self) -> None:
        center = _point2d(self.center)
        radius = float(self.radius)
        if not math.isfinite(radius) or radius <= 0.0:
            raise ValueError("a vessel radius must be finite and positive")
        object.__setattr__(self, "center", center)
        object.__setattr__(self, "radius", radius)

    def shell_residual(self, point: Point2D) -> float:
        """Return distance from the center minus the shell radius."""
        return _distance(self.center, _point2d(point)) - self.radius

    def contains_point(self, point: Point2D, tolerance: float = _TOLERANCE) -> bool:
        """Return whether a point lies in the closed vessel."""
        return self.shell_residual(point) <= tolerance

    def contains_circle(
        self,
        circle: CircleVessel,
        tolerance: float = _TOLERANCE,
    ) -> bool:
        """Return whether another closed circle is contained by this vessel."""
        return _distance(self.center, circle.center) + circle.radius <= self.radius + tolerance


DEFAULT_ROOT_VESSEL = CircleVessel()


def axial_to_cartesian(
    coordinate: AxialCoordinate,
    spacing: float = 1.0,
    origin: Point2D = (0.0, 0.0),
    orientation: int = 1,
) -> Point2D:
    """Map a hexagonal axial coordinate to an equal-spacing planar lattice."""
    q, r = coordinate
    if (
        not isinstance(q, int)
        or isinstance(q, bool)
        or not isinstance(r, int)
        or isinstance(r, bool)
    ):
        raise ValueError("axial coordinates must be integers")
    spacing = float(spacing)
    if not math.isfinite(spacing) or spacing <= 0.0:
        raise ValueError("spacing must be finite and positive")
    origin = _point2d(origin)
    _validate_orientation(orientation)
    x = spacing * (q + r / 2.0)
    y = spacing * (math.sqrt(3.0) / 2.0) * r
    return origin[0] + orientation * x, origin[1] + orientation * y


def hex_distance(coordinate: AxialCoordinate) -> int:
    """Return graph distance from the origin on the axial hexagonal lattice."""
    q, r = coordinate
    return max(abs(q), abs(r), abs(q + r))


def central_mirror_point(point: Point2D, center: Point2D = (0.0, 0.0)) -> Point2D:
    """Mirror a point through a chosen center."""
    point = _point2d(point)
    center = _point2d(center)
    return 2.0 * center[0] - point[0], 2.0 * center[1] - point[1]


def seed_circles(
    container: CircleVessel,
    orientation: int = 1,
) -> tuple[CircleVessel, ...]:
    """Place one complete seven-circle Seed inside a circular vessel.

    Each Seed circle has half the container radius.  Ring centers are one Seed
    radius from the common center, so all seven circles remain in the vessel.
    """
    _validate_orientation(orientation)
    radius = container.radius * SEED_CIRCLE_SCALE
    circles = tuple(
        CircleVessel(
            axial_to_cartesian(
                coordinate,
                spacing=radius,
                origin=container.center,
                orientation=orientation,
            ),
            radius,
        )
        for coordinate in _SEED_AXIAL_COORDINATES
    )
    if not all(container.contains_circle(circle) for circle in circles):
        raise RuntimeError("contained Seed construction escaped its vessel")
    return circles


@dataclass(frozen=True)
class VesicaPortGeometry:
    """Exact equal-circle geometry for one Seed overlap."""

    vesica_index: int
    seed_positions: tuple[int, int]
    parent_vessel: CircleVessel
    generator_circles: tuple[CircleVessel, CircleVessel]
    neutral_center: Point2D
    cusp_points: tuple[Point2D, Point2D]
    minor_axis_length: float
    major_axis_length: float
    lens_area: float
    child_vessel: CircleVessel

    @property
    def contained(self) -> bool:
        """Whether the child circle lies in both generators and its parent."""
        return self.parent_vessel.contains_circle(self.child_vessel) and all(
            generator.contains_circle(self.child_vessel) for generator in self.generator_circles
        )


def seed_vesica_geometry(
    container: CircleVessel,
    vesica_index: int,
    orientation: int = 1,
) -> VesicaPortGeometry:
    """Construct one of a contained Seed's twelve Vesica universe ports."""
    vesicas = seed_vesicas()
    if vesica_index not in range(len(vesicas)):
        raise ValueError(f"vesica_index must be in 0..{len(vesicas) - 1}")
    _validate_orientation(orientation)

    circles = seed_circles(container, orientation)
    positions = vesicas[vesica_index]
    first, second = (circles[position] for position in positions)
    radius = first.radius
    dx = second.center[0] - first.center[0]
    dy = second.center[1] - first.center[1]
    separation = math.hypot(dx, dy)
    if not math.isclose(separation, radius, rel_tol=0.0, abs_tol=_TOLERANCE):
        raise RuntimeError("Seed neighbors must meet at one generator radius")

    axis = (dx / separation, dy / separation)
    transverse = (-axis[1], axis[0])
    midpoint = (
        (first.center[0] + second.center[0]) / 2.0,
        (first.center[1] + second.center[1]) / 2.0,
    )
    half_major_axis = math.sqrt(radius * radius - (separation / 2.0) ** 2)
    cusps = (
        (
            midpoint[0] + half_major_axis * transverse[0],
            midpoint[1] + half_major_axis * transverse[1],
        ),
        (
            midpoint[0] - half_major_axis * transverse[0],
            midpoint[1] - half_major_axis * transverse[1],
        ),
    )
    child = CircleVessel(midpoint, radius - separation / 2.0)
    geometry = VesicaPortGeometry(
        vesica_index=vesica_index,
        seed_positions=positions,
        parent_vessel=container,
        generator_circles=(first, second),
        neutral_center=midpoint,
        cusp_points=cusps,
        minor_axis_length=2.0 * radius - separation,
        major_axis_length=2.0 * half_major_axis,
        lens_area=(2.0 * math.pi / 3.0 - math.sqrt(3.0) / 2.0) * radius * radius,
        child_vessel=child,
    )
    if not geometry.contained:
        raise RuntimeError("Vesica child construction escaped its containing geometry")
    return geometry


def recursive_universe_count(depth: int) -> int:
    """Return the number of distinct Vesica addresses at an exact depth."""
    _validate_nonnegative_integer(depth, "depth")
    return VESICAS_PER_SEED**depth


def universe_domain(
    address: VesicaUniverseAddress,
    root_vessel: CircleVessel = DEFAULT_ROOT_VESSEL,
) -> CircleVessel:
    """Return the nested Seed vessel carried by a recursive Vesica address.

    Each nonempty address itself identifies a Vesica lens domain.  The returned
    circle is the maximal centered vessel used to contain that domain's next
    Seed, rather than a replacement for the lens.
    """
    current = root_vessel
    for parent_depth, vesica_index in enumerate(address.path):
        port = seed_vesica_geometry(
            current,
            vesica_index,
            orientation=scale_orientation(parent_depth),
        )
        current = port.child_vessel
    return current


def universe_port_geometry(
    address: VesicaUniverseAddress,
    root_vessel: CircleVessel = DEFAULT_ROOT_VESSEL,
) -> VesicaPortGeometry:
    """Return the final port selected by a nonempty recursive address."""
    if not address.path:
        raise ValueError("a port address must select at least one Vesica")
    parent = universe_domain(VesicaUniverseAddress(address.path[:-1]), root_vessel)
    parent_depth = address.depth - 1
    return seed_vesica_geometry(
        parent,
        address.path[-1],
        orientation=scale_orientation(parent_depth),
    )


def mirror_universe_address(address: VesicaUniverseAddress) -> VesicaUniverseAddress:
    """Expose the recursive central mirror under the engine vocabulary."""
    return mirror_vesica_address(address)


def flower_circle_count(rings: int) -> int:
    """Return 1 + 3n(n+1), the exact number of Flower lattice circles."""
    _validate_nonnegative_integer(rings, "rings")
    return 1 + 3 * rings * (rings + 1)


def flower_port_count(rings: int) -> int:
    """Return the number of adjacent equal-circle Vesicas in a hex disk."""
    _validate_nonnegative_integer(rings, "rings")
    return 9 * rings * rings + 3 * rings


def flower_axial_coordinates(rings: int) -> tuple[AxialCoordinate, ...]:
    """Return a finite equal-circle Flower as a radius-n hexagonal disk."""
    _validate_nonnegative_integer(rings, "rings")
    coordinates = (
        (q, r)
        for q in range(-rings, rings + 1)
        for r in range(-rings, rings + 1)
        if hex_distance((q, r)) <= rings
    )
    return tuple(sorted(coordinates, key=lambda coordinate: (hex_distance(coordinate), coordinate)))


def flower_adjacencies(
    rings: int,
) -> tuple[tuple[AxialCoordinate, AxialCoordinate], ...]:
    """Return every undirected neighboring-circle pair in a finite Flower."""
    nodes = set(flower_axial_coordinates(rings))
    edges: set[tuple[AxialCoordinate, AxialCoordinate]] = set()
    for node in nodes:
        for dq, dr in _HEX_DIRECTIONS:
            neighbor = node[0] + dq, node[1] + dr
            if neighbor in nodes:
                edge = (node, neighbor) if node < neighbor else (neighbor, node)
                edges.add(edge)
    return tuple(sorted(edges))


def flower_circles(
    rings: int,
    radius: float = 1.0,
    origin: Point2D = (0.0, 0.0),
) -> tuple[tuple[AxialCoordinate, CircleVessel], ...]:
    """Return outward Flower growth with equal, unchanged circle radius."""
    radius = float(radius)
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be finite and positive")
    origin = _point2d(origin)
    return tuple(
        (
            coordinate,
            CircleVessel(
                axial_to_cartesian(coordinate, spacing=radius, origin=origin),
                radius,
            ),
        )
        for coordinate in flower_axial_coordinates(rings)
    )


class TreePillar(StrEnum):
    """Three mirror-related channels extracted from the Flower lattice."""

    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


def tree_pillar(coordinate: AxialCoordinate) -> TreePillar:
    """Classify the left, center, and right Flower columns exactly."""
    horizontal_numerator = 2 * coordinate[0] + coordinate[1]
    if horizontal_numerator < 0:
        return TreePillar.NEGATIVE
    if horizontal_numerator > 0:
        return TreePillar.POSITIVE
    return TreePillar.NEUTRAL


@dataclass(frozen=True)
class FlowerTreeGeometry:
    """Inner and outer routing views derived from one Flower adjacency graph."""

    rings: int
    nodes: tuple[AxialCoordinate, ...]
    edges: tuple[tuple[AxialCoordinate, AxialCoordinate], ...]
    outward_routes: tuple[DirectedRoute, ...]
    inward_routes: tuple[DirectedRoute, ...]
    transverse_edges: tuple[tuple[AxialCoordinate, AxialCoordinate], ...]

    def nodes_on(self, pillar: TreePillar) -> tuple[AxialCoordinate, ...]:
        return tuple(node for node in self.nodes if tree_pillar(node) is pillar)


def tree_from_flower(rings: int = 2) -> FlowerTreeGeometry:
    """Derive mirrored inner and outer Tree routes from Flower growth.

    Edges crossing hexagonal radii are directed away from the center for the
    outer Tree and toward it for the inner Tree.  Same-radius edges remain
    transverse weave links.  No unrelated ten-node diagram is imported.
    """
    if rings < 1:
        raise ValueError("Tree extraction requires at least one Flower ring")
    nodes = flower_axial_coordinates(rings)
    edges = flower_adjacencies(rings)
    outward: list[DirectedRoute] = []
    transverse: list[tuple[AxialCoordinate, AxialCoordinate]] = []
    for left, right in edges:
        left_depth = hex_distance(left)
        right_depth = hex_distance(right)
        if left_depth < right_depth:
            outward.append((left, right))
        elif right_depth < left_depth:
            outward.append((right, left))
        else:
            transverse.append((left, right))
    outward_routes = tuple(sorted(outward))
    return FlowerTreeGeometry(
        rings=rings,
        nodes=nodes,
        edges=edges,
        outward_routes=outward_routes,
        inward_routes=tuple((target, source) for source, target in outward_routes),
        transverse_edges=tuple(sorted(transverse)),
    )


class PolarityFlow(StrEnum):
    """Signed phase state on one port."""

    OUTWARD = "outward"
    NEUTRAL = "neutral"
    INWARD = "inward"


class ScaleTransferDirection(StrEnum):
    """Quadrature exchange direction between a parent and child scale."""

    INTO_CHILD = "into_child"
    BALANCED = "balanced"
    INTO_PARENT = "into_parent"


def _signed_state(value: float, positive: StrEnum, negative: StrEnum, neutral: StrEnum) -> StrEnum:
    if abs(value) <= _TOLERANCE:
        return neutral
    return positive if value > 0.0 else negative


@dataclass(frozen=True)
class NegativeSpaceAperture:
    """One explicit Terryen candidate's certified cavity state."""

    key: str
    normalized_sphere_radius: float
    window: NegativeSpaceWindow
    bounded_components: int

    @property
    def open(self) -> bool:
        return self.window.contains(self.normalized_sphere_radius) and self.bounded_components == 1


def negative_space_aperture(key: str, normalized_sphere_radius: float) -> NegativeSpaceAperture:
    """Evaluate an explicitly selected equal-sphere cavity as a port aperture."""
    radius = float(normalized_sphere_radius)
    if not math.isfinite(radius) or radius < 0.0:
        raise ValueError("normalized_sphere_radius must be finite and nonnegative")
    window = terryen_negative_space_window(key)
    topology = cech_topology(key, radius)
    return NegativeSpaceAperture(
        key=key,
        normalized_sphere_radius=radius,
        window=window,
        bounded_components=topology.bounded_negative_space_components,
    )


@dataclass(frozen=True)
class UniversePortState:
    """Geometry, clock state, routing pair, and candidate cavity for one port."""

    address: VesicaUniverseAddress
    geometry: VesicaPortGeometry
    routing_channel: int
    phase_tick: int
    phase: float
    orientation: int
    core_state: int
    paired_core_state: int
    polarity_carrier: float
    transfer_carrier: float
    polarity_flow: PolarityFlow
    scale_transfer: ScaleTransferDirection
    aperture: NegativeSpaceAperture

    @property
    def active(self) -> bool:
        """A port is active only when its selected cavity has one bounded void."""
        return self.geometry.contained and self.aperture.open

    @property
    def funnel_source(self) -> Point2D | None:
        """Return the phase-directed source cusp, or None at neutral polarity."""
        if self.polarity_flow is PolarityFlow.NEUTRAL:
            return None
        return self.geometry.cusp_points[0 if self.polarity_flow is PolarityFlow.OUTWARD else 1]

    @property
    def funnel_sink(self) -> Point2D | None:
        """Return the cusp opposite the current source, or None at neutrality."""
        if self.polarity_flow is PolarityFlow.NEUTRAL:
            return None
        return self.geometry.cusp_points[1 if self.polarity_flow is PolarityFlow.OUTWARD else 0]


def universe_port_state(
    address: VesicaUniverseAddress,
    routing_channel: int,
    phase_tick: int,
    aperture_key: str,
    normalized_sphere_radius: float,
    root_vessel: CircleVessel = DEFAULT_ROOT_VESSEL,
) -> UniversePortState:
    """Build one active-port candidate without hiding its modeling choices."""
    if (
        not isinstance(routing_channel, int)
        or isinstance(routing_channel, bool)
        or routing_channel not in range(3)
    ):
        raise ValueError("routing_channel must be in 0..2")
    if not isinstance(phase_tick, int) or isinstance(phase_tick, bool):
        raise TypeError("phase_tick must be an integer")
    geometry = universe_port_geometry(address, root_vessel)
    parent_depth = address.depth - 1
    orientation = scale_orientation(parent_depth)
    phase = polarity_phase_from_tick(phase_tick)
    polarity_value = alternating_polarity_carrier(phase, parent_depth)
    transfer_value = alternating_transfer_carrier(phase, parent_depth)
    flow = _signed_state(
        polarity_value,
        PolarityFlow.OUTWARD,
        PolarityFlow.INWARD,
        PolarityFlow.NEUTRAL,
    )
    transfer = _signed_state(
        transfer_value,
        ScaleTransferDirection.INTO_CHILD,
        ScaleTransferDirection.INTO_PARENT,
        ScaleTransferDirection.BALANCED,
    )
    state = route(routing_channel, phase_tick)
    return UniversePortState(
        address=address,
        geometry=geometry,
        routing_channel=routing_channel,
        phase_tick=phase_tick,
        phase=phase,
        orientation=orientation,
        core_state=state,
        paired_core_state=polarity(state),
        polarity_carrier=polarity_value,
        transfer_carrier=transfer_value,
        polarity_flow=PolarityFlow(flow),
        scale_transfer=ScaleTransferDirection(transfer),
        aperture=negative_space_aperture(aperture_key, normalized_sphere_radius),
    )
