from fractions import Fraction
from math import isclose, sqrt

import pytest

from src.platonic_solid_bridge import (
    CUBE_VERTICES,
    DUAL_SOLID_NAMES,
    MIRROR_TETRAHEDRON_VERTICES,
    TETRAHEDRON_VERTICES,
    solid_signature,
)
from src.terryology_audit import (
    KNOWN_KISSING_NUMBERS,
    SQRT_TWO,
    TERRYEN_WAVE_FIELDS,
    TERRYOLOGY_CLAIMS,
    DimensionalMonomial,
    EvidenceStatus,
    SolutionMultiplicity,
    SqrtTwoNumber,
    audit_operation_on_samples,
    decimal_sqrt_two_square_residual,
    howard_literal_product,
    ordinary_product,
    participant_union_count,
    symmetric_one_one_patch,
    terryen_candidate_vertices,
    terryen_spherical_code_certificate,
    terryen_wave_field,
    tetrahedral_mirror_completion,
    within_known_kissing_bound,
    zero_product_solution_multiplicity,
)
from src.twenty_four_cell_bridge import (
    TWENTY_FOUR_CELL_VERTICES,
    twenty_four_cell_edges,
    twenty_four_cell_facets,
    twenty_four_cell_triangular_faces,
    twenty_four_cell_vertices_from_tetrahedron,
)


def test_claim_registry_separates_arithmetic_geometry_and_physics():
    assert len(TERRYOLOGY_CLAIMS) == 6
    assert len({claim.key for claim in TERRYOLOGY_CLAIMS}) == 6
    assert {claim.status for claim in TERRYOLOGY_CLAIMS} == {
        EvidenceStatus.SOURCE_REPORTED,
        EvidenceStatus.INCONSISTENT_WITH_STATED_AXIOMS,
        EvidenceStatus.CATEGORY_ERROR,
        EvidenceStatus.UNDERSPECIFIED,
        EvidenceStatus.UNTESTED_PHYSICAL,
    }
    physical = next(claim for claim in TERRYOLOGY_CLAIMS if claim.key.endswith("identifications"))
    assert physical.status is EvidenceStatus.UNTESTED_PHYSICAL


def test_ordinary_product_retains_all_audited_laws_and_identity():
    audit = audit_operation_on_samples(ordinary_product)

    assert not audit.failures
    assert audit.two_sided_identities == (1,)
    assert ordinary_product(1, 1) == 1


def test_literal_repeated_addition_is_an_off_by_one_operation():
    assert howard_literal_product(1, 1) == 2
    assert howard_literal_product(3, 4) == 15
    with pytest.raises(ValueError, match="nonnegative"):
        howard_literal_product(1, -1)


def test_literal_operation_has_exact_law_counterexamples():
    audit = audit_operation_on_samples(howard_literal_product)

    assert audit.failure("commutativity") is not None
    assert audit.failure("associativity") is not None
    assert audit.failure("left-distributivity-over-addition") is not None
    assert audit.failure("right-distributivity-over-addition") is None
    assert not audit.two_sided_identities
    assert howard_literal_product(howard_literal_product(1, 1), 1) == 4
    assert howard_literal_product(1, howard_literal_product(1, 1)) == 3


def test_changing_only_one_times_one_breaks_ring_laws():
    audit = audit_operation_on_samples(symmetric_one_one_patch)

    assert audit.failure("commutativity") is None
    assert audit.failure("associativity") is not None
    assert audit.failure("left-distributivity-over-addition") is not None
    assert audit.failure("right-distributivity-over-addition") is not None
    assert not audit.two_sided_identities
    assert symmetric_one_one_patch(symmetric_one_one_patch(1, 1), 2) == 4
    assert symmetric_one_one_patch(1, symmetric_one_one_patch(1, 2)) == 2


def test_counting_both_participants_is_consistent_addition_not_multiplication():
    audit = audit_operation_on_samples(participant_union_count)

    assert participant_union_count(1, 1) == 2
    assert audit.failure("commutativity") is None
    assert audit.failure("associativity") is None
    assert audit.failure("left-distributivity-over-addition") is not None
    assert audit.failure("right-distributivity-over-addition") is not None
    assert audit.two_sided_identities == (0,)
    with pytest.raises(ValueError, match="nonnegative"):
        participant_union_count(-1, 1)


def test_square_root_two_is_exact_in_its_quadratic_number_field():
    assert SQRT_TWO * SQRT_TWO == SqrtTwoNumber(2)
    assert SQRT_TWO**3 == 2 * SQRT_TWO
    assert SQRT_TWO**3 - 2 * SQRT_TWO == SqrtTwoNumber(0)
    assert SQRT_TWO**0 == SqrtTwoNumber(1)
    with pytest.raises(ValueError, match="nonnegative"):
        SQRT_TWO**-1


def test_a_finite_decimal_is_an_approximation_not_an_exact_square_root():
    residual = decimal_sqrt_two_square_residual("1.414213562373095")

    assert residual != 0
    assert abs(residual) < Fraction(1, 10**14)


