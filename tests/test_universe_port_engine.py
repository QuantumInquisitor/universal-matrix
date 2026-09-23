from math import isclose, pi, sqrt

import pytest

from src.canonical_kernel import polarity
from src.sevenfold_seed_contract import VesicaUniverseAddress, seed_vesicas
from src.terryen_negative_space import terryen_negative_space_window
from src.universe_port_engine import (
    CONTAINED_RECURSION_SCALE,
    CircleVessel,
    PolarityFlow,
    ScaleTransferDirection,
    TreePillar,
    central_mirror_point,
    flower_adjacencies,
    flower_axial_coordinates,
    flower_circle_count,
    flower_circles,
    flower_port_count,
    mirror_universe_address,
    negative_space_aperture,
    recursive_universe_count,
    seed_circles,
    seed_vesica_geometry,
    tree_from_flower,
    tree_pillar,
    universe_domain,
    universe_port_geometry,
    universe_port_state,
)

TERRYEN_KEYS = ("tetra_terryen", "huntyen", "mira", "aubreyen", "heavenly")


def assert_point_close(left: tuple[float, float], right: tuple[float, float]) -> None:
    assert left == pytest.approx(right, abs=1e-12)


def test_contained_seed_is_one_center_plus_six_equal_ring_circles() -> None:
    vessel = CircleVessel((2.0, -3.0), 8.0)
    circles = seed_circles(vessel)

    assert len(circles) == 7
    assert circles[0].center == vessel.center
    assert {circle.radius for circle in circles} == {4.0}
    assert all(vessel.contains_circle(circle) for circle in circles)
    assert isclose(circles[0].shell_residual(vessel.center), -4.0)
    assert all(isclose(circle.shell_residual(vessel.center), 0.0) for circle in circles[1:])


def test_twelve_seed_ports_have_exact_equal_circle_vesica_geometry() -> None:
    vessel = CircleVessel(radius=4.0)
    expected_area = (2.0 * pi / 3.0 - sqrt(3.0) / 2.0) * 4.0

    for index in range(len(seed_vesicas())):
        port = seed_vesica_geometry(vessel, index)
        first, second = port.generator_circles

        assert port.seed_positions == seed_vesicas()[index]
        assert port.minor_axis_length == pytest.approx(2.0)
        assert port.major_axis_length == pytest.approx(2.0 * sqrt(3.0))
        assert port.lens_area == pytest.approx(expected_area)
        assert port.child_vessel.radius == pytest.approx(1.0)
        assert first.shell_residual(port.cusp_points[0]) == pytest.approx(0.0, abs=1e-12)
        assert second.shell_residual(port.cusp_points[0]) == pytest.approx(0.0, abs=1e-12)
        assert port.contained


def test_every_universe_contains_a_complete_seed_and_twelve_child_ports() -> None:
    root = CircleVessel(radius=16.0)
    parent_address = VesicaUniverseAddress((0, 7))
    parent = universe_domain(parent_address, root)
    children = tuple(
        universe_port_geometry(parent_address.child(index), root) for index in range(12)
    )

    assert parent.radius == pytest.approx(16.0 * CONTAINED_RECURSION_SCALE**2)
    assert len(children) == 12
    assert all(parent.contains_circle(child.child_vessel) for child in children)
    assert all(
        child.child_vessel.radius == pytest.approx(parent.radius / 4.0) for child in children
    )
    assert recursive_universe_count(0) == 1
    assert recursive_universe_count(1) == 12
    assert recursive_universe_count(4) == 12**4


def test_recursive_radius_law_has_no_arbitrary_depth_cutoff() -> None:
    root = CircleVessel(radius=1024.0)
    for depth in range(9):
        address = VesicaUniverseAddress((0,) * depth)
        assert universe_domain(address, root).radius == pytest.approx(
            root.radius * CONTAINED_RECURSION_SCALE**depth
        )


def test_recursive_address_mirror_is_an_exact_spatial_involution() -> None:
    root = CircleVessel((3.5, -1.25), 10.0)
    address = VesicaUniverseAddress((0, 7, 5, 11))
    mirrored_address = mirror_universe_address(address)
    domain = universe_domain(address, root)
    mirrored_domain = universe_domain(mirrored_address, root)
    port = universe_port_geometry(address, root)
    mirrored_port = universe_port_geometry(mirrored_address, root)

    assert mirror_universe_address(mirrored_address) == address
    assert mirrored_domain.radius == pytest.approx(domain.radius)
    assert_point_close(
        mirrored_domain.center,
        central_mirror_point(domain.center, root.center),
    )
    assert_point_close(
        mirrored_port.neutral_center,
        central_mirror_point(port.neutral_center, root.center),
    )
    for cusp, mirrored_cusp in zip(
        port.cusp_points,
        mirrored_port.cusp_points,
        strict=True,
    ):
        assert_point_close(mirrored_cusp, central_mirror_point(cusp, root.center))


@pytest.mark.parametrize("rings", range(5))
def test_flower_growth_has_exact_hex_disk_circle_and_port_counts(rings: int) -> None:
    nodes = flower_axial_coordinates(rings)
    edges = flower_adjacencies(rings)

    assert len(nodes) == flower_circle_count(rings) == 1 + 3 * rings * (rings + 1)
    assert len(edges) == flower_port_count(rings) == 9 * rings * rings + 3 * rings
    assert len(set(nodes)) == len(nodes)
    assert len(set(edges)) == len(edges)


