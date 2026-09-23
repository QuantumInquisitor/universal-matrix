"""Topology-control spherical lift of the derived 43-chamber Sri Yantra.

This module deliberately does not implement Rao's historical great-circle
spherical construction.

Its purpose is narrower and more rigorous: provide a known homeomorphic lift of
the complete Huet planar chamber complex into a unit sphere so the engine has a
control case in which ambient curvature changes but topology cannot.

The construction is:

1. translate the planar chamber complex along its symmetry axis;
2. apply one positive isotropic scale so every selected chamber vertex lies
   strictly inside the open unit disk;
3. apply inverse stereographic projection from that disk to the open northern
   hemisphere of the unit sphere.

Inverse stereographic projection is a homeomorphism.  Every planar chamber edge
is therefore represented by the image of its complete line segment, not by a
newly substituted great-circle chord.  Incidence, edge intersections,
non-intersections, cyclic rings, and mirror pairing are consequently preserved
by construction.

This control is useful precisely because Rao's sourced spherical Sri Yantra is
different: Rao rebuilds the linework from great-circle arcs and spherical
trigonometric constraints.  Any difference found there must be attributed to
that new geometric construction rather than to the mere act of drawing the
same complex on a curved carrier.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite, sqrt

from .sri_yantra_huet_chambers import (
    HUET_CHAMBER_SYSTEM,
    ChamberSystem,
)

Point2D = tuple[float, float]
Point3D = tuple[float, float, float]

_TOLERANCE = 1e-11
_TARGET_DISK_RADIUS = 0.9


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


@dataclass(frozen=True)
class PlanarNormalization:
    """Affine normalization used before inverse stereographic projection."""

    center_x: float
    scale: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "center_x", _finite(self.center_x, "center_x"))
        object.__setattr__(self, "scale", _finite(self.scale, "scale"))
        if self.scale <= 0.0:
            raise ValueError("normalization scale must be positive")

    def forward(self, point: Point2D) -> Point2D:
        return (
            _finite(self.scale * (_finite(point[0], "x") - self.center_x), "normalized x"),
            _finite(self.scale * _finite(point[1], "y"), "normalized y"),
        )

    def inverse(self, point: Point2D) -> Point2D:
        return (
            _finite(_finite(point[0], "u") / self.scale + self.center_x, "recovered x"),
            _finite(_finite(point[1], "v") / self.scale, "recovered y"),
        )


@dataclass(frozen=True)
class SphericalTopologyControl:
    """Homeomorphic spherical realization of one planar chamber system."""

    planar: ChamberSystem
    normalization: PlanarNormalization
    node_points: tuple[Point3D, ...]

    @property
    def selected_candidate_ids(self) -> tuple[int, ...]:
        return self.planar.selected_candidate_ids

    @property
    def chamber_count(self) -> int:
        return self.planar.chamber_count

    @property
    def ring_counts(self) -> tuple[int, int, int, int, int]:
        return self.planar.ring_counts

    @property
    def ring_vertex_counts(self) -> tuple[int, int, int, int, int]:
        return self.planar.ring_vertex_counts

    @property
    def chamber_edge_count(self) -> int:
        return self.planar.chamber_edge_count


def _selected_vertex_ids(system: ChamberSystem) -> tuple[int, ...]:
    return tuple(
        sorted(
            {
                vertex_id
                for candidate_id in system.selected_candidate_ids
                for vertex_id in system.candidates[candidate_id].vertex_ids
            }
        )
    )


def derive_planar_normalization(
    system: ChamberSystem = HUET_CHAMBER_SYSTEM,
) -> PlanarNormalization:
    """Fit all selected chamber vertices inside a radius-0.9 planar disk."""
    vertex_ids = _selected_vertex_ids(system)
    if not vertex_ids:
        raise RuntimeError("the chamber system must contain selected vertices")

    selected_points = tuple(system.nodes[vertex_id] for vertex_id in vertex_ids)
    minimum_x = min(point[0] for point in selected_points)
    maximum_x = max(point[0] for point in selected_points)
    center_x = 0.5 * (minimum_x + maximum_x)

    maximum_radius = max(hypot(point[0] - center_x, point[1]) for point in selected_points)
    if maximum_radius <= _TOLERANCE:
        raise RuntimeError("the selected chamber complex must have positive extent")

    return PlanarNormalization(
        center_x=center_x,
        scale=_TARGET_DISK_RADIUS / maximum_radius,
    )


def inverse_stereographic(point: Point2D) -> Point3D:
    """Map the plane to the unit sphere with the origin at the north pole."""
    u = _finite(point[0], "u")
    v = _finite(point[1], "v")
    squared_radius = _finite(u * u + v * v, "squared chart radius")
    denominator = 1.0 + squared_radius
    return (
        2.0 * u / denominator,
        2.0 * v / denominator,
        (1.0 - squared_radius) / denominator,
    )


def forward_stereographic(point: Point3D) -> Point2D:
    """Invert the selected inverse-stereographic chart away from the south pole."""
    x, y, z = (_finite(component, "sphere coordinate") for component in point)
    if abs(hypot(x, y, z) - 1.0) > _TOLERANCE:
        raise ValueError("point must lie on the unit sphere")
    denominator = 1.0 + z
    if denominator <= _TOLERANCE:
        raise ValueError("the south pole is outside this stereographic chart")
    return x / denominator, y / denominator


def lift_planar_point(
    point: Point2D,
    normalization: PlanarNormalization,
) -> Point3D:
    """Lift one planar coordinate into the topology-control sphere."""
    return inverse_stereographic(normalization.forward(point))


def recover_planar_point(
    point: Point3D,
    normalization: PlanarNormalization,
) -> Point2D:
    """Recover one original planar coordinate from the spherical control."""
    return normalization.inverse(forward_stereographic(point))


def sphere_norm(point: Point3D) -> float:
    return sqrt(sum(component * component for component in point))


def lift_segment_point(
    start: Point2D,
    end: Point2D,
    parameter: float,
    normalization: PlanarNormalization,
) -> Point3D:
    """Lift one point on a complete planar chamber-edge segment."""
    parameter = _finite(parameter, "segment parameter")
    if parameter < 0.0 or parameter > 1.0:
        raise ValueError("segment parameter must lie in [0,1]")
    planar = (
        start[0] + parameter * (end[0] - start[0]),
        start[1] + parameter * (end[1] - start[1]),
    )
    return lift_planar_point(planar, normalization)


def derive_spherical_topology_control(
    system: ChamberSystem = HUET_CHAMBER_SYSTEM,
) -> SphericalTopologyControl:
    """Lift every arrangement node through one injective spherical chart."""
    normalization = derive_planar_normalization(system)
    node_points = tuple(lift_planar_point(point, normalization) for point in system.nodes)
    control = SphericalTopologyControl(
        planar=system,
        normalization=normalization,
        node_points=node_points,
    )

    if not mapped_nodes_are_injective(control):
        raise RuntimeError("the spherical topology-control chart must be injective")
    if not selected_vertices_lie_in_open_northern_hemisphere(control):
        raise RuntimeError("selected chamber vertices must remain in the open northern hemisphere")
    if not planar_roundtrip_closes(control):
        raise RuntimeError("stereographic roundtrip must recover every planar arrangement node")
    if not mirror_equivariant(control):
        raise RuntimeError("spherical control must preserve the planar mirror")
    if control.chamber_count != 43:
        raise RuntimeError("the spherical control must carry all 43 chambers")
    return control


def mapped_nodes_are_injective(
    control: SphericalTopologyControl,
    tolerance: float = _TOLERANCE,
) -> bool:
    """Return whether all arrangement nodes remain distinct on the sphere."""
    for left_index, left in enumerate(control.node_points):
        for right in control.node_points[left_index + 1 :]:
            distance = sqrt(
                sum(
                    (left_component - right_component) ** 2
                    for left_component, right_component in zip(left, right, strict=True)
                )
            )
            if distance <= tolerance:
                return False
    return True


def selected_vertices_lie_in_open_northern_hemisphere(
    control: SphericalTopologyControl,
) -> bool:
    """Return whether every selected chamber vertex has positive spherical z."""
    return all(
        control.node_points[vertex_id][2] > 0.0
        for vertex_id in _selected_vertex_ids(control.planar)
    )


def planar_roundtrip_closes(
    control: SphericalTopologyControl,
    tolerance: float = _TOLERANCE,
) -> bool:
    """Return whether every spherical node maps back to its original planar node."""
    for planar, spherical in zip(
        control.planar.nodes,
        control.node_points,
        strict=True,
    ):
        recovered = recover_planar_point(
            spherical,
            control.normalization,
        )
        if (
            hypot(
                recovered[0] - planar[0],
                recovered[1] - planar[1],
            )
            > tolerance
        ):
            return False
    return True


def mirror_spherical_point(point: Point3D) -> Point3D:
    """Reflect the spherical control across the inherited planar symmetry plane."""
    return point[0], -point[1], point[2]


def _planar_mirror_node_ids(
    system: ChamberSystem,
) -> tuple[int, ...]:
    result = []
    for point in system.nodes:
        target = (point[0], -point[1])
        matches = [
            index
            for index, candidate in enumerate(system.nodes)
            if hypot(candidate[0] - target[0], candidate[1] - target[1]) <= 1e-9
        ]
        if len(matches) != 1:
            raise RuntimeError("each planar arrangement node must have one mirror partner")
        result.append(matches[0])
    return tuple(result)


def mirror_equivariant(
    control: SphericalTopologyControl,
    tolerance: float = _TOLERANCE,
) -> bool:
    """Return whether planar reflection commutes with the spherical lift."""
    mirror_ids = _planar_mirror_node_ids(control.planar)
    for node_id, mirrored_id in enumerate(mirror_ids):
        reflected = mirror_spherical_point(control.node_points[node_id])
        target = control.node_points[mirrored_id]
        distance = sqrt(
            sum((left - right) ** 2 for left, right in zip(reflected, target, strict=True))
        )
        if distance > tolerance:
            return False
    return True


def chamber_incidence_signature(
    control: SphericalTopologyControl,
) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    """Return the selected chamber-to-vertex incidence carried through the lift."""
    return tuple(
        (
            candidate_id,
            control.planar.candidates[candidate_id].vertex_ids,
        )
        for candidate_id in control.selected_candidate_ids
    )


def ring_cycle_signature(
    control: SphericalTopologyControl,
) -> tuple[tuple[str, int, tuple[int, ...]], ...]:
    """Return ring identity, size, and member IDs under the control lift."""
    return tuple(
        (
            ring.name,
            len(ring.candidate_ids),
            ring.candidate_ids,
        )
        for ring in control.planar.rings
    )


def topology_change_detected(
    control: SphericalTopologyControl,
) -> bool:
    """Detect topology loss under the known homeomorphic control mapping."""
    if not mapped_nodes_are_injective(control):
        return True
    if not planar_roundtrip_closes(control):
        return True
    if not mirror_equivariant(control):
        return True
    if control.chamber_count != 43:
        return True
    if control.ring_counts != (1, 8, 10, 10, 14):
        return True
    if control.ring_vertex_counts != (3, 16, 20, 20, 28):
        return True
    if control.chamber_edge_count != 129:
        return True
    return False


SPHERICAL_TOPOLOGY_CONTROL = derive_spherical_topology_control()
