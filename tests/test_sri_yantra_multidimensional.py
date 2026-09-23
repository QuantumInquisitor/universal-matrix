from fractions import Fraction
from math import sqrt

import pytest

from src.sevenfold_seed_contract import VesicaUniverseAddress
from src.sri_yantra_multidimensional import (
    CANONICAL_AVARANAS,
    CANONICAL_GENERATORS,
    CANONICAL_SRI_YANTRA,
    MERU_REALIZATION,
    PLANE_REALIZATION,
    SPHERICAL_REALIZATION,
    SPIRAL_CONE_REALIZATION,
    STATE_SPACE_FACTORS,
    AvaranaId,
    AvaranaSpec,
    ComponentKind,
    CurvatureKind,
    FlowSense,
    GeneratorOrientation,
    RealizationKind,
    RealizedYantraState,
    ShellCurrent,
    SriYantraComplex,
    YantraFiberAddress,
    YantraGenerator,
    YantraLocation,
    YantraRealization,
    avarana_spec,
    candidate_spherical_shell_point,
    candidate_spiral_cone_point,
    centered_simplex_vertices,
    closed_shell_circulation,
    cyclic_mirror_location,
    lift_all_generators,
    lift_realized_state,
    mirror_realized_state,
    mirror_yantra_address,
    project_realized_state,
    reverse_flow,
    reverse_handedness,
    shell_currents,
    shell_divergence,
    simplex_field_realization,
    uniform_component_flux,
)
from src.transitive_plane_branching import (
    DREAM_PLANE,
    MATERIAL_PLANE,
    PlaneAddress,
    PossibilityAddress,
)

_BASE = PlaneAddress(
    VesicaUniverseAddress((0, 7)),
    MATERIAL_PLANE,
    PossibilityAddress((-2, 0, 3)),
)


def fiber_address(
    avarana: AvaranaId = AvaranaId.TRIANGLES_FOURTEEN,
    member: int = 3,
    phase: Fraction = Fraction(1, 7),
) -> YantraFiberAddress:
    return YantraFiberAddress(_BASE, YantraLocation(avarana, member), phase)


def squared_distance(left, right):
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def test_canonical_inventory_keeps_source_counts_independent_of_embedding() -> None:
    assert len(CANONICAL_SRI_YANTRA.avaranas) == 9
    assert len(CANONICAL_SRI_YANTRA.generators) == 9
    assert CANONICAL_SRI_YANTRA.generator_count(GeneratorOrientation.UPWARD) == 4
    assert CANONICAL_SRI_YANTRA.generator_count(GeneratorOrientation.DOWNWARD) == 5
    assert CANONICAL_SRI_YANTRA.triangular_cell_count == 14 + 10 + 10 + 8 + 1 == 43
    assert CANONICAL_SRI_YANTRA.lotus_petal_count == 16 + 8 == 24
    assert CANONICAL_SRI_YANTRA.boundary_gate_count == 4


def test_avaranas_are_contiguous_and_ordered_from_boundary_to_bindu() -> None:
    assert tuple(spec.ordinal for spec in CANONICAL_AVARANAS) == tuple(range(1, 10))
    assert CANONICAL_AVARANAS[0].identifier is AvaranaId.BHUPURA
    assert CANONICAL_AVARANAS[-1].identifier is AvaranaId.BINDU
    assert avarana_spec(AvaranaId.BINDU).component_kind is ComponentKind.BINDU
    assert avarana_spec(AvaranaId.BINDU).component_count == 1


def test_custom_complex_rejects_noncontiguous_avaranas_and_generators() -> None:
    skipped = (
        AvaranaSpec(1, AvaranaId.BHUPURA, ComponentKind.BOUNDARY_GATE, 4),
        AvaranaSpec(3, AvaranaId.BINDU, ComponentKind.BINDU, 1),
    )
    with pytest.raises(ValueError, match="contiguous outer-to-inner"):
        SriYantraComplex(skipped, CANONICAL_GENERATORS)

    skipped_generator = (
        YantraGenerator(GeneratorOrientation.UPWARD, 1),
        YantraGenerator(GeneratorOrientation.UPWARD, 3),
    )
    with pytest.raises(ValueError, match="family indices"):
        SriYantraComplex(CANONICAL_AVARANAS, skipped_generator)


