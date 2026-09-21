import math
import numpy as np

from src.reciprocity_backreaction_audit import (
    metric_determinant,
    metric_diagonal,
    spatial_flux_prefactor,
    sqrt_minus_g,
    static_covariant_box_from_flat_laplacian,
)


def test_metric_determinant_matches_diagonal_product():
    psi = 0.37
    c = 2.4
    diag = metric_diagonal(psi, c)
    assert math.isclose(
        float(np.prod(diag)),
        metric_determinant(psi, c),
        rel_tol=0,
        abs_tol=1e-14,
    )


def test_sqrt_minus_g_matches_determinant():
    psi = -0.2
    c = 1.7
    assert math.isclose(
        sqrt_minus_g(psi, c),
        math.sqrt(-metric_determinant(psi, c)),
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_spatial_flux_prefactor_is_independent_of_psi():
    c = 3.1
    values = [spatial_flux_prefactor(psi, c) for psi in (-1.0, 0.0, 0.5, 2.0)]
    assert np.allclose(values, c, atol=1e-14, rtol=0)


def test_static_vacuum_harmonic_field_remains_covariantly_harmonic():
    for psi in (-0.4, 0.0, 0.8):
        assert static_covariant_box_from_flat_laplacian(psi, 0.0) == 0.0


def test_nonzero_flat_laplacian_gets_positive_exponential_prefactor():
    value = static_covariant_box_from_flat_laplacian(
        psi_background=0.3,
        flat_laplacian_value=-2.0,
    )
    assert value < 0
    assert math.isclose(value, -2.0 * math.exp(-0.6), abs_tol=1e-15)
