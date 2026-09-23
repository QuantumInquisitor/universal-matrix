from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import isclose

import pytest

from src.lynchpin_geometry_audit import (
    COLLAPSIBLE_ASSEMBLIES,
    CORE_LYNCHPIN_CONFIGURATIONS,
    DESIGN_PATENT_SHAPES,
    ENHANCED_BUILDING_CONFIGURATIONS,
    LYNCHPIN_PANELS,
    LYNCHPIN_TRIPLE_HINGES,
    PENTAGON_INTERIOR_ANGLE_DEGREES,
    PENTAGON_INTERIOR_COSINE,
    TETRAHEDRAL_RAY_COSINE,
    AuditStatus,
    connected_dodecahedral_six_face_subsets,
    dodecahedral_face_adjacencies,
    dodecahedral_six_face_orbits,
    equal_ray_angle_degrees,
    equiangular_gram_determinant,
    equiangular_ray_rank,
    icosahedral_symmetry_groups,
    local_hinge_cosine,
    lynchpin_opposite_panel_pairs,
    lynchpin_panel_adjacencies,
    lynchpin_panel_degrees,
    metric_area_scale,
    modified_dodecahedron_panel_ledger,
    regular_polygon_interior_angle_degrees,
    tetrahedral_panel_symmetry_groups,
    unit_square_split_areas,
)
from src.platonic_solid_bridge import ONE, ZERO, PhiNumber, solid_signature


def test_six_lynchpin_panels_are_the_six_tetrahedron_edges():
    assert len(LYNCHPIN_PANELS) == 6
    assert len(set(LYNCHPIN_PANELS)) == 6
    assert all(len(panel) == 2 for panel in LYNCHPIN_PANELS)
    assert {vertex for panel in LYNCHPIN_PANELS for vertex in panel} == set(range(4))


def test_four_triple_hinges_are_the_four_tetrahedron_vertex_stars():
    assert len(LYNCHPIN_TRIPLE_HINGES) == 4
    assert all(len(hinge) == 3 for hinge in LYNCHPIN_TRIPLE_HINGES)
    assert Counter(panel for hinge in LYNCHPIN_TRIPLE_HINGES for panel in hinge) == {
        panel: 2 for panel in range(6)
    }


def test_panel_adjacency_is_exactly_the_octahedral_graph():
    adjacencies = lynchpin_panel_adjacencies()
    opposites = lynchpin_opposite_panel_pairs()

    assert len(adjacencies) == 12
    assert lynchpin_panel_degrees() == (4, 4, 4, 4, 4, 4)
    assert len(opposites) == 3
    assert {frozenset(edge) for edge in adjacencies}.isdisjoint(
        frozenset(frozenset(edge) for edge in opposites)
    )
    assert solid_signature("octahedron")[:2] == (6, 12)


def test_triple_hinges_are_non_manifold_even_though_adjacency_is_octahedral():
    assert all(len(hinge) > 2 for hinge in LYNCHPIN_TRIPLE_HINGES)
    hinge_triangles = {frozenset(hinge) for hinge in LYNCHPIN_TRIPLE_HINGES}
    graph_edges = {frozenset(edge) for edge in lynchpin_panel_adjacencies()}
    graph_triangles = {
        frozenset(candidate)
        for candidate in combinations(range(6), 3)
        if all(frozenset(edge) in graph_edges for edge in combinations(candidate, 2))
    }

    assert len(hinge_triangles) == 4
    assert len(graph_triangles) == 8
    assert hinge_triangles < graph_triangles


def test_incidence_has_twelve_proper_and_twenty_four_full_tetrahedral_symmetries():
    proper, full = tetrahedral_panel_symmetry_groups()
    hinges = {frozenset(hinge) for hinge in LYNCHPIN_TRIPLE_HINGES}

    assert len(proper) == 12
    assert len(full) == 24
    for action in full:
        assert {frozenset(action[index] for index in hinge) for hinge in hinges} == hinges


def test_regular_pentagon_hinge_rays_require_four_dimensions_if_kept_exact():
    assert PENTAGON_INTERIOR_ANGLE_DEGREES == regular_polygon_interior_angle_degrees(5) == 108
    assert equiangular_gram_determinant(4, PENTAGON_INTERIOR_COSINE) != ZERO
    assert equiangular_ray_rank(4, PENTAGON_INTERIOR_COSINE) == 4


def test_exact_three_dimensional_closure_requires_tetrahedral_not_pentagonal_angle():
    assert equiangular_gram_determinant(4, TETRAHEDRAL_RAY_COSINE) == ZERO
    assert equiangular_ray_rank(4, TETRAHEDRAL_RAY_COSINE) == 3
    assert isclose(equal_ray_angle_degrees(TETRAHEDRAL_RAY_COSINE), 109.47122063449069)
    assert not isclose(
        equal_ray_angle_degrees(TETRAHEDRAL_RAY_COSINE),
        float(PENTAGON_INTERIOR_ANGLE_DEGREES),
    )


def test_local_three_panel_separation_exposes_the_same_angle_tradeoff():
    assert local_hinge_cosine(TETRAHEDRAL_RAY_COSINE) == PhiNumber(Fraction(-1, 2))
    assert isclose(
        equal_ray_angle_degrees(local_hinge_cosine(TETRAHEDRAL_RAY_COSINE)),
        120.0,
    )
    assert isclose(
        equal_ray_angle_degrees(local_hinge_cosine(PENTAGON_INTERIOR_COSINE)),
        116.56505117707799,
    )


