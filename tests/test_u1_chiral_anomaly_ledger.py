import numpy as np

from src.u1_chiral_anomaly_ledger import (
    WeylSpecies,
    anomaly_ledger,
    cubic_u1_anomaly_coefficient,
    direct_overlap_index,
    index_sum_residual,
    local_index_gauge_residual,
    local_overlap_index_density,
    mixed_gravitational_u1_coefficient,
    total_covariant_local_anomaly_candidate,
)
from src.u1_overlap_dirac_lattice import zero_links


def test_local_index_density_sums_to_direct_overlap_index():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2501)
    links = rng.normal(
        scale=0.02,
        size=(4,) + shape,
    )

    residual = index_sum_residual(
        links,
        charge=1.0,
        rho=1.0,
    )
    assert abs(residual) < 1e-9


def test_free_trivial_background_has_zero_index_for_integer_charges():
    links = zero_links((2, 2, 1, 1))
    for charge in (-2.0, -1.0, 1.0, 2.0):
        index = direct_overlap_index(
            links,
            charge=charge,
            rho=1.0,
        )
        assert abs(index) < 1e-10


def test_local_overlap_index_density_is_gauge_invariant():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2502)
    links = rng.normal(
        scale=0.02,
        size=(4,) + shape,
    )
    alpha = rng.normal(
        scale=0.15,
        size=shape,
    )

    residual = local_index_gauge_residual(
        links,
        alpha,
        charge=2.0,
        rho=1.0,
    )
    assert np.max(np.abs(residual)) < 1e-8


def test_local_density_is_real_and_finite():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2503)
    links = rng.normal(
        scale=0.015,
        size=(4,) + shape,
    )

    density = local_overlap_index_density(
        links,
        charge=1.0,
        rho=1.0,
    )
    assert np.all(np.isfinite(density))
    assert density.shape == shape


def test_vectorlike_pair_cancels_u1_anomaly_coefficients():
    species = [
        WeylSpecies(charge=1.0, handedness=1),
        WeylSpecies(charge=1.0, handedness=-1),
    ]

    assert abs(
        cubic_u1_anomaly_coefficient(species)
    ) < 1e-15
    assert abs(
        mixed_gravitational_u1_coefficient(species)
    ) < 1e-15

    ledger = anomaly_ledger(species)
    assert ledger["u1_cubic_cancels"]
    assert ledger["mixed_gravitational_u1_cancels"]
    assert ledger["perturbative_abelian_conditions_cancel"]


def test_single_chiral_charge_is_anomalous_in_representation_ledger():
    species = [
        WeylSpecies(charge=1.0, handedness=1),
    ]
    ledger = anomaly_ledger(species)

    assert ledger["u1_cubic"] == 1.0
    assert ledger["mixed_gravitational_u1"] == 1.0
    assert not ledger["perturbative_abelian_conditions_cancel"]


def test_nontrivial_anomaly_free_charge_set():
    # Left-handed charges {-3,-4,5} have zero linear sum but nonzero cubic sum,
    # so this deliberately verifies that the two cancellation conditions are
    # independent rather than collapsed into one check.
    species = [
        WeylSpecies(charge=-3.0, handedness=1),
        WeylSpecies(charge=-4.0, handedness=1),
        WeylSpecies(charge=5.0, handedness=1),
        WeylSpecies(charge=2.0, handedness=1),
    ]
    ledger = anomaly_ledger(species)

    assert ledger["mixed_gravitational_u1"] == 0.0
    assert ledger["u1_cubic"] != 0.0
    assert not ledger["perturbative_abelian_conditions_cancel"]


def test_total_covariant_candidate_vanishes_for_vectorlike_pair():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2504)
    links = rng.normal(
        scale=0.015,
        size=(4,) + shape,
    )

    species = [
        WeylSpecies(charge=1.0, handedness=1),
        WeylSpecies(charge=1.0, handedness=-1),
    ]

    total = total_covariant_local_anomaly_candidate(
        links,
        species,
        rho=1.0,
    )
    assert np.max(np.abs(total)) < 1e-12