def test_division_by_zero_fails_for_nonexistence_or_nonuniqueness():
    assert zero_product_solution_multiplicity(1) is SolutionMultiplicity.NONE
    assert zero_product_solution_multiplicity(-3) is SolutionMultiplicity.NONE
    assert zero_product_solution_multiplicity(0) is SolutionMultiplicity.NON_UNIQUE


def test_physical_dimension_changes_without_changing_the_coefficient():
    one_metre = DimensionalMonomial(1, 1)

    assert one_metre * one_metre == DimensionalMonomial(1, 2)


def test_source_counts_map_to_regular_vertex_orbits_without_relabeling():
    assert tuple(field.display_name for field in TERRYEN_WAVE_FIELDS) == (
        "Tetra-Terryen",
        "Huntyen",
        "Mira",
        "Aubreyen",
        "Heavenly",
    )
    assert tuple(field.bubble_count for field in TERRYEN_WAVE_FIELDS) == (4, 8, 6, 12, 24)
    assert tuple(field.candidate_polytope for field in TERRYEN_WAVE_FIELDS) == (
        "tetrahedron",
        "cube",
        "octahedron",
        "icosahedron",
        "24-cell",
    )
    assert all(field.status is EvidenceStatus.CANDIDATE_MAPPING for field in TERRYEN_WAVE_FIELDS)


@pytest.mark.parametrize("field", TERRYEN_WAVE_FIELDS, ids=lambda field: field.key)
def test_every_candidate_has_the_reported_count_and_dimension(field):
    vertices = terryen_candidate_vertices(field.key)

    assert len(vertices) == field.bubble_count
    assert {len(vertex) for vertex in vertices} == {field.candidate_dimension}
    assert len({sum(component * component for component in vertex) for vertex in vertices}) == 1


@pytest.mark.parametrize(
    ("key", "expected_cosine", "expected_angle"),
    (
        ("tetra_terryen", -1 / 3, 109.47122063449069),
        ("huntyen", 1 / 3, 70.52877936550931),
        ("mira", 0.0, 90.0),
        ("aubreyen", 1 / sqrt(5), 63.43494882292201),
        ("heavenly", 0.5, 60.0),
    ),
)
def test_candidate_directions_give_nonoverlapping_equal_sphere_shells(
    key,
    expected_cosine,
    expected_angle,
):
    certificate = terryen_spherical_code_certificate(key)

    assert isclose(certificate.maximum_pairwise_cosine, expected_cosine)
    assert isclose(certificate.minimum_angle_degrees, expected_angle)
    assert certificate.supports_equal_sphere_kissing


def test_twenty_four_requires_four_dimensions_under_equal_sphere_kissing_model():
    assert KNOWN_KISSING_NUMBERS == {1: 2, 2: 6, 3: 12, 4: 24}
    assert within_known_kissing_bound(12, 3)
    assert not within_known_kissing_bound(24, 3)
    assert within_known_kissing_bound(24, 4)
    with pytest.raises(ValueError, match="recorded exact"):
        within_known_kissing_bound(24, 5)
    with pytest.raises(ValueError, match="nonnegative"):
        within_known_kissing_bound(-1, 3)


def test_four_point_tetrahedron_plus_its_mirror_is_the_eight_point_cube():
    completion = tetrahedral_mirror_completion()

    assert set(TETRAHEDRON_VERTICES).isdisjoint(MIRROR_TETRAHEDRON_VERTICES)
    assert completion == CUBE_VERTICES
    assert len(completion) == 8


def test_huntyen_and_mira_candidates_are_exact_platonic_duals():
    assert DUAL_SOLID_NAMES[terryen_wave_field("huntyen").candidate_polytope] == (
        terryen_wave_field("mira").candidate_polytope
    )
    cube = solid_signature("cube")
    octahedron = solid_signature("octahedron")
    assert cube == (8, 12, 6)
    assert octahedron == (6, 12, 8)


def test_candidate_sequence_has_exact_inside_out_duality():
    tetrahedron = solid_signature("tetrahedron")
    icosahedron = solid_signature("icosahedron")
    dodecahedron = solid_signature("dodecahedron")

    assert tetrahedron == (4, 6, 4)
    assert icosahedron == (12, 30, 20)
    assert dodecahedron == (20, 30, 12)
    assert icosahedron == tuple(reversed(dodecahedron))
    assert (
        len(TWENTY_FOUR_CELL_VERTICES),
        len(twenty_four_cell_edges()),
        len(twenty_four_cell_triangular_faces()),
        len(twenty_four_cell_facets()),
    ) == (24, 96, 96, 24)


def test_heavenly_candidate_is_the_existing_tetrahedron_generated_24_cell():
    assert len(TWENTY_FOUR_CELL_VERTICES) == terryen_wave_field("heavenly").bubble_count
    assert set(twenty_four_cell_vertices_from_tetrahedron(1)) == set(TWENTY_FOUR_CELL_VERTICES)
    assert set(twenty_four_cell_vertices_from_tetrahedron(-1)) == set(TWENTY_FOUR_CELL_VERTICES)


def test_unknown_wave_field_is_rejected():
    with pytest.raises(ValueError, match="unknown Terryen"):
        terryen_wave_field("not-a-field")
