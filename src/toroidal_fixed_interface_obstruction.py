"""Find collisions that any fixed-bend-interface deformation must retain.

This is an additive diagnostic, not a new routing or current field. It checks
both end faces of same-face incident bends against their neighboring finite
straight shells. A strictly penetrating face point remains an intersection
under any continuous deformation fixing that face and the neighboring shell.

The analytic witness search covers centered, perpendicular configurations at
the bend's mid-annulus radius. Failure to find a witness is not clearance.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Hashable
from dataclasses import dataclass

from .toroidal_annular_junction import AnnularPortFace
from .toroidal_incident_bend_audit import AnnularStraightSegment, _endpoint_bend_and_straight
from .toroidal_separated_channels import (
    SeparatedFramedEdgeNetwork,
    build_separated_framed_edge_network,
)
from .toroidal_smooth_bends import AnnularQuarterBend, build_smooth_global_toroidal_routing
from .vesica_tree_circulation import PORT_NODES, vesica_circulation

_TOLERANCE = 1e-10


def _dot(left, right) -> float:
    return math.fsum(a * b for a, b in zip(left, right, strict=True))


@dataclass(frozen=True)
class FixedInterfaceWitness:
    phi: float
    q: float
    theta: float
    point: tuple[float, float, float]
    straight_penetration: float


def find_mid_annulus_interface_witness(
    bend: AnnularQuarterBend,
    straight: AnnularStraightSegment,
    *,
    phi: float,
) -> FixedInterfaceWitness | None:
    """Construct and verify a point strictly inside the neighboring shell.

    The straight axis must be parallel to the face's normal basis vector
    (hence lie in the face plane), with no binormal offset from its center.
    Its radial distance on the circle is sqrt(d**2 + r**2*sin(theta)**2).
    The final exact finite-shell membership check guards the floating-point
    alignment tolerance and excludes witnesses beyond either straight end.
    None means only that this restricted construction found no witness.
    """
    if phi not in (0.0, math.pi / 2):
        raise ValueError("phi must select a bend end face: 0 or pi/2")
    normal, tangent = bend.normal(phi), bend.tangent(phi)
    center = bend.centerline_point(phi)
    delta = tuple(a - b for a, b in zip(center, straight.start, strict=True))
    if abs(abs(_dot(straight.direction, normal)) - 1.0) > _TOLERANCE:
        return None
    if abs(_dot(delta, bend._binormal)) > _TOLERANCE:
        return None

    radius = (bend.inner_radius + bend.outer_radius) / 2
    distance = abs(_dot(delta, tangent))
    lower = max(straight.inner_radius, distance)
    upper = min(straight.outer_radius, math.hypot(distance, radius))
    if upper - lower <= _TOLERANCE:
        return None
    target_radius = (lower + upper) / 2
    sine = min(1.0, math.sqrt(max(0.0, target_radius**2 - distance**2)) / radius)
    cosine = math.sqrt(max(0.0, 1.0 - sine**2))
    # Both axial branches and binormal signs matter for a finite segment.
    for axial_sign in (1.0, -1.0):
        for binormal_sign in (1.0, -1.0):
            theta = math.atan2(binormal_sign * sine, axial_sign * cosine)
            point = bend.map_point(phi, 0.5, theta)
            penetration = straight.penetration_margin(point)
            if penetration > _TOLERANCE:
                return FixedInterfaceWitness(phi, 0.5, theta, point, penetration)
    return None


@dataclass(frozen=True)
class IncidentFixedInterfaceObstruction[NodeT: Hashable]:
    node: NodeT
    face: AnnularPortFace
    bending_edge_index: int
    straight_edge_index: int
    witness: FixedInterfaceWitness


@dataclass(frozen=True)
class FixedInterfaceAudit[NodeT: Hashable]:
    examined_interface_count: int
    obstructions: tuple[IncidentFixedInterfaceObstruction[NodeT], ...]

    @property
    def obstruction_count(self) -> int:
        return len(self.obstructions)


def audit_fixed_bend_interfaces[NodeT: Hashable](
    network: SeparatedFramedEdgeNetwork[NodeT],
    *,
    bend_margin: float = 0.25,
    node_gap: float = 1.0,
    edge_gap: float = 0.5,
) -> FixedInterfaceAudit[NodeT]:
    """Inspect both interfaces of each same-face incident bend/straight pair.

    This starts from the routing, independently of previous sampled collisions.
    It neither modifies the network nor certifies all other collision pairs.
    """
    routing = build_smooth_global_toroidal_routing(
        network.framed_network, bend_margin=bend_margin, node_gap=node_gap, edge_gap=edge_gap,
    )
    edges = {edge.edge_index: edge for edge in routing.edges}
    obstructions, examined = [], 0
    for junction in network.junction_network.junctions:
        groups = defaultdict(list)
        for port in junction.ports:
            assembly = network.framed_network.assemblies[port.edge_index]
            if abs(assembly.edge.current) > _TOLERANCE:
                groups[port.face].append(port.edge_index)
        for face, indices in groups.items():
            for bending_index in sorted(indices):
                bend, _ = _endpoint_bend_and_straight(edges[bending_index], junction.node)
                for straight_index in sorted(indices):
                    if straight_index == bending_index:
                        continue
                    _, straight = _endpoint_bend_and_straight(edges[straight_index], junction.node)
                    for phi in (0.0, math.pi / 2):
                        examined += 1
                        witness = find_mid_annulus_interface_witness(bend, straight, phi=phi)
                        if witness is not None:
                            obstructions.append(IncidentFixedInterfaceObstruction(
                                junction.node, face, bending_index, straight_index, witness,
                            ))
    return FixedInterfaceAudit(examined, tuple(obstructions))


def main() -> None:
    circulation = vesica_circulation(1.0, return_split=0.4)
    network = build_separated_framed_edge_network(circulation.edges, PORT_NODES, shell_gap=3.0)
    audit = audit_fixed_bend_interfaces(network, bend_margin=0.05)
    print("TOROIDAL FIXED BEND-INTERFACE OBSTRUCTION")
    print("shell_gap=3; bend_margin=0.05; witness_search=analytic_mid_annulus")
    print("scope=same_face_incident_bend_interfaces_vs_finite_straights; no_global_clearance_claim")
    print(f"examined_interface_count={audit.examined_interface_count}")
    print(f"obstruction_count={audit.obstruction_count}")
    for item in audit.obstructions:
        witness = item.witness
        print(
            f"node={item.node}; face={item.face}; bend={item.bending_edge_index}; "
            f"straight={item.straight_edge_index}; phi={witness.phi:.12g}; "
            f"q={witness.q:g}; theta={witness.theta:.12g}; "
            f"straight_penetration={witness.straight_penetration:.12g}; point={witness.point}"
        )
    print("constraint=move_bend_interfaces_or_neighboring_shells_to_remove_these_witnesses")
    print("junction_ports_need_not_move; no_witness_does_not_imply_clearance")


if __name__ == "__main__":
    main()
