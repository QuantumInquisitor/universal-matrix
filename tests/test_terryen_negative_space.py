from math import isclose, sqrt

import pytest

from src.terryology_audit import TERRYEN_WAVE_FIELDS
from src.terryen_negative_space import (
    cech_critical_radius,
    cech_topology,
    central_void_boundary_point,
    equal_sphere_equations,
    heavenly_projection_diagnostic,
    is_in_negative_space,
    negative_space_margin,
    orthographic_basis_4d,
    project_4d_point,
    terryen_center_symmetry,
    terryen_negative_space_window,
    terryen_unit_centers,
    tetra_mirror_completion_matches_huntyen,
)


CASES = (
    ("tetra_terryen", 4, 3, sqrt(8.0 / 9.0), 0.97),
    ("huntyen", 8, 3, sqrt(2.0 / 3.0), 0.90),
    ("mira", 6, 3, sqrt(2.0 / 3.0), 0.90),
    ("aubreyen", 12, 3, sqrt((2.0 - 2.0 / sqrt(5.0)) / 3.0), 0.80),
    ("heavenly", 24, 4, 1.0 / sqrt(2.0), 0.72),
)


def dot(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


@pytest.mark.parametrize(("key", "count", "dimension", "birth", "sample_radius"), CASES)
def test_equal_sphere_families_are_explicit_and_unit_centered(
    key: str,
    count: int,
    dimension: int,
    birth: float,
    sample_radius: float,
) -> None:
    del birth
    centers = terryen_unit_centers(key)
    equations = equal_sphere_equations(key, sample_radius)

    assert len(centers) == len(equations) == count
    assert {len(center) for center in centers} == {dimension}
    assert all(isclose(dot(center, center), 1.0, abs_tol=1e-12) for center in centers)
    assert all(equation.center == center for equation, center in zip(equations, centers, strict=True))
    assert all(equation.radius == sample_radius for equation in equations)

    origin = (0.0,) * dimension
    assert negative_space_margin(key, sample_radius, origin) == pytest.approx(
        1.0 - sample_radius * sample_radius
    )
    assert is_in_negative_space(key, sample_radius, origin)


@pytest.mark.parametrize(("key", "count", "dimension", "birth", "sample_radius"), CASES)
def test_analytic_cavity_windows_match_cech_homology(
    key: str,
    count: int,
    dimension: int,
    birth: float,
    sample_radius: float,
) -> None:
    del count
    window = terryen_negative_space_window(key)
    assert window.birth_radius == pytest.approx(birth)
    assert window.death_radius == 1.0
    assert window.contains(birth)
    assert window.contains(sample_radius)
    assert not window.contains(1.0)

    before_birth = cech_topology(key, birth - 1e-6)
    inside_window = cech_topology(key, sample_radius)
    at_death = cech_topology(key, 1.0)

    assert before_birth.bounded_negative_space_components == 0
    assert inside_window.betti_numbers == (1, *((0,) * (dimension - 2)), 1)
    assert inside_window.bounded_negative_space_components == 1
    assert at_death.betti_numbers == (1, *((0,) * (dimension - 1)))
    assert at_death.bounded_negative_space_components == 0


def test_heavenly_birth_complex_is_a_regression_certificate() -> None:
    topology = cech_topology("heavenly", 1.0 / sqrt(2.0))

    assert topology.ambient_dimension == 4
    assert topology.simplex_counts == (24, 168, 384, 360, 144)
    assert topology.boundary_ranks == (0, 23, 145, 239, 120)
    assert topology.betti_numbers == (1, 0, 0, 1)
    assert topology.bounded_negative_space_components == 1


@pytest.mark.parametrize(("key", "count", "dimension", "birth", "sample_radius"), CASES)
def test_radial_extraction_lands_on_the_negative_space_boundary(
    key: str,
    count: int,
    dimension: int,
    birth: float,
    sample_radius: float,
) -> None:
    del count, dimension, birth
    direction = terryen_unit_centers(key)[0]
    point = central_void_boundary_point(key, sample_radius, direction)

    assert point is not None
    assert negative_space_margin(key, sample_radius, point) == pytest.approx(0.0, abs=1e-10)
    assert negative_space_margin(
        key,
        sample_radius,
        tuple(component * 0.5 for component in point),
    ) > 0.0
    assert negative_space_margin(
        key,
        sample_radius,
        tuple(component * 1.01 for component in point),
    ) < 0.0


def test_tetrahedral_facet_controls_the_first_cavity_birth() -> None:
    birth = terryen_negative_space_window("tetra_terryen").birth_radius

    assert cech_critical_radius("tetra_terryen", (0, 1, 2)) == pytest.approx(birth)
    assert cech_critical_radius("tetra_terryen", (0, 1, 2, 3)) == pytest.approx(1.0)


@pytest.mark.parametrize(("key", "count", "dimension", "birth", "sample_radius"), CASES)
def test_center_sets_have_uniform_distance_profiles(
    key: str,
    count: int,
    dimension: int,
    birth: float,
    sample_radius: float,
) -> None:
    del birth, sample_radius
    diagnostic = terryen_center_symmetry(key)

    assert diagnostic.point_count == count
    assert diagnostic.dimension == dimension
    assert diagnostic.centroid_residual < 1e-12
    assert diagnostic.common_radius_residual < 1e-12
    assert diagnostic.uniform_distance_profile
    assert sum(diagnostic.shell_multiplicities) == count - 1


def test_mirroring_is_explicit_in_four_candidates_and_completes_the_tetrahedron() -> None:
    assert not terryen_center_symmetry("tetra_terryen").centrally_symmetric
    assert tetra_mirror_completion_matches_huntyen()

    for key in ("huntyen", "mira", "aubreyen", "heavenly"):
        diagnostic = terryen_center_symmetry(key)
        assert diagnostic.centrally_symmetric
        assert diagnostic.mirror_permutation is not None
        assert all(
            diagnostic.mirror_permutation[opposite] == index
            for index, opposite in enumerate(diagnostic.mirror_permutation)
        )


def test_central_mirroring_preserves_the_implicit_field() -> None:
    point = (0.17, -0.11, 0.23)
    for key in ("huntyen", "mira", "aubreyen"):
        assert negative_space_margin(key, 0.9, point) == pytest.approx(
            negative_space_margin(key, 0.9, tuple(-value for value in point)),
            abs=1e-12,
        )


def test_controlled_heavenly_projection_is_orthonormal_distinct_and_mirrored() -> None:
    diagnostic = heavenly_projection_diagnostic()

    assert len(diagnostic.projected_centers) == 24
    assert diagnostic.distinct_projected_centers == 24
    assert diagnostic.orthonormal_residual < 1e-12
    assert diagnostic.mirror_residual < 1e-12

    basis = orthographic_basis_4d()
    view = diagnostic.normalized_view_direction
    assert all(dot(direction, view) == pytest.approx(0.0, abs=1e-12) for direction in basis)

    point = (0.5, -0.5, 0.5, -0.5)
    projection = project_4d_point(point)
    mirrored = project_4d_point(tuple(-value for value in point))
    assert mirrored == pytest.approx(tuple(-value for value in projection), abs=1e-12)


@pytest.mark.parametrize(
    ("callable_object", "args"),
    (
        (equal_sphere_equations, ("mira", -0.1)),
        (cech_topology, ("mira", -0.1)),
        (central_void_boundary_point, ("mira", 1.0, (1.0, 0.0, 0.0))),
        (orthographic_basis_4d, ((1.0, 2.0, 3.0),)),
        (project_4d_point, ((1.0, 2.0, 3.0),)),
    ),
)
def test_invalid_geometry_inputs_fail_closed(callable_object: object, args: tuple[object, ...]) -> None:
    with pytest.raises(ValueError):
        callable_object(*args)  # type: ignore[operator]
