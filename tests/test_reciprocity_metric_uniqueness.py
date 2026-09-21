import math
import numpy as np

from src.reciprocity_metric_uniqueness import (
    b6_invariant_metric,
    composition_residual,
    gamma_from_local_causal_invariance,
    isotropic_under_signed_permutations,
    local_causal_speed_ratio,
    reciprocity_metric_diagonal,
    reciprocity_spatial_scale,
)


def test_b6_invariant_metric_is_invariant_under_all_signed_permutations():
    h = b6_invariant_metric(1.7)
    assert isotropic_under_signed_permutations(h)


def test_anisotropic_metric_breaks_full_b6_symmetry():
    h = np.diag([1.0, 1.0, 2.0])
    assert not isotropic_under_signed_permutations(h)


def test_exponential_spatial_response_obeys_additive_composition():
    for gamma in (-0.5, 0.0, 0.8, 1.0, 2.0):
        assert math.isclose(
            composition_residual(0.2, -0.07, gamma),
            0.0,
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_local_causal_invariance_selects_gamma_one():
    gamma = gamma_from_local_causal_invariance()
    assert gamma == 1.0

    for psi in (-1.0, -0.3, 0.2, 0.9):
        assert math.isclose(
            local_causal_speed_ratio(psi, gamma),
            1.0,
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_nonunit_gamma_fails_local_causal_invariance_for_nonzero_psi():
    assert not math.isclose(
        local_causal_speed_ratio(0.4, 0.9),
        1.0,
        rel_tol=0,
        abs_tol=1e-12,
    )


def test_reciprocity_metric_uses_inverse_clock_and_space_exponents():
    psi = 0.3
    c = 2.0
    g = reciprocity_metric_diagonal(psi, c)
    assert math.isclose(
        g[0],
        -c*c*math.exp(-2*psi),
        rel_tol=0,
        abs_tol=1e-15,
    )
    assert np.allclose(
        g[1:],
        reciprocity_spatial_scale(psi)**2,
        atol=1e-15,
        rtol=0,
    )
