import math

import pytest

from src.toroidal_shared_prefix_fanout import FANOUT_NODES, build_shared_prefix_fanout_experiment
from src.toroidal_shared_return_route import move_inner_return_to_shared_route, routed_tube_pieces
from src.vesica_tree_circulation import graph_divergence


@pytest.fixture(scope="module", params=(1.0, -1.0))
def experiment(request):
    return build_shared_prefix_fanout_experiment(request.param)


def test_balanced_fanout_has_common_source_but_distinct_destinations(experiment):
    routing = experiment.original
    currents = tuple(edge.route.edge for edge in routing.edges)
    assert graph_divergence(FANOUT_NODES, currents) == dict.fromkeys(FANOUT_NODES, 0.0)
    inner, outer = routing.edges[2:]
    assert inner.route.source_frame == outer.route.source_frame
    assert inner.route.target_frame.node == "B"
    assert outer.route.target_frame.node == "C"
    assert math.dist(inner.route.target_frame.origin, outer.route.target_frame.origin) > 54
    with pytest.raises(ValueError, match="identical port frames"):
        move_inner_return_to_shared_route(routing, 1.0)


def test_shared_prefix_preserves_ports_currents_and_local_regularity(experiment):
    before, after = experiment.original, experiment.candidate
    for left, right in zip(before.edges, after.edges, strict=True):
        assert left.route.assembly == right.route.assembly
        assert left.route.source_frame == right.route.source_frame
        assert left.route.target_frame == right.route.target_frame
    for index in (0, 1, 3):
        assert before.edges[index] is after.edges[index]
    assert after.edges[2].route.route[:4] == after.edges[3].route.route[:4]
    assert after.edges[2].route.route[-1] != after.edges[3].route.route[-1]
    assert after.global_routing.maximum_endpoint_frame_residual() == 0
    assert after.maximum_interface_residual() < 1e-12
    assert after.minimum_jacobian_margin() > 0


def test_analytic_split_point_is_strictly_inside_both_finite_volumes(experiment):
    candidate, witness = experiment.candidate, experiment.witness
    bend = routed_tube_pieces(candidate.edges[2])[7]
    straight = routed_tube_pieces(candidate.edges[3])[6]
    assert witness.inner_penetration == pytest.approx(0.2)
    assert witness.outer_penetration == pytest.approx(0.2)
    assert bend.volume.inverse_parameters(witness.point) == pytest.approx((witness.phi, 0.5, 0.0), abs=1e-12)
    # Independent Cartesian check: this outer straight runs in x, with y/z
    # fixed. Its finite axial interval and radial bounds both contain p.
    x, y, z = witness.point
    start, end = straight.volume.start, straight.volume.end
    assert min(start[0], end[0]) < x < max(start[0], end[0])
    assert start[1:] == end[1:]
    radius = math.hypot(y - start[1], z - start[2])
    assert radius == pytest.approx(12.4)
    assert straight.volume.inner_radius < radius < straight.volume.outer_radius
    # A small three-dimensional neighborhood also overlaps, not just a face.
    for axis in range(3):
        for delta in (-1e-4, 1e-4):
            point = tuple(value + (delta if i == axis else 0) for i, value in enumerate(witness.point))
            assert min(bend.penetration(point), straight.penetration(point)) > 0.19


@pytest.mark.parametrize("current", (0.0, float("nan"), float("inf")))
def test_invalid_experiment_current_is_rejected(current):
    with pytest.raises(ValueError, match="finite and nonzero"):
        build_shared_prefix_fanout_experiment(current)
