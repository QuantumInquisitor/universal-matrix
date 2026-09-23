import math
from typing import get_type_hints

import pytest

from src.sevenfold_seed_contract import VesicaUniverseAddress
from src.transitive_plane_branching import (
    ASTRAL_PLANE,
    DREAM_PLANE,
    ETHERIC_PLANE,
    MATERIAL_PLANE,
    MENTAL_PLANE,
    PROBABILITY_PLANE,
    PSYCHIC_PLANE,
    AddressRelation,
    PlaneAddress,
    PlaneId,
    PlaneLink,
    PlaneLinkKind,
    PlaneTopology,
    PlaneTransition,
    PossibilityAddress,
    PossibilityBranch,
    chapter_eight_overlap_topology,
    classify_address_relation,
    mirror_plane_address,
    mirror_possibility_address,
    mirror_possibility_branch,
    route_plane_current,
    symmetric_possibility_branch,
)
from src.vesica_tree_circulation import (
    FlowChannel,
    continuity_residual,
    continuity_step,
    graph_divergence,
    maximum_residual,
    total_content,
)

_TEST_UNIVERSE = VesicaUniverseAddress((0, 7))
_ROOT_POSSIBILITY = PossibilityAddress()


def state(
    plane: PlaneId = MATERIAL_PLANE,
    universe: VesicaUniverseAddress = _TEST_UNIVERSE,
    possibility: PossibilityAddress = _ROOT_POSSIBILITY,
) -> PlaneAddress:
    return PlaneAddress(universe, plane, possibility)


def test_product_address_keeps_scale_plane_and_branch_depth_independent() -> None:
    origin = state()
    on_dream = origin.on_plane(DREAM_PLANE)
    branch = origin.branch(-2)
    deeper_scale = PlaneAddress(origin.universe.child(3), origin.plane, origin.possibility)

    assert classify_address_relation(origin, origin) is AddressRelation.SAME_STATE
    assert classify_address_relation(origin, on_dream) is AddressRelation.PLANE_TRANSITION
    assert classify_address_relation(origin, branch) is AddressRelation.POSSIBILITY_BRANCH
    assert classify_address_relation(origin, deeper_scale) is AddressRelation.RECURSIVE_SCALE
    assert on_dream.scale_depth == branch.scale_depth == origin.scale_depth
    assert on_dream.branch_depth == origin.branch_depth
    assert branch.branch_depth == origin.branch_depth + 1


def test_mixed_coordinate_and_nonadjacent_moves_fail_closed() -> None:
    origin = state()
    mixed = PlaneAddress(origin.universe.child(1), DREAM_PLANE, origin.possibility)
    skipped_branch = PlaneAddress(
        origin.universe,
        origin.plane,
        PossibilityAddress((1, -1)),
    )

    with pytest.raises(ValueError, match="exactly one"):
        classify_address_relation(origin, mixed)
    with pytest.raises(ValueError, match="adjacent branch"):
        classify_address_relation(origin, skipped_branch)


def test_signed_possibility_mirror_is_an_involution_and_preserves_zero() -> None:
    address = PossibilityAddress((-3, 0, 2, -1))
    mirrored = mirror_possibility_address(address)

    assert mirrored.path == (3, 0, -2, 1)
    assert mirror_possibility_address(mirrored) == address


def test_plane_mirror_combines_universe_and_possibility_without_renaming_plane() -> None:
    address = state(
        plane=MENTAL_PLANE,
        universe=VesicaUniverseAddress((0, 7, 5)),
        possibility=PossibilityAddress((2, 0, -4)),
    )
    mirrored = mirror_plane_address(address)

    assert mirrored.plane == address.plane
    assert mirrored.scale_depth == address.scale_depth
    assert mirrored.possibility.path == (-2, 0, 4)
    assert mirror_plane_address(mirrored) == address


def test_chapter_eight_topology_routes_through_declared_intermediaries() -> None:
    topology = chapter_eight_overlap_topology()
    route = topology.shortest_route(MATERIAL_PLANE, PROBABILITY_PLANE)

    assert route[0] == MATERIAL_PLANE
    assert route[-1] == PROBABILITY_PLANE
    assert len(route) == 3
    assert route[1] in (ASTRAL_PLANE, ETHERIC_PLANE)
    assert topology.link_between(route[0], route[1]) is not None
    assert topology.link_between(route[1], route[2]) is not None


