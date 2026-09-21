import math
import numpy as np

from src.source_interaction import (
    Source,
    charge_density,
    discrete_radial_force,
    interaction_energy_cross_term,
    pair_energy,
    solve_sources,
)


def test_poisson_solution_satisfies_gauss_constraint():
    solution = solve_sources(
        (8, 8, 8),
        [Source((0, 0, 0), 1.0), Source((2, 1, 0), -1.0)],
    )
    assert solution.max_abs_gauss_residual() < 1e-11


def test_zero_mode_neutralization_is_exact():
    rho = charge_density((6, 6, 6), [Source((0, 0, 0), 1.0)])
    assert abs(float(np.sum(rho))) < 1e-12


def test_opposite_sources_have_lower_energy_when_closer():
    shape = (16, 16, 16)
    u1 = pair_energy(shape, 1, 1.0, -1.0)
    u2 = pair_energy(shape, 2, 1.0, -1.0)
    u3 = pair_energy(shape, 3, 1.0, -1.0)
    assert u1 < u2 < u3


def test_like_sources_have_higher_energy_when_closer():
    shape = (16, 16, 16)
    u1 = pair_energy(shape, 1, 1.0, 1.0)
    u2 = pair_energy(shape, 2, 1.0, 1.0)
    u3 = pair_energy(shape, 3, 1.0, 1.0)
    assert u1 > u2 > u3


def test_force_proxy_changes_sign_with_relative_source_sign():
    shape = (16, 16, 16)
    f_opposite = discrete_radial_force(shape, 3, 1.0, -1.0)
    f_like = discrete_radial_force(shape, 3, 1.0, 1.0)

    # Positive means increasing separation is energetically disfavored, i.e.
    # attraction toward smaller r under this radial sign convention.
    assert f_opposite < 0.0
    assert f_like > 0.0


def test_cross_term_sign_matches_source_product():
    shape = (12, 12, 12)
    a = Source((0, 0, 0), 1.0)
    b_opp = Source((2, 0, 0), -1.0)
    b_like = Source((2, 0, 0), 1.0)

    u_opp = interaction_energy_cross_term(shape, a, b_opp)
    u_like = interaction_energy_cross_term(shape, a, b_like)

    assert u_opp < 0.0
    assert u_like > 0.0
    assert math.isclose(abs(u_opp), abs(u_like), rel_tol=0, abs_tol=1e-12)