def test_location_bounds_use_each_enclosures_own_component_count() -> None:
    assert YantraLocation(AvaranaId.LOTUS_SIXTEEN, 15).member_count == 16
    assert YantraLocation(AvaranaId.BINDU).member_count == 1

    with pytest.raises(ValueError, match="0..15"):
        YantraLocation(AvaranaId.LOTUS_SIXTEEN, 16)
    with pytest.raises(ValueError, match="0..0"):
        YantraLocation(AvaranaId.BINDU, 1)


def test_cyclic_mirror_is_an_involution_on_every_enclosure() -> None:
    for spec in CANONICAL_AVARANAS:
        for member in range(spec.component_count):
            location = YantraLocation(spec.identifier, member)
            mirrored = cyclic_mirror_location(location)

            assert mirrored.avarana is location.avarana
            assert cyclic_mirror_location(mirrored) == location

    assert cyclic_mirror_location(YantraLocation(AvaranaId.BINDU)) == YantraLocation(
        AvaranaId.BINDU
    )


def test_fibre_address_adds_local_coordinates_without_collapsing_base_factors() -> None:
    address = fiber_address()
    moved_base = PlaneAddress(
        address.base.universe.child(5),
        DREAM_PLANE,
        address.base.possibility.child(-1),
    )
    moved = address.over(moved_base)

    assert moved.base == moved_base
    assert moved.location == address.location
    assert moved.phase == address.phase
    assert moved.base.universe.depth == address.base.universe.depth + 1
    assert moved.base.plane is DREAM_PLANE
    assert moved.base.possibility.depth == address.base.possibility.depth + 1


def test_phase_is_a_normalized_independent_circle_coordinate() -> None:
    address = fiber_address(phase=Fraction(8, 7))

    assert address.phase == Fraction(1, 7)
    assert address.advanced(Fraction(13, 14)).phase == Fraction(1, 14)
    assert address.advanced(1) == address


def test_full_address_mirror_is_involutive_and_keeps_enclosure_depth() -> None:
    address = fiber_address(member=5, phase=Fraction(2, 9))
    mirrored = mirror_yantra_address(address)

    assert mirrored.location.avarana is address.location.avarana
    assert mirrored.location.member == (-address.location.member) % address.location.member_count
    assert mirrored.phase == Fraction(7, 9)
    assert mirror_yantra_address(mirrored) == address


def test_documented_forms_distinguish_intrinsic_and_ambient_dimension() -> None:
    assert (
        PLANE_REALIZATION.intrinsic_dimension,
        PLANE_REALIZATION.ambient_dimension,
        PLANE_REALIZATION.curvature,
    ) == (2, 2, CurvatureKind.FLAT)
    assert (
        SPHERICAL_REALIZATION.intrinsic_dimension,
        SPHERICAL_REALIZATION.ambient_dimension,
        SPHERICAL_REALIZATION.curvature,
    ) == (2, 3, CurvatureKind.POSITIVE)
    assert (
        MERU_REALIZATION.intrinsic_dimension,
        MERU_REALIZATION.ambient_dimension,
        MERU_REALIZATION.curvature,
    ) == (3, 3, CurvatureKind.MIXED_OR_PIECEWISE)


@pytest.mark.parametrize("dimension", (2, 3, 4, 7, 13))
def test_simplex_field_is_open_to_arbitrary_supported_dimension(dimension: int) -> None:
    realization = simplex_field_realization(dimension)

    assert realization.kind is RealizationKind.SIMPLEX_FIELD_CANDIDATE
    assert realization.intrinsic_dimension == dimension
    assert realization.ambient_dimension == dimension + 1


def test_invalid_dimension_signatures_fail_closed() -> None:
    with pytest.raises(ValueError, match="fixed dimension signature"):
        YantraRealization(RealizationKind.PLANE, 2, 3, CurvatureKind.FLAT)
    with pytest.raises(ValueError, match=r"d \+ 1"):
        YantraRealization(
            RealizationKind.SIMPLEX_FIELD_CANDIDATE,
            4,
            4,
            CurvatureKind.FLAT,
        )
    with pytest.raises(ValueError, match="at least two"):
        simplex_field_realization(1)