def test_named_but_unconnected_plane_does_not_gain_an_invented_route() -> None:
    topology = chapter_eight_overlap_topology()

    assert topology.neighbors(PSYCHIC_PLANE) == ()
    with pytest.raises(ValueError, match="no declared overlap route"):
        topology.shortest_route(MATERIAL_PLANE, PSYCHIC_PLANE)


def test_routed_plane_current_keeps_universe_and_possibility_fixed() -> None:
    topology = chapter_eight_overlap_topology()
    source = state(possibility=PossibilityAddress((-1, 0, 2)))
    transitions = route_plane_current(topology, source, PROBABILITY_PLANE, 0.8)

    assert len(transitions) == 2
    assert transitions[0].source == source
    assert transitions[-1].target.plane == PROBABILITY_PLANE
    assert all(step.source.universe == source.universe for step in transitions)
    assert all(step.target.universe == source.universe for step in transitions)
    assert all(step.source.possibility == source.possibility for step in transitions)
    assert all(step.target.possibility == source.possibility for step in transitions)
    assert all(step.edge.channel is FlowChannel.PLANE_TRANSITION for step in transitions)


def test_transitive_route_has_only_endpoint_divergence_and_conserves_content() -> None:
    topology = chapter_eight_overlap_topology()
    source = state()
    transitions = route_plane_current(topology, source, PROBABILITY_PLANE, 0.75)
    nodes = tuple([transitions[0].source] + [step.target for step in transitions])
    edges = tuple(step.edge for step in transitions)
    divergence = graph_divergence(nodes, edges)
    before = dict.fromkeys(nodes, 2.0)
    after = continuity_step(nodes, before, edges, 0.2)
    residual = continuity_residual(nodes, before, after, edges, 0.2)

    assert divergence[nodes[0]] == pytest.approx(0.75)
    assert divergence[nodes[-1]] == pytest.approx(-0.75)
    assert all(divergence[node] == pytest.approx(0.0) for node in nodes[1:-1])
    assert total_content(after) == pytest.approx(total_content(before), abs=1e-12)
    assert maximum_residual(residual) < 1e-12


def test_direct_transition_rejects_missing_overlap_and_scale_or_branch_changes() -> None:
    topology = chapter_eight_overlap_topology()
    source = state()

    with pytest.raises(ValueError, match="direct overlap"):
        topology.transition(source, source.on_plane(MENTAL_PLANE), 1.0)
    with pytest.raises(ValueError, match="only the plane"):
        topology.transition(
            source,
            PlaneAddress(source.universe.child(1), ASTRAL_PLANE, source.possibility),
            1.0,
        )
    with pytest.raises(ValueError, match="only the plane"):
        topology.transition(source, source.branch(1), 1.0)


@pytest.mark.parametrize("pair_count", (1, 2, 3, 5))
def test_symmetric_branch_supports_open_mirror_paired_outcome_counts(pair_count: int) -> None:
    branch = symmetric_possibility_branch(
        state(PROBABILITY_PLANE),
        through_current=2.5,
        pair_count=pair_count,
    )
    weights = dict(branch.weights)

    assert len(branch.children) == 2 * pair_count + 1
    assert len(branch.nodes) == 2 * pair_count + 2
    assert math.fsum(weights.values()) == pytest.approx(1.0)
    assert all(weights[outcome] == pytest.approx(weights[-outcome]) for outcome in weights)
    assert all(child.universe == branch.parent.universe for child in branch.children)
    assert all(child.plane == branch.parent.plane for child in branch.children)
    assert all(
        classify_address_relation(branch.parent, child) is AddressRelation.POSSIBILITY_BRANCH
        for child in branch.children
    )
    assert branch.branch_cut_flux == pytest.approx(2.5)


def test_six_plus_one_is_available_without_becoming_a_plane_count_axiom() -> None:
    branch = symmetric_possibility_branch(state(PROBABILITY_PLANE), pair_count=3)

    assert tuple(outcome for outcome, _ in branch.weights) == (-3, -2, -1, 0, 1, 2, 3)
    assert len(chapter_eight_overlap_topology().planes) != len(branch.children)


