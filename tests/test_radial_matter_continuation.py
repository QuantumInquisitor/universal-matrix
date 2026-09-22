import pytest

from src.localized_matter_variational import MatterPotential
from src.radial_matter_continuation import (
    accepted_records,
    below_threshold_records,
    classify_continuation_solution,
    continue_radial_branch,
    solve_radial_matter_seeded,
)
from src.radial_matter_solver import solve_radial_matter


POTENTIAL = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


def test_seeded_neighbor_solve_stays_on_converged_nodeless_branch():
    seed = solve_radial_matter(
        central_amplitude=0.5,
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )
    neighbor = solve_radial_matter_seeded(
        0.6,
        seed,
        potential=POTENTIAL,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )
    record = classify_continuation_solution(0.6, neighbor)

    assert record.converged
    assert record.nodeless
    assert record.in_frequency_window
    assert record.accepted_as_seed
    assert 0.0 < neighbor.omega < 1.0


def test_continuation_tracks_default_branch_to_amplitude_one():
    amplitudes = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    records = continue_radial_branch(
        amplitudes,
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )

    assert len(records) == len(amplitudes)
    assert len(accepted_records(records)) == len(amplitudes)
    assert [r.central_amplitude for r in records] == pytest.approx(amplitudes)

    omegas = [r.omega for r in records]
    assert all(0.0 < omega < 1.0 for omega in omegas)
    assert all(
        later < earlier
        for earlier, later in zip(omegas, omegas[1:], strict=True)
    )


def test_continued_branch_reaches_below_free_mass_energy_per_charge():
    records = continue_radial_branch(
        [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )
    stable = below_threshold_records(records)

    assert stable
    final = records[-1]
    assert final.central_amplitude == pytest.approx(1.0)
    assert final.energy_per_charge < POTENTIAL.free_mass
    assert final.omega == pytest.approx(0.80015, rel=5e-4)


def test_every_accepted_point_has_small_relative_virial_residual():
    records = continue_radial_branch(
        [0.5, 0.7, 0.9, 1.0],
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )

    assert all(r.relative_virial_residual < 1e-3 for r in accepted_records(records))