def test_all_shape_triangle_statement_only_works_as_exterior_angles():
    interior = regular_polygon_interior_angle_degrees(3)
    exterior = 180 - interior

    assert interior == 60
    assert exterior == 120
    assert 3 * interior == 180
    assert 3 * exterior == 360


def test_splitting_a_unit_square_does_not_double_ordinary_area():
    areas = unit_square_split_areas()

    assert areas == (Fraction(1, 2), Fraction(1, 2))
    assert sum(areas) == ONE.rational


def test_metric_area_scaling_requires_an_explicit_metric_determinant():
    assert metric_area_scale(1, 0, 1) == 1.0
    assert metric_area_scale(4, 0, 1) == 2.0
    with pytest.raises(ValueError, match="positive definite"):
        metric_area_scale(1, 2, 1)
    with pytest.raises(ValueError, match="positive definite"):
        metric_area_scale(-1, 0, -1)


def test_full_h3_group_acts_on_the_twelve_dodecahedral_faces():
    proper, full = icosahedral_symmetry_groups()

    assert len(dodecahedral_face_adjacencies()) == 30
    assert len(proper) == 60
    assert len(full) == 120
    assert all(sorted(action) == list(range(12)) for action in full)


def test_all_connected_six_face_dodecahedral_patches_are_enumerated():
    subsets = connected_dodecahedral_six_face_subsets()
    full_orbits = dodecahedral_six_face_orbits()
    proper_orbits = dodecahedral_six_face_orbits(include_reflections=False)

    assert len(subsets) == 812
    assert len(full_orbits) == 14
    assert len(proper_orbits) == 20
    assert sum(orbit.orbit_size for orbit in full_orbits) == 812
    assert sum(orbit.orbit_size for orbit in proper_orbits) == 812


def test_six_dodecahedral_patch_classes_have_distinct_mirror_partners():
    full_orbits = dodecahedral_six_face_orbits()

    assert sum(orbit.has_distinct_mirror_partner for orbit in full_orbits) == 6
    assert Counter(orbit.orbit_size for orbit in full_orbits) == {
        10: 1,
        12: 1,
        20: 2,
        30: 3,
        60: 3,
        120: 4,
    }


def test_no_six_face_dodecahedral_patch_has_lynchpin_octahedral_adjacency():
    full_orbits = dodecahedral_six_face_orbits()

    assert max(orbit.internal_adjacencies for orbit in full_orbits) == 10
    assert len(lynchpin_panel_adjacencies()) == 12
    assert all(orbit.degree_sequence != (4, 4, 4, 4, 4, 4) for orbit in full_orbits)


def test_modified_dodecahedron_ledger_exposes_unmapped_panels():
    assert modified_dodecahedron_panel_ledger(4) == (24, 12, 12)
    assert modified_dodecahedron_panel_ledger(5) == (30, 12, 18)
    with pytest.raises(ValueError, match="at least one"):
        modified_dodecahedron_panel_ledger(0)


def test_core_registry_covers_every_lynchpin_patent_figure():
    covered = {
        figure for configuration in CORE_LYNCHPIN_CONFIGURATIONS for figure in configuration.figures
    }

    assert covered == set(range(1, 25))
    assert len({configuration.key for configuration in CORE_LYNCHPIN_CONFIGURATIONS}) == len(
        CORE_LYNCHPIN_CONFIGURATIONS
    )


def test_related_configuration_inventories_are_complete_and_nonduplicated():
    assert len(COLLAPSIBLE_ASSEMBLIES) == 8
    assert len(ENHANCED_BUILDING_CONFIGURATIONS) == 17
    assert (
        len({configuration.description for configuration in ENHANCED_BUILDING_CONFIGURATIONS}) == 17
    )
    assert {configuration.figures[0] for configuration in ENHANCED_BUILDING_CONFIGURATIONS} == {
        2,
        3,
        6,
        9,
        11,
        13,
        15,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
    }
    assert len(DESIGN_PATENT_SHAPES) == 24
    assert len({publication for publication, _ in DESIGN_PATENT_SHAPES}) == 24
    assert ("USD1002750S1", "circular internal Lynchpin structure") in DESIGN_PATENT_SHAPES
    assert ("USD1121503S1", "aerial vehicle") in DESIGN_PATENT_SHAPES


def test_physical_claims_are_not_misclassified_as_exact_geometry():
    propulsion = next(
        configuration
        for configuration in CORE_LYNCHPIN_CONFIGURATIONS
        if configuration.key == "compound_propulsion_pair"
    )

    assert propulsion.status is AuditStatus.UNTESTED_PHYSICAL
    assert all(
        configuration.status is not AuditStatus.EXACT
        for configuration in ENHANCED_BUILDING_CONFIGURATIONS
    )


def test_invalid_polygon_and_ray_requests_are_rejected():
    with pytest.raises(ValueError, match="at least three"):
        regular_polygon_interior_angle_degrees(2)
    with pytest.raises(ValueError, match="at least two"):
        equiangular_ray_rank(1, TETRAHEDRAL_RAY_COSINE)
    with pytest.raises(ValueError, match="not positive semidefinite"):
        equiangular_ray_rank(4, -ONE)
