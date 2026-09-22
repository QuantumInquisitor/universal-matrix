import pytest

from src.charged_matter_persistence import (
    default_continued_candidate,
    evolve_candidate,
    localized_amplitude_perturbation,
    map_candidate_to_3d,
    mapping_consistency,
    passes_survival_window,
)


@pytest.fixture(scope="module")
def candidate():
    return default_continued_candidate()


@pytest.fixture(scope="module")
def mapped_state(candidate):
    return map_candidate_to_3d(
        candidate,
        shape=(25, 25, 25),
        spacing=0.5,
    )


def test_spacing_consistent_mapping_preserves_energy_per_charge(candidate, mapped_state):
    consistency = mapping_consistency(candidate, mapped_state)

    assert candidate.energy_per_charge < 1.0
    assert consistency.cartesian_energy_per_charge < 1.0
    assert consistency.relative_difference < 0.02


def test_unperturbed_continued_candidate_survives_direct_3d_window(candidate):
    state = map_candidate_to_3d(
        candidate,
        shape=(25, 25, 25),
        spacing=0.5,
    )
    report = evolve_candidate(
        state,
        steps=1000,
        dt=0.001,
    )

    assert passes_survival_window(report)
    assert abs(report.relative_energy_drift) < 1e-6
    assert abs(report.relative_charge_drift) < 1e-10


def test_small_localized_amplitude_perturbation_survives_same_window(candidate):
    base = map_candidate_to_3d(
        candidate,
        shape=(25, 25, 25),
        spacing=0.5,
    )
    perturbed = localized_amplitude_perturbation(
        base,
        fractional_amplitude=0.005,
        width=1.0,
    )
    report = evolve_candidate(
        perturbed,
        steps=1000,
        dt=0.001,
    )

    assert passes_survival_window(report)
    assert abs(report.relative_energy_drift) < 1e-6
    assert abs(report.relative_charge_drift) < 1e-10


def test_perturbation_changes_initial_state_without_changing_grid(candidate):
    base = map_candidate_to_3d(
        candidate,
        shape=(17, 17, 17),
        spacing=0.5,
    )
    perturbed = localized_amplitude_perturbation(
        base,
        fractional_amplitude=0.005,
        width=1.0,
    )

    assert perturbed.lattice_spacing == pytest.approx(base.lattice_spacing)
    assert perturbed.phi.shape == base.phi.shape
    assert perturbed.energy != pytest.approx(base.energy)
    assert perturbed.charge != pytest.approx(base.charge)
