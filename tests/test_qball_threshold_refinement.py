import pytest

from src.qball_threshold_refinement import (
    local_slope_diagnostics,
    refine_energy_per_charge_threshold,
    threshold_bracket,
)


@pytest.fixture(scope="module")
def refined():
    return refine_energy_per_charge_threshold(
        refinement_rounds=2,
        interior_points_per_round=4,
        radial_points=260,
        tolerance=3e-5,
    )


def test_refinement_reduces_crossing_bracket(refined):
    # Coarse branch brackets the crossing between 0.9 and 1.0.
    assert refined.bracket_width < 0.1
    assert refined.bracket_width <= 0.004000000001
    assert 0.9 < refined.crossing.interpolated_amplitude < 1.0


def test_refined_crossing_remains_inside_analytic_branch(refined):
    assert 0.0 < refined.crossing.interpolated_omega < 1.0
    assert refined.crossing.threshold == pytest.approx(1.0)
    assert refined.accepted_points >= 14


def test_bracket_endpoints_straddle_energy_threshold(refined):
    left, right = threshold_bracket(refined.records)
    gl = left.solution.energy_per_charge - refined.crossing.threshold
    gr = right.solution.energy_per_charge - refined.crossing.threshold

    assert gl * gr <= 0.0


def test_local_branch_slope_is_reported_without_promoting_it_to_proof(refined):
    diagnostics = local_slope_diagnostics(refined)

    assert diagnostics["dcharge_domega"] != 0.0
    assert diagnostics["denergy_dcharge"] > 0.0
    assert diagnostics["variational_relative_error"] < 0.03
    assert isinstance(diagnostics["negative_charge_frequency_slope"], bool)
