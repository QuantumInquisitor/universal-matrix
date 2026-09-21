import math
import numpy as np

from src.localized_matter_variational import MatterPotential
from src.radial_matter_solver import solve_radial_matter


POTENTIAL = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


def test_radial_solver_converges_for_representative_profile():
    solution = solve_radial_matter(
        central_amplitude=0.5,
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )

    assert solution.solver_status == 0
    assert 0.0 < solution.omega < POTENTIAL.free_mass
    assert solution.nodeless
    assert abs(solution.profile[-1]) < 1e-8
    assert abs(solution.derivative[0]) < 1e-4


def test_nonlinear_solution_has_finite_positive_energy_and_charge():
    solution = solve_radial_matter(
        central_amplitude=0.5,
        potential=POTENTIAL,
        omega_guess=0.955,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )
    assert solution.solver_status == 0
    assert solution.energy > 0
    assert solution.charge > 0
    assert math.isfinite(solution.energy_per_charge)


def test_representative_nonlinear_branch_is_not_automatically_stable():
    solution = solve_radial_matter(
        central_amplitude=0.5,
        potential=POTENTIAL,
        omega_guess=0.95,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )

    # This is intentionally a negative result: a localized field-equation
    # solution can still sit above the free-particle E/Q threshold.
    assert solution.energy_per_charge > POTENTIAL.free_mass
    assert not solution.below_free_mass_threshold


def test_profile_decays_outward_on_representative_branch():
    solution = solve_radial_matter(
        central_amplitude=0.5,
        potential=POTENTIAL,
        omega_guess=0.955,
        radius_max=20.0,
        radial_points=300,
        tolerance=2e-5,
    )
    sample = np.abs(solution.profile)
    assert sample[-1] < sample[0] * 1e-6
