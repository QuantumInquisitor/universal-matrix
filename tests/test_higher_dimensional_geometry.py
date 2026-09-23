from __future__ import annotations

import pytest

from src.higher_dimensional_geometry import (
    E8_ROOT_COUNT,
    centered_simplex_vertices,
    cross_polytope_projection_multiplicities,
    cross_polytope_vertices,
    d4_subsystem_reflection_closed,
    dot,
    e8_antipodal_pair_count,
    e8_nearest_neighbor_count,
    e8_reflect,
    e8_root_family_counts,
    e8_roots_scaled,
    embed_24_cell_dual_in_e8,
    hypercube_projection_multiplicities,
    hypercube_vertices,
    mirror_closed,
    mirrored_simplex_compound,
    persistent_regular_families,
    squared_distance,
)


@pytest.mark.parametrize("dimension", [2, 3, 4, 5, 8])
def test_regular_family_vertex_counts_and_equal_radii(dimension):
    cube = hypercube_vertices(dimension)
    cross = cross_polytope_vertices(dimension)
    simplex = centered_simplex_vertices(dimension)

    assert len(cube) == 2**dimension
    assert len(cross) == 2 * dimension
    assert len(simplex) == dimension + 1

    assert {dot(vertex, vertex) for vertex in cube} == {dimension}
    assert {dot(vertex, vertex) for vertex in cross} == {1}
    assert {dot(vertex, vertex) for vertex in simplex} == {dimension * (dimension + 1)}


@pytest.mark.parametrize("dimension", [2, 3, 4, 5, 8])
def test_centered_simplex_has_constant_pairwise_distance(dimension):
    simplex = centered_simplex_vertices(dimension)
    expected = 2 * (dimension + 1) ** 2
    distances = {
        squared_distance(left, right)
        for index, left in enumerate(simplex)
        for right in simplex[index + 1 :]
    }
    assert distances == {expected}


@pytest.mark.parametrize("dimension", [3, 4, 5, 8])
def test_mirror_rule_distinguishes_simplex_from_cube_and_cross_polytope(dimension):
    assert mirror_closed(hypercube_vertices(dimension))
    assert mirror_closed(cross_polytope_vertices(dimension))
    assert not mirror_closed(centered_simplex_vertices(dimension))

    compound = mirrored_simplex_compound(dimension)
    assert len(compound) == 2 * (dimension + 1)
    assert mirror_closed(compound)


@pytest.mark.parametrize("dimension", [3, 4, 5, 8])
def test_hypercube_projects_recursively_with_double_multiplicity(dimension):
    projection = dict(hypercube_projection_multiplicities(dimension))
    assert set(projection) == set(hypercube_vertices(dimension - 1))
    assert set(projection.values()) == {2}


@pytest.mark.parametrize("dimension", [3, 4, 5, 8])
def test_cross_polytope_projection_keeps_lower_cross_and_doubles_origin(dimension):
    projection = dict(cross_polytope_projection_multiplicities(dimension))
    origin = (0,) * (dimension - 1)

    assert projection[origin] == 2
    assert {point for point, count in projection.items() if count == 1} == set(
        cross_polytope_vertices(dimension - 1)
    )


def test_only_three_regular_convex_families_persist_from_dimension_five_up():
    assert persistent_regular_families(5) == ("simplex", "hypercube", "cross_polytope")
    assert persistent_regular_families(8) == ("simplex", "hypercube", "cross_polytope")
    with pytest.raises(ValueError):
        persistent_regular_families(4)


def test_e8_exact_root_inventory_and_two_coordinate_families():
    roots = e8_roots_scaled()
    assert len(roots) == E8_ROOT_COUNT == 240
    assert e8_root_family_counts() == ((2, 112), (8, 128))
    assert mirror_closed(roots)
    assert e8_antipodal_pair_count() == 120


def test_e8_reflections_close_the_full_root_system():
    roots = e8_roots_scaled()
    root_set = set(roots)
    for vector in roots:
        for root in roots:
            assert e8_reflect(vector, root) in root_set


def test_e8_root_polytope_has_56_nearest_neighbors_at_every_vertex():
    assert {e8_nearest_neighbor_count(root) for root in e8_roots_scaled()} == {56}


def test_existing_24_cell_dual_embeds_as_a_d4_subsystem_of_e8():
    subsystem = embed_24_cell_dual_in_e8()
    roots = set(e8_roots_scaled())

    assert len(subsystem) == 24
    assert set(subsystem) <= roots
    assert all(root[4:] == (0, 0, 0, 0) for root in subsystem)
    assert all(sum(component != 0 for component in root) == 2 for root in subsystem)
    assert d4_subsystem_reflection_closed()
