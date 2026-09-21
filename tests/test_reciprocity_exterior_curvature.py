import math

from src.reciprocity_exterior_curvature import (
    einstein_tensor_coordinate_diagonal,
    is_ricci_flat,
    kretschmann_scalar,
    leading_large_radius_kretschmann,
    ricci_scalar,
    ricci_tensor_square,
)


def test_exterior_is_not_ricci_flat_for_positive_mu_and_finite_radius():
    assert not is_ricci_flat(radius=10.0, mu=1.0)
    assert ricci_scalar(10.0, 1.0) < 0.0


def test_zero_mu_is_flat():
    assert is_ricci_flat(radius=1.0, mu=0.0)
    assert kretschmann_scalar(1.0, 0.0) == 0.0
    assert ricci_tensor_square(1.0, 0.0) == 0.0


def test_kretschmann_is_positive():
    for radius in (0.2, 0.5, 1.0, 3.0, 10.0):
        assert kretschmann_scalar(radius, 1.0) > 0.0


def test_large_radius_kretschmann_approaches_48_mu2_over_r6():
    mu = 1.0
    radius = 1e7
    exact = kretschmann_scalar(radius, mu)
    leading = leading_large_radius_kretschmann(radius, mu)
    assert abs(exact/leading - 1.0) < 1e-6


def test_curvature_invariants_tend_toward_zero_at_small_radius():
    mu = 1.0
    r1 = 0.05
    r2 = 0.02
    assert abs(ricci_scalar(r2, mu)) < abs(ricci_scalar(r1, mu))
    assert kretschmann_scalar(r2, mu) < kretschmann_scalar(r1, mu)


def test_einstein_tensor_is_nonzero_in_scalar_vacuum_exterior():
    diagonal = einstein_tensor_coordinate_diagonal(
        radius=2.0,
        mu=1.0,
        theta=math.pi/2,
    )
    assert any(abs(component) > 0 for component in diagonal)