def test_branch_mirror_commutes_with_child_construction_and_is_involutive() -> None:
    branch = PossibilityBranch(
        state(
            PROBABILITY_PLANE,
            VesicaUniverseAddress((0, 7, 5)),
            PossibilityAddress((2, 0, -4)),
        ),
        3.0,
        ((-2, 0.1), (-1, 0.2), (0, 0.4), (1, 0.2), (2, 0.1)),
    )
    mirrored = mirror_possibility_branch(branch)

    assert set(mirrored.children) == {mirror_plane_address(child) for child in branch.children}
    assert mirror_possibility_branch(mirrored) == branch


def test_custom_mirror_pair_weights_and_neutral_share_are_allowed() -> None:
    branch = PossibilityBranch(
        state(PROBABILITY_PLANE),
        4.0,
        ((-2, 0.1), (-1, 0.2), (0, 0.4), (1, 0.2), (2, 0.1)),
    )

    assert branch.branch_cut_flux == pytest.approx(4.0)
    currents = {edge.target.possibility.path[-1]: edge.current for edge in branch.outward_edges}
    assert currents == pytest.approx({-2: 0.4, -1: 0.8, 0: 1.6, 1: 0.8, 2: 0.4})


def test_outward_branch_moves_content_while_closed_return_is_stationary() -> None:
    branch = symmetric_possibility_branch(
        state(PROBABILITY_PLANE),
        through_current=1.2,
        pair_count=3,
        neutral_share=0.4,
    )
    before = dict.fromkeys(branch.nodes, 3.0)
    after = continuity_step(branch.nodes, before, branch.outward_edges, dt=0.25)
    stationary = continuity_step(branch.nodes, before, branch.closed_edges, dt=0.25)

    assert after[branch.parent] == pytest.approx(2.7)
    assert total_content(after) == pytest.approx(total_content(before), abs=1e-12)
    assert stationary == pytest.approx(before)
    assert branch.balance_residual < 1e-12
    assert all(edge.channel is FlowChannel.POSSIBILITY_BRANCH for edge in branch.outward_edges)
    assert all(edge.channel is FlowChannel.POSSIBILITY_RETURN for edge in branch.return_edges)


@pytest.mark.parametrize(
    ("weights", "message"),
    (
        (((-1, 0.2), (0, 0.5), (1, 0.2)), "sum to one"),
        (((0, 0.5), (1, 0.5)), "at least one pair"),
        (((-1, 0.2), (0, 0.5), (1, 0.3)), "equal weights"),
        (((-1, -0.1), (0, 1.2), (1, -0.1)), "nonnegative"),
        (((-1, 0.25), (0, 0.5), (0, 0.0), (1, 0.25)), "unique"),
    ),
)
def test_invalid_branch_laws_fail_closed(
    weights: tuple[tuple[int, float], ...],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        PossibilityBranch(state(PROBABILITY_PLANE), 1.0, weights)


def test_invalid_scalar_and_topology_inputs_fail_closed() -> None:
    source = state()
    duplicate_link = PlaneLink(MATERIAL_PLANE, ASTRAL_PLANE)

    with pytest.raises(ValueError, match="nonnegative"):
        symmetric_possibility_branch(source, through_current=-1.0)
    with pytest.raises(ValueError, match="finite"):
        symmetric_possibility_branch(source, through_current=math.nan)
    with pytest.raises(ValueError, match="positive integer"):
        symmetric_possibility_branch(source, pair_count=0)
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        symmetric_possibility_branch(source, neutral_share=1.1)
    with pytest.raises(ValueError, match="only one direct link"):
        PlaneTopology(
            (MATERIAL_PLANE, ASTRAL_PLANE),
            (duplicate_link, duplicate_link),
        )
    with pytest.raises(ValueError, match="snake-case"):
        PlaneId("Material Plane")
    with pytest.raises(ValueError, match="distinct"):
        PlaneLink(MATERIAL_PLANE, MATERIAL_PLANE, PlaneLinkKind.COEXISTENT)


def test_public_transition_annotation_stays_specific() -> None:
    assert get_type_hints(PlaneTransition)["source"] is PlaneAddress
    assert get_type_hints(PossibilityBranch)["parent"] is PlaneAddress