def test_flower_expansion_preserves_equal_radius_while_recursion_scales_inward() -> None:
    flower = flower_circles(2, radius=3.0)
    nested = universe_domain(VesicaUniverseAddress((0, 1)), CircleVessel(radius=3.0))

    assert len(flower) == 19
    assert {circle.radius for _, circle in flower} == {3.0}
    assert nested.radius == pytest.approx(3.0 / 16.0)


def test_tree_is_derived_from_flower_with_mirrored_inner_outer_routes() -> None:
    tree = tree_from_flower(2)

    assert len(tree.nodes) == 19
    assert len(tree.edges) == 42
    assert set(tree.outward_routes) == {(target, source) for source, target in tree.inward_routes}
    assert set(tree.edges) == {tuple(sorted(route)) for route in tree.outward_routes} | set(
        tree.transverse_edges
    )
    assert len(tree.nodes_on(TreePillar.POSITIVE)) == len(tree.nodes_on(TreePillar.NEGATIVE))
    assert tree.nodes_on(TreePillar.NEUTRAL) == ((0, 0), (-1, 2), (1, -2))


def test_tree_pillars_exchange_under_central_mirror_and_fix_neutral() -> None:
    opposite = {
        TreePillar.NEGATIVE: TreePillar.POSITIVE,
        TreePillar.NEUTRAL: TreePillar.NEUTRAL,
        TreePillar.POSITIVE: TreePillar.NEGATIVE,
    }
    for coordinate in flower_axial_coordinates(3):
        mirrored = -coordinate[0], -coordinate[1]
        assert tree_pillar(mirrored) is opposite[tree_pillar(coordinate)]


@pytest.mark.parametrize("key", TERRYEN_KEYS)
def test_every_explicit_terryen_candidate_can_open_one_bounded_aperture(key: str) -> None:
    window = terryen_negative_space_window(key)
    sample_radius = (window.birth_radius + window.death_radius) / 2.0
    aperture = negative_space_aperture(key, sample_radius)

    assert aperture.key == key
    assert aperture.bounded_components == 1
    assert aperture.open


def test_aperture_closes_before_birth_and_at_cavity_death() -> None:
    window = terryen_negative_space_window("heavenly")

    assert not negative_space_aperture("heavenly", window.birth_radius - 1e-5).open
    assert negative_space_aperture("heavenly", window.birth_radius).open
    assert not negative_space_aperture("heavenly", window.death_radius).open


def test_port_clock_has_outward_inward_and_two_neutral_transfer_crossings() -> None:
    address = VesicaUniverseAddress((0,))
    radius = 0.9
    states = {
        tick: universe_port_state(address, 2, tick, "mira", radius) for tick in (0, 9, 18, 27, 36)
    }

    assert states[0].polarity_flow is PolarityFlow.OUTWARD
    assert states[0].scale_transfer is ScaleTransferDirection.BALANCED
    assert states[9].polarity_flow is PolarityFlow.NEUTRAL
    assert states[9].scale_transfer is ScaleTransferDirection.INTO_CHILD
    assert states[18].polarity_flow is PolarityFlow.INWARD
    assert states[18].scale_transfer is ScaleTransferDirection.BALANCED
    assert states[27].polarity_flow is PolarityFlow.NEUTRAL
    assert states[27].scale_transfer is ScaleTransferDirection.INTO_PARENT
    assert states[36].polarity_flow is PolarityFlow.OUTWARD
    assert states[36].core_state == states[0].core_state
    assert all(state.active for state in states.values())


def test_adjacent_scales_reverse_orientation_and_funnel_polarity() -> None:
    parent = universe_port_state(
        VesicaUniverseAddress((0,)),
        0,
        0,
        "huntyen",
        0.9,
    )
    child = universe_port_state(
        VesicaUniverseAddress((0, 0)),
        0,
        0,
        "huntyen",
        0.9,
    )

    assert parent.orientation == 1
    assert child.orientation == -1
    assert parent.polarity_flow is PolarityFlow.OUTWARD
    assert child.polarity_flow is PolarityFlow.INWARD
    assert parent.polarity_carrier == pytest.approx(-child.polarity_carrier)
    assert parent.funnel_source is not None
    assert parent.funnel_sink is not None
    assert parent.funnel_source != parent.funnel_sink


def test_port_state_carries_exact_108_pairing_without_claiming_physical_identity() -> None:
    states = {
        universe_port_state(
            VesicaUniverseAddress((index % 12,)),
            channel,
            tick,
            "mira",
            0.9,
        )
        for channel in range(3)
        for tick in range(36)
        for index in (0,)
    }

    assert len({state.core_state for state in states}) == 108
    assert all(state.paired_core_state == polarity(state.core_state) for state in states)


@pytest.mark.parametrize(
    ("callable_object", "args", "error"),
    (
        (CircleVessel, ((0.0, 0.0), 0.0), ValueError),
        (recursive_universe_count, (-1,), ValueError),
        (flower_axial_coordinates, (-1,), ValueError),
        (tree_from_flower, (0,), ValueError),
        (universe_port_geometry, (VesicaUniverseAddress(),), ValueError),
        (
            universe_port_state,
            (VesicaUniverseAddress((0,)), 3, 0, "mira", 0.9),
            ValueError,
        ),
        (
            universe_port_state,
            (VesicaUniverseAddress((0,)), 0, 0.5, "mira", 0.9),
            TypeError,
        ),
    ),
)
def test_invalid_port_inputs_fail_closed(
    callable_object: object,
    args: tuple[object, ...],
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        callable_object(*args)  # type: ignore[operator]