def test_projection_and_lift_change_only_the_realization() -> None:
    plane_state = RealizedYantraState(fiber_address(), PLANE_REALIZATION, FlowSense.INWARD)
    lifted = lift_realized_state(plane_state, MERU_REALIZATION)
    projected = project_realized_state(lifted, PLANE_REALIZATION)

    assert lifted.address == plane_state.address
    assert lifted.flow is plane_state.flow
    assert lifted.realization is MERU_REALIZATION
    assert projected == plane_state

    with pytest.raises(ValueError, match="cannot increase"):
        project_realized_state(plane_state, MERU_REALIZATION)
    with pytest.raises(ValueError, match="cannot decrease"):
        lift_realized_state(lifted, PLANE_REALIZATION)


def test_state_mirror_flow_reversal_and_chirality_are_independent_involutions() -> None:
    state = RealizedYantraState(
        fiber_address(),
        SPIRAL_CONE_REALIZATION,
        FlowSense.INWARD,
        handedness=-1,
    )

    assert mirror_realized_state(mirror_realized_state(state)) == state
    assert reverse_flow(reverse_flow(state)) == state
    assert reverse_handedness(reverse_handedness(state)) == state
    assert mirror_realized_state(reverse_flow(state)) == reverse_flow(mirror_realized_state(state))
    assert mirror_realized_state(state).flow is FlowSense.INWARD
    assert reverse_flow(state).flow is FlowSense.OUTWARD


def test_inward_shell_current_has_constant_cut_flux_and_zero_internal_divergence() -> None:
    currents = shell_currents(3.5, FlowSense.INWARD)
    divergence = shell_divergence(currents)

    assert len(currents) == len(CANONICAL_AVARANAS) - 1
    assert all(current.magnitude == pytest.approx(3.5) for current in currents)
    assert currents[0].source is AvaranaId.BHUPURA
    assert currents[-1].target is AvaranaId.BINDU
    assert divergence[AvaranaId.BHUPURA] == pytest.approx(3.5)
    assert divergence[AvaranaId.BINDU] == pytest.approx(-3.5)
    assert all(abs(divergence[spec.identifier]) < 1e-12 for spec in CANONICAL_AVARANAS[1:-1])


def test_outward_shell_current_is_the_exact_route_reverse() -> None:
    inward = shell_currents(2.0, FlowSense.INWARD)
    outward = shell_currents(2.0, FlowSense.OUTWARD)

    assert outward == tuple(current.reversed() for current in reversed(inward))


def test_equal_inward_and_outward_routes_make_closed_zero_divergence_circulation() -> None:
    divergence = shell_divergence(closed_shell_circulation(1.25))

    assert all(value == pytest.approx(0.0) for value in divergence.values())


def test_uniform_component_flux_preserves_cut_flux_across_unequal_counts() -> None:
    total_flux = 5.0
    for spec in CANONICAL_AVARANAS:
        component_flux = uniform_component_flux(total_flux, spec.identifier)

        assert len(component_flux) == spec.component_count
        assert sum(component_flux) == pytest.approx(total_flux)


def test_invalid_shell_currents_and_fluxes_fail_closed() -> None:
    with pytest.raises(ValueError, match="adjacent"):
        ShellCurrent(AvaranaId.BHUPURA, AvaranaId.LOTUS_EIGHT, 1.0)
    with pytest.raises(ValueError, match="nonnegative"):
        shell_currents(-1.0, FlowSense.INWARD)
    with pytest.raises(ValueError, match="stationary"):
        shell_currents(1.0, FlowSense.STATIONARY)
    assert shell_currents(0.0, FlowSense.STATIONARY) == ()


@pytest.mark.parametrize("dimension", (2, 3, 4, 7))
def test_centered_simplex_is_regular_centered_and_zero_sum(dimension: int) -> None:
    vertices = centered_simplex_vertices(dimension)

    assert len(vertices) == dimension + 1
    assert all(len(vertex) == dimension + 1 for vertex in vertices)
    assert all(sum(vertex) == 0 for vertex in vertices)
    assert all(sum(vertex[axis] for vertex in vertices) == 0 for axis in range(dimension + 1))
    assert {
        squared_distance(vertices[left], vertices[right])
        for left in range(len(vertices))
        for right in range(left + 1, len(vertices))
    } == {2}


