import math
from typing import get_type_hints

import pytest

from src.sevenfold_seed_contract import VesicaUniverseAddress
from src.universe_port_engine import (
    PolarityFlow,
    ScaleTransferDirection,
    TreePillar,
    flower_circle_count,
    mirror_universe_address,
    universe_port_state,
)
from src.vesica_tree_circulation import (
    PORT_NODES,
    CanonicalPortCirculation,
    DirectedCurrent,
    FlowChannel,
    PortNode,
    RecursiveScaleCurrent,
    canonical_port_circulation,
    continuity_residual,
    continuity_step,
    graph_divergence,
    maximum_residual,
    outward_tree_weights,
    ring_cycle_routes,
    total_content,
    tree_circulation,
    vesica_circulation,
)


def active_state(address: VesicaUniverseAddress, tick: int = 0):
    return universe_port_state(address, 1, tick, "mira", 0.9)


@pytest.mark.parametrize(("current", "split"), ((1.0, 0.5), (-2.5, 0.5), (0.7, 0.2)))
def test_vesica_axis_and_two_returns_are_locally_conservative(
    current: float,
    split: float,
) -> None:
    circulation = vesica_circulation(current, split)

    assert len(circulation.edges) == 4
    assert circulation.edges[0].source is PortNode.CUSP_A
    assert circulation.edges[0].target is PortNode.NEUTRAL
    assert circulation.edges[1].source is PortNode.NEUTRAL
    assert circulation.edges[1].target is PortNode.CUSP_B
    assert sum(edge.current for edge in circulation.edges[2:]) == pytest.approx(current)
    assert circulation.balance_residual < 1e-12


def test_unbalanced_graph_current_moves_content_but_preserves_its_total() -> None:
    currents = (
        DirectedCurrent(
            PortNode.CUSP_A,
            PortNode.NEUTRAL,
            0.75,
            FlowChannel.VESICA_AXIS_IN,
        ),
    )
    before = {
        PortNode.CUSP_A: 2.0,
        PortNode.NEUTRAL: 1.0,
        PortNode.CUSP_B: 3.0,
    }
    after = continuity_step(PORT_NODES, before, currents, dt=0.2)
    residual = continuity_residual(PORT_NODES, before, after, currents, dt=0.2)

    assert after[PortNode.CUSP_A] == pytest.approx(1.85)
    assert after[PortNode.NEUTRAL] == pytest.approx(1.15)
    assert after[PortNode.CUSP_B] == before[PortNode.CUSP_B]
    assert total_content(after) == pytest.approx(total_content(before), abs=1e-12)
    assert maximum_residual(residual) < 1e-12


def test_closed_vesica_circulation_is_stationary_under_continuity() -> None:
    circulation = vesica_circulation(1.3, return_split=0.37)
    before = dict.fromkeys(PORT_NODES, 2.0)
    after = continuity_step(PORT_NODES, before, circulation.edges, dt=0.1)

    assert after == pytest.approx(before)


def test_clock_quadrature_exchanges_local_circulation_with_scale_transfer() -> None:
    address = VesicaUniverseAddress((0,))
    flows = {
        tick: canonical_port_circulation(active_state(address, tick), amplitude=3.0)
        for tick in (0, 9, 18, 27, 36)
    }

    assert flows[0].local.through_current == pytest.approx(3.0)
    assert flows[0].scale.current == 0.0
    assert flows[9].local.through_current == 0.0
    assert flows[9].scale.current == pytest.approx(3.0)
    assert flows[18].local.through_current == pytest.approx(-3.0)
    assert flows[18].scale.current == 0.0
    assert flows[27].local.through_current == 0.0
    assert flows[27].scale.current == pytest.approx(-3.0)
    assert flows[36].local.through_current == pytest.approx(3.0)
    assert all(flow.quadrature_content == pytest.approx(9.0) for flow in flows.values())
    assert all(abs(flow.quadrature_residual) < 1e-12 for flow in flows.values())


