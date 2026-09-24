"""A bounded different-destination control for the shared-return construction.

Four balanced edges on three nodes admit a common outgoing route prefix, but
the inner branch intersects the outer straight where their destinations split.
An explicit point proves this candidate fails; it says nothing about all
possible fan-out geometries and supplies no connected field on the overlap.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .toroidal_separated_channels import build_separated_framed_edge_network
from .toroidal_shared_return_route import routed_tube_pieces
from .toroidal_smooth_bends import (
    SmoothedRoutedEdge,
    SmoothGlobalToroidalRouting,
    _build_edge_bends,
    build_smooth_global_toroidal_routing,
)
from .vesica_tree_circulation import DirectedCurrent, FlowChannel

FANOUT_NODES = ("A", "B", "C")


@dataclass(frozen=True)
class FanoutSplitWitness:
    point: tuple[float, float, float]
    phi: float
    inner_penetration: float
    outer_penetration: float


@dataclass(frozen=True)
class SharedPrefixFanoutExperiment:
    original: SmoothGlobalToroidalRouting
    candidate: SmoothGlobalToroidalRouting
    witness: FanoutSplitWitness


def build_shared_prefix_fanout_experiment(current: float = 1.0) -> SharedPrefixFanoutExperiment:
    """Build only the fixed gap-3, margin-0.05 balanced three-node example.

    Both branches leave A; their destinations are B and C. Preserve every
    endpoint frame while placing inner edge 2 on outer edge 3's prefix.
    No existing builder or full-route sharing precondition is relaxed.
    """
    current = float(current)
    if not math.isfinite(current) or abs(current) <= 1e-10:
        raise ValueError("experiment current must be finite and nonzero")
    currents = tuple(
        DirectedCurrent(source, target, current * fraction, FlowChannel.TREE_OUTER)
        for source, target, fraction in (("B", "A", 0.4), ("C", "A", 0.6),
                                          ("A", "B", 0.4), ("A", "C", 0.6))
    )
    network = build_separated_framed_edge_network(currents, FANOUT_NODES, shell_gap=3.0)
    original = build_smooth_global_toroidal_routing(network.framed_network, bend_margin=0.05)
    inner, outer = original.edges[2:]
    target, common = inner.route.target_frame.origin, outer.route.route
    points = (*common[:4], (target[0], common[4][1], common[4][2]),
              (target[0], common[5][1], common[5][2]), target)
    radius = outer.bends[0].bend_radius
    route = replace(inner.route, route=points, lane_y=outer.route.lane_y,
                    lane_height=outer.route.lane_height,
                    clearance_radius=max(inner.route.clearance_radius,
                                         inner.route.assembly.channel.outer_radius + radius))
    moved = SmoothedRoutedEdge(route, _build_edge_bends(route, radius))
    edges = (*original.edges[:2], moved, outer)
    candidate = SmoothGlobalToroidalRouting(
        replace(original.global_routing, edges=tuple(edge.route for edge in edges)),
        edges, original.bend_margin,
    )

    # At the split, bend piece 7 turns away from outer straight piece 6.
    # theta=0 gives straight-axis distance R - (R-r_inner)*cos(phi).
    # Set that distance to the outer annulus midpoint and verify membership
    # in both actual finite volumes, including their axial ends.
    left = routed_tube_pieces(moved)[7]
    right = routed_tube_pieces(outer)[6]
    inner_mid = (left.volume.inner_radius + left.volume.outer_radius) / 2
    outer_mid = (right.volume.inner_radius + right.volume.outer_radius) / 2
    phi = math.acos((radius - outer_mid) / (radius - inner_mid))
    point = left.volume.map_point(phi, 0.5, 0.0)
    witness = FanoutSplitWitness(point, phi, left.penetration(point), right.penetration(point))
    if min(witness.inner_penetration, witness.outer_penetration) <= 1e-10:
        raise RuntimeError("fixed fan-out candidate lost its verified interior witness")
    return SharedPrefixFanoutExperiment(original, candidate, witness)


def main() -> None:
    print("TOROIDAL SHARED-PREFIX FAN-OUT CONTROL")
    for current in (1.0, -1.0):
        experiment = build_shared_prefix_fanout_experiment(current)
        routing, witness = experiment.candidate, experiment.witness
        inner, outer = routing.edges[2:]
        print(f"current={current:g}; common_source_frame={inner.route.source_frame == outer.route.source_frame}; "
              f"common_target_frame={inner.route.target_frame == outer.route.target_frame}")
        print(f"interface_residual={routing.maximum_interface_residual():.12g}; "
              f"minimum_jacobian={routing.minimum_jacobian_margin():.12g}")
        print(f"split_pieces=inner_2_piece_7_vs_outer_3_piece_6; phi={witness.phi:.12g}; q=0.5; theta=0; "
              f"point={witness.point}; inner_penetration={witness.inner_penetration:.12g}; "
              f"outer_penetration={witness.outer_penetration:.12g}")
    print("result=this_shared_prefix_candidate_intersects_at_its_destination_split")
    print("not_a_general_fanout_impossibility_or_a_connected_global_current_field")


if __name__ == "__main__":
    main()