@pytest.mark.parametrize("dimension", (2, 3, 4, 7))
def test_opposite_simplex_orientation_is_exact_central_inversion(dimension: int) -> None:
    upward = centered_simplex_vertices(dimension, GeneratorOrientation.UPWARD)
    downward = centered_simplex_vertices(dimension, GeneratorOrientation.DOWNWARD)

    assert downward == tuple(tuple(-component for component in vertex) for vertex in upward)


def test_simplex_compound_recovers_six_triangle_and_eight_tetrahedron_vertices() -> None:
    triangle_compound = {
        *centered_simplex_vertices(2, GeneratorOrientation.UPWARD),
        *centered_simplex_vertices(2, GeneratorOrientation.DOWNWARD),
    }
    tetrahedron_compound = {
        *centered_simplex_vertices(3, GeneratorOrientation.UPWARD),
        *centered_simplex_vertices(3, GeneratorOrientation.DOWNWARD),
    }

    assert len(triangle_compound) == 6
    assert len(tetrahedron_compound) == 8


def test_all_nine_generators_lift_without_losing_four_plus_five_orientation() -> None:
    lifted = lift_all_generators(4)

    assert len(lifted) == 9
    assert sum(item.generator.orientation is GeneratorOrientation.UPWARD for item in lifted) == 4
    assert sum(item.generator.orientation is GeneratorOrientation.DOWNWARD for item in lifted) == 5
    assert all(item.dimension == 4 and len(item.vertices) == 5 for item in lifted)


def test_spiral_cone_chart_places_boundary_on_base_and_bindu_at_apex() -> None:
    boundary_state = RealizedYantraState(
        fiber_address(AvaranaId.BHUPURA, member=0, phase=Fraction(0)),
        SPIRAL_CONE_REALIZATION,
    )
    bindu_state = RealizedYantraState(
        fiber_address(AvaranaId.BINDU, member=0, phase=Fraction(3, 7)),
        SPIRAL_CONE_REALIZATION,
    )

    assert candidate_spiral_cone_point(boundary_state, 2.0, 5.0) == pytest.approx((2.0, 0.0, 0.0))
    assert candidate_spiral_cone_point(bindu_state, 2.0, 5.0) == pytest.approx((0.0, 0.0, 5.0))


def test_spiral_cone_chart_is_equivariant_under_the_address_mirror() -> None:
    state = RealizedYantraState(
        fiber_address(AvaranaId.TRIANGLES_FOURTEEN, member=4, phase=Fraction(1, 9)),
        SPIRAL_CONE_REALIZATION,
        handedness=-1,
    )
    point = candidate_spiral_cone_point(state)
    mirrored = candidate_spiral_cone_point(mirror_realized_state(state))

    assert mirrored == pytest.approx((point[0], -point[1], point[2]))


def test_spherical_chart_is_unit_norm_and_keeps_bindu_fixed_at_pole() -> None:
    address = fiber_address(AvaranaId.TRIANGLES_EIGHT, member=3, phase=Fraction(1, 11))
    point = candidate_spherical_shell_point(address)
    bindu = candidate_spherical_shell_point(fiber_address(AvaranaId.BINDU, member=0))

    assert sqrt(sum(component**2 for component in point)) == pytest.approx(1.0)
    assert bindu == pytest.approx((0.0, 0.0, 1.0))


def test_spherical_chart_mirror_is_an_exact_azimuthal_reflection() -> None:
    address = fiber_address(AvaranaId.LOTUS_SIXTEEN, member=5, phase=Fraction(2, 13))
    point = candidate_spherical_shell_point(address)
    mirrored = candidate_spherical_shell_point(mirror_yantra_address(address))

    assert mirrored == pytest.approx((point[0], -point[1], point[2]))


def test_state_space_names_keep_geometry_and_engine_axes_explicitly_separate() -> None:
    assert STATE_SPACE_FACTORS[:3] == (
        "recursive_universe",
        "named_plane",
        "possibility_path",
    )
    assert {"avarana", "phase", "realization", "flow", "handedness"} < set(STATE_SPACE_FACTORS)
