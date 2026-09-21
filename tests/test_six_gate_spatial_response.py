import numpy as np

from src.six_gate_spatial_response import (
    SIGNED_PERMUTATIONS,
    isotropic_projection,
    linearized_metric_response,
    preserves_b6_symmetry,
    spatial_scale_factor,
    symmetry_average,
)


def test_signed_permutation_group_has_48_elements():
    assert len(SIGNED_PERMUTATIONS) == 48


def test_isotropic_tensor_commutes_with_full_six_gate_symmetry():
    response = 2.7 * np.eye(3)
    assert preserves_b6_symmetry(response)


def test_generic_anisotropic_tensor_breaks_full_symmetry():
    response = np.diag([1.0, 2.0, 3.0])
    assert not preserves_b6_symmetry(response)


def test_group_average_projects_to_scalar_identity():
    response = np.array(
        [
            [1.0, 2.0, -0.5],
            [0.3, 4.0, 1.2],
            [2.1, -0.7, 7.0],
        ]
    )
    averaged = symmetry_average(response)
    expected = isotropic_projection(response)
    assert np.allclose(averaged, expected, atol=1e-14, rtol=0)


def test_linearized_metric_response_is_b6_invariant():
    response = linearized_metric_response(psi=0.03, gamma_matrix=0.8)
    assert preserves_b6_symmetry(response)


def test_spatial_scale_composes_multiplicatively():
    gamma = 0.9
    p1 = 0.2
    p2 = -0.05
    lhs = spatial_scale_factor(p1 + p2, gamma)
    rhs = spatial_scale_factor(p1, gamma) * spatial_scale_factor(p2, gamma)
    assert np.isclose(lhs, rhs, atol=1e-15, rtol=0)
