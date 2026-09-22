import math

import pytest

from src.canonical_kernel import N_CORE, polarity
from src.matrix_ontology import (
    PAIR_COUNT,
    CandidateCellState,
    CanonicalCoreAddress,
    GATE_VECTORS,
    OntologyStatus,
    PolarityBranch,
    RepeatedMatrixCellComplex,
    ontology_ledger,
)


def test_exact_pair_polarity_decomposition_is_bijective():
    recovered = set()

    for n in range(N_CORE):
        address = CanonicalCoreAddress.from_n(n)
        assert address.n == n
        recovered.add((address.pair_id, address.polarity_bit))

    assert len(recovered) == N_CORE
    assert PAIR_COUNT == 54
    assert recovered == {
        (pair_id, polarity_bit)
        for pair_id in range(54)
        for polarity_bit in (0, 1)
    }


def test_canonical_polarity_toggles_only_branch():
    for n in range(N_CORE):
        address = CanonicalCoreAddress.from_n(n)
        flipped = address.flipped()

        assert flipped.pair_id == address.pair_id
        assert flipped.polarity_bit == 1 - address.polarity_bit
        assert flipped.n == polarity(n)
        assert address.canonical_polarity_matches()
        assert flipped.flipped() == address


def test_lower_and_upper_addresses_reconstruct_exactly():
    for pair_id in range(54):
        lower = CanonicalCoreAddress(
            pair_id,
            PolarityBranch.LOWER,
        )
        upper = CanonicalCoreAddress(
            pair_id,
            PolarityBranch.UPPER,
        )

        assert lower.n == pair_id
        assert upper.n == pair_id + 54


def test_invalid_pair_ids_are_rejected():
    for pair_id in (-1, 54, 100):
        with pytest.raises(ValueError):
            CanonicalCoreAddress(pair_id)


def test_ontology_ledger_has_unique_names_and_explicit_statuses():
    ledger = ontology_ledger()
    names = [entry.name for entry in ledger]

    assert len(names) == len(set(names))

    by_name = {entry.name: entry for entry in ledger}
    assert by_name["core_pair_id"].status is OntologyStatus.EXACT_CANONICAL
    assert by_name["polarity_bit"].status is OntologyStatus.EXACT_CANONICAL
    assert by_name["gauge_link"].status is OntologyStatus.EDGE_DEGREE_CANDIDATE
    assert by_name["particle_species"].status is OntologyStatus.DERIVED_CANDIDATE
    assert by_name["absolute_length_scale"].status is OntologyStatus.OPEN


def test_candidate_cell_state_does_not_add_dimensional_units():
    state = CandidateCellState(
        address=CanonicalCoreAddress.from_n(17),
        scale_level=3,
        phase=math.pi / 4,
        phase_momentum=-0.25,
    )

    assert state.address.n == 17
    assert state.scale_level == 3

    with pytest.raises(ValueError):
        CandidateCellState(
            address=state.address,
            scale_level=-1,
        )


def test_six_gate_vectors_are_three_opposite_pairs():
    assert set(GATE_VECTORS) == {
        "X_POS",
        "X_NEG",
        "Y_POS",
        "Y_NEG",
        "Z_POS",
        "Z_NEG",
    }

    assert GATE_VECTORS["X_POS"] == tuple(-x for x in GATE_VECTORS["X_NEG"])
    assert GATE_VECTORS["Y_POS"] == tuple(-x for x in GATE_VECTORS["Y_NEG"])
    assert GATE_VECTORS["Z_POS"] == tuple(-x for x in GATE_VECTORS["Z_NEG"])


def test_open_repeated_cell_complex_has_correct_neighbors():
    complex_ = RepeatedMatrixCellComplex((3, 2, 2), boundary_mode="open")

    assert complex_.site_count == 12
    assert complex_.neighbor((1, 1, 1), "X_POS") == (2, 1, 1)
    assert complex_.neighbor((0, 0, 0), "X_NEG") is None
    assert complex_.neighbor((0, 0, 0), "Y_NEG") is None
    assert complex_.neighbor((0, 0, 0), "Z_NEG") is None

    expected_oriented_links = 2 * (
        (3 - 1) * 2 * 2
        + 3 * (2 - 1) * 2
        + 3 * 2 * (2 - 1)
    )
    assert len(tuple(complex_.oriented_links())) == expected_oriented_links


def test_periodic_repeated_cell_complex_wraps_six_gates():
    complex_ = RepeatedMatrixCellComplex((3, 4, 5), boundary_mode="periodic")

    assert complex_.neighbor((0, 0, 0), "X_NEG") == (2, 0, 0)
    assert complex_.neighbor((0, 0, 0), "Y_NEG") == (0, 3, 0)
    assert complex_.neighbor((0, 0, 0), "Z_NEG") == (0, 0, 4)
    assert complex_.neighbor((2, 3, 4), "X_POS") == (0, 3, 4)
    assert len(tuple(complex_.oriented_links())) == 6 * complex_.site_count


def test_repeated_complex_has_no_physical_lattice_spacing_parameter():
    fields = set(RepeatedMatrixCellComplex.__dataclass_fields__)
    assert fields == {"shape", "boundary_mode"}