def test_clock_labels_agree_with_current_direction() -> None:
    address = VesicaUniverseAddress((4,))
    outward = canonical_port_circulation(active_state(address, 0))
    neutral_child = canonical_port_circulation(active_state(address, 9))
    inward = canonical_port_circulation(active_state(address, 18))
    neutral_parent = canonical_port_circulation(active_state(address, 27))

    assert outward.state.polarity_flow is PolarityFlow.OUTWARD
    assert outward.local.through_current > 0.0
    assert neutral_child.state.scale_transfer is ScaleTransferDirection.INTO_CHILD
    assert neutral_child.scale.source == VesicaUniverseAddress()
    assert neutral_child.scale.target == address
    assert inward.state.polarity_flow is PolarityFlow.INWARD
    assert inward.local.through_current < 0.0
    assert neutral_parent.state.scale_transfer is ScaleTransferDirection.INTO_PARENT
    assert neutral_parent.scale.source == address
    assert neutral_parent.scale.target == VesicaUniverseAddress()


def test_adjacent_recursive_depth_reverses_both_quadrature_currents() -> None:
    parent = canonical_port_circulation(active_state(VesicaUniverseAddress((0,)), 4))
    child = canonical_port_circulation(active_state(VesicaUniverseAddress((0, 0)), 4))

    assert child.local.through_current == pytest.approx(-parent.local.through_current)
    assert child.scale.current == pytest.approx(-parent.scale.current)


@pytest.mark.parametrize("depth", range(1, 5))
def test_every_clock_tick_preserves_local_balance_and_quadrature(depth: int) -> None:
    address = VesicaUniverseAddress((0,) * depth)

    for tick in range(36):
        flow = canonical_port_circulation(active_state(address, tick), amplitude=2.75)
        assert flow.local.balance_residual < 1e-12
        assert abs(flow.quadrature_residual) < 1e-12


def test_quarter_turn_carrier_cleanup_precedes_large_amplitude_scaling() -> None:
    address = VesicaUniverseAddress((0,))
    flow = canonical_port_circulation(active_state(address, 9), amplitude=1e20)

    assert flow.local.through_current == 0.0
    assert flow.scale.current == pytest.approx(1e20)


def test_recursive_scale_current_is_a_distinct_parent_child_address_edge() -> None:
    parent = VesicaUniverseAddress((2, 7))
    child = parent.child(11)
    down = RecursiveScaleCurrent(parent, child, 0.4)
    up = RecursiveScaleCurrent(parent, child, -0.4)
    balanced = RecursiveScaleCurrent(parent, child, 0.0)

    assert (down.source, down.target) == (parent, child)
    assert (up.source, up.target) == (child, parent)
    assert balanced.source is balanced.target is None


def test_mirrored_addresses_preserve_the_scalar_circulation_law() -> None:
    address = VesicaUniverseAddress((0, 7, 5))
    mirrored = mirror_universe_address(address)
    original = canonical_port_circulation(active_state(address, 5), amplitude=2.0)
    reflection = canonical_port_circulation(active_state(mirrored, 5), amplitude=2.0)

    assert reflection.local.through_current == pytest.approx(original.local.through_current)
    assert reflection.scale.current == pytest.approx(original.scale.current)
    assert reflection.local.divergence == pytest.approx(original.local.divergence)


@pytest.mark.parametrize("rings", range(1, 6))
def test_normalized_outer_tree_preserves_unit_flux_across_every_ring(rings: int) -> None:
    circulation = tree_circulation(rings, radial_current=2.5)

    assert len(circulation.geometry.nodes) == flower_circle_count(rings)
    assert all(circulation.radial_cut_flux(depth) == pytest.approx(2.5) for depth in range(rings))


def test_inner_tree_is_the_exact_weighted_reverse_of_outer_tree() -> None:
    circulation = tree_circulation(3, radial_current=1.7)

    outward = {(edge.source, edge.target): edge.current for edge in circulation.outward_edges}
    inward = {(edge.target, edge.source): edge.current for edge in circulation.inward_edges}
    assert inward == pytest.approx(outward)


