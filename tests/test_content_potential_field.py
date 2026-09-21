import math
import numpy as np

from src.content_potential_field import (
    PointContentSource,
    field_energy_density,
    point_source_gradient_3d,
    point_source_potential_3d,
    potential_clock_rate_ratio,
    solve_content_potential,
)


def test_point_potential_has_inverse_radius_scaling():
    q = 3.0
    k = 0.7
    p1 = point_source_potential_3d(2.0, q, k)
    p2 = point_source_potential_3d(4.0, q, k)
    assert math.isclose(p1 / p2, 2.0, rel_tol=0, abs_tol=1e-14)


def test_point_gradient_has_inverse_square_magnitude():
    q = 2.0
    k = 0.4
    g1 = point_source_gradient_3d([2.0, 0.0, 0.0], q, k)
    g2 = point_source_gradient_3d([4.0, 0.0, 0.0], q, k)
    ratio = np.linalg.norm(g1) / np.linalg.norm(g2)
    assert math.isclose(ratio, 4.0, rel_tol=0, abs_tol=1e-13)


def test_positive_source_gradient_points_toward_source():
    position = np.array([2.0, -1.0, 0.5])
    gradient = point_source_gradient_3d(
        position,
        source_strength=1.0,
        coupling=0.8,
    )
    assert float(np.dot(gradient, position)) < 0


def test_gradient_energy_density_is_nonnegative():
    value = field_energy_density([1.0, -2.0, 0.5], coupling=0.3)
    assert value > 0


def test_higher_positive_potential_slows_clock_for_positive_clock_coupling():
    near = potential_clock_rate_ratio(
        potential=2.0,
        clock_coupling=0.2,
    )
    far = potential_clock_rate_ratio(
        potential=0.5,
        clock_coupling=0.2,
    )
    assert near < far


def test_finite_open_solver_accepts_nonzero_content_source():
    rho = np.zeros((5, 5, 5))
    rho[2, 2, 2] = 1.0
    solution = solve_content_potential(
        rho,
        coupling=0.6,
        tolerance=1e-11,
    )
    assert solution.max_abs_gauss_residual(0.6 * rho) < 1e-9


def test_point_source_object_matches_functions():
    source = PointContentSource(source_strength=2.5, field_coupling=0.4)
    assert source.potential(3.0) == point_source_potential_3d(3.0, 2.5, 0.4)
    assert np.allclose(
        source.gradient([3.0, 0.0, 0.0]),
        point_source_gradient_3d([3.0, 0.0, 0.0], 2.5, 0.4),
    )
