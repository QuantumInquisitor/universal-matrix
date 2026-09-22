import pytest

from src.localized_matter_variational import MatterPotential
from src.qball_branch_diagnostics import (
    branch_diagnostic_summary,
    branch_secants,
    energy_per_charge_threshold_crossings,
)
from src.radial_matter_continuation import continue_radial_branch


POTENTIAL = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


@pytest.fixture(scope="module")
def branch():
    return continue_radial_branch(
        [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )


def test_branch_secants_report_measured_charge_frequency_slope(branch):
    secants = branch_secants(branch)

    assert len(secants) == 5
    assert all(
        s.negative_charge_frequency_slope == (s.dcharge_domega < 0.0)
        for s in secants
    )
    assert all(s.dcharge_domega != 0.0 for s in secants)


def test_stationary_branch_secants_satisfy_dE_dQ_approximately_omega(branch):
    secants = branch_secants(branch)

    # The branch spacing in central amplitude is deliberately coarse, so this
    # checks the finite-secant relation rather than demanding differential
    # precision.
    assert max(s.variational_relative_error for s in secants) < 0.03
    assert all(s.denergy_dcharge > 0.0 for s in secants)


def test_energy_per_charge_crosses_free_mass_between_point_nine_and_one(branch):
    crossings = energy_per_charge_threshold_crossings(branch)

    assert len(crossings) == 1
    crossing = crossings[0]
    assert crossing.left_amplitude == pytest.approx(0.9)
    assert crossing.right_amplitude == pytest.approx(1.0)
    assert 0.9 < crossing.interpolated_amplitude < 1.0
    assert 0.8 < crossing.interpolated_omega < 0.87
    assert crossing.threshold == pytest.approx(1.0)


def test_branch_summary_records_both_variational_and_threshold_information(branch):
    summary = branch_diagnostic_summary(branch)

    assert summary["accepted_points"] == 6
    assert summary["secants"] == 5
    assert summary["omega_strictly_decreasing"] is True
    assert summary["all_negative_dq_domega"] == all(
        s.negative_charge_frequency_slope
        for s in branch_secants(branch)
    )
    assert summary["maximum_variational_relative_error"] < 0.03
    assert summary["energy_per_charge_crossings"] == 1
    assert summary["minimum_energy_per_charge"] < 1.0
    assert summary["maximum_energy_per_charge"] > 1.0