@pytest.mark.parametrize(("rings", "handedness"), ((1, 1), (2, -1), (4, 1)))
def test_each_transverse_ring_is_one_closed_cycle(rings: int, handedness: int) -> None:
    circulation = tree_circulation(
        rings,
        radial_current=0.0,
        weave_current=0.8,
        weave_handedness=handedness,
    )

    for ring in range(1, rings + 1):
        routes = ring_cycle_routes(circulation.geometry, ring, handedness)
        assert len(routes) == 6 * ring
        assert {source for source, _ in routes} == {target for _, target in routes}
    assert circulation.balance_residual < 1e-12


def test_radial_pair_and_ring_weave_form_a_closed_tree_circulation() -> None:
    circulation = tree_circulation(
        4,
        radial_current=1.25,
        weave_current=-0.3,
        weave_handedness=-1,
    )

    assert circulation.balance_residual < 1e-12
    before = {node: 1.0 + index / 10.0 for index, node in enumerate(circulation.geometry.nodes)}
    after = continuity_step(circulation.geometry.nodes, before, circulation.edges, dt=0.25)
    assert after == pytest.approx(before)


def test_tree_boundary_flux_is_mirror_balanced_across_three_pillars() -> None:
    circulation = tree_circulation(4, radial_current=1.0)
    flux = circulation.boundary_flux_by_pillar()

    assert flux[TreePillar.POSITIVE] == pytest.approx(flux[TreePillar.NEGATIVE])
    assert math.fsum(flux.values()) == pytest.approx(1.0)
    assert all(value > 0.0 for value in flux.values())


def test_central_mirror_preserves_normalized_tree_route_weights() -> None:
    circulation = tree_circulation(3)
    weights = dict(outward_tree_weights(circulation.geometry))

    for (source, target), weight in weights.items():
        mirrored_route = (-source[0], -source[1]), (-target[0], -target[1])
        assert weights[mirrored_route] == pytest.approx(weight)


def test_graph_divergence_sums_to_zero_for_any_internal_currents() -> None:
    circulation = tree_circulation(2, radial_current=0.0)
    nodes = circulation.geometry.nodes
    arbitrary = tuple(
        DirectedCurrent(source, target, index / 13.0, FlowChannel.TREE_OUTER)
        for index, (source, target) in enumerate(circulation.geometry.outward_routes, start=1)
    )
    divergence = graph_divergence(nodes, arbitrary)

    assert math.fsum(divergence.values()) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize(
    ("callable_object", "args", "error"),
    (
        (vesica_circulation, (1.0, -0.1), ValueError),
        (vesica_circulation, (1.0, 1.1), ValueError),
        (tree_circulation, (0,), ValueError),
        (tree_circulation, (2, 1.0, 0.0, 0), ValueError),
        (
            continuity_step,
            (PORT_NODES, {node: 0.0 for node in PORT_NODES}, (), 0.0),
            ValueError,
        ),
        (
            RecursiveScaleCurrent,
            (VesicaUniverseAddress(), VesicaUniverseAddress((0, 1)), 1.0),
            ValueError,
        ),
        (maximum_residual, ({"node": math.nan},), ValueError),
    ),
)
def test_invalid_circulation_inputs_fail_closed(
    callable_object: object,
    args: tuple[object, ...],
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        callable_object(*args)  # type: ignore[operator]


def test_canonical_circulation_rejects_closed_aperture_and_negative_amplitude() -> None:
    closed = universe_port_state(VesicaUniverseAddress((0,)), 0, 0, "mira", 1.0)

    with pytest.raises(ValueError, match="active port"):
        canonical_port_circulation(closed)
    with pytest.raises(ValueError, match="nonnegative"):
        canonical_port_circulation(active_state(VesicaUniverseAddress((0,))), amplitude=-1.0)


def test_public_dataclass_annotation_stays_specific() -> None:
    assert get_type_hints(CanonicalPortCirculation)["scale"] is RecursiveScaleCurrent
