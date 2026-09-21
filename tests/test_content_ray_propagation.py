import math
import numpy as np

from src.content_ray_propagation import (
    RayState,
    content_index,
    ray_direction_derivative,
    trace_ray,
)


def test_uniform_content_produces_straight_ray():
    content = lambda x: 2.0
    gradient = lambda x: np.zeros_like(x)

    ray = RayState(
        position=np.array([0.0, 0.0]),
        direction=np.array([1.0, 0.0]),
    )
    states = trace_ray(
        ray,
        steps=100,
        ds=0.01,
        content_fn=content,
        gradient_fn=gradient,
        coupling=0.3,
    )

    final = states[-1]
    assert np.allclose(final.direction, [1.0, 0.0], atol=1e-12, rtol=0)
    assert abs(final.position[1]) < 1e-12


def test_transverse_positive_content_gradient_bends_toward_gradient():
    base = 2.0
    slope = 0.1

    def content(x):
        return base + slope * x[1]

    def gradient(x):
        return np.array([0.0, slope])

    ray = RayState(
        position=np.array([0.0, 0.0]),
        direction=np.array([1.0, 0.0]),
    )
    states = trace_ray(
        ray,
        steps=200,
        ds=0.01,
        content_fn=content,
        gradient_fn=gradient,
        coupling=0.5,
    )

    final = states[-1]
    assert final.direction[1] > 0
    assert final.position[1] > 0


def test_longitudinal_gradient_does_not_instantly_bend_ray():
    derivative = ray_direction_derivative(
        direction=[1.0, 0.0, 0.0],
        content_gradient=[2.0, 0.0, 0.0],
        coupling=0.4,
    )
    assert np.allclose(derivative, 0.0, atol=1e-15, rtol=0)


def test_direction_derivative_is_transverse():
    direction = np.array([1.0, 2.0, -1.0])
    gradient = np.array([0.3, -0.2, 0.7])
    derivative = ray_direction_derivative(direction, gradient, coupling=0.8)
    unit = direction / np.linalg.norm(direction)
    assert abs(float(np.dot(unit, derivative))) < 1e-14


def test_index_composition_matches_content_clock_lapse():
    g = 0.2
    x = 0.7
    y = 0.4
    lhs = content_index(x + y, g)
    rhs = content_index(x, g) * content_index(y, g)
    assert math.isclose(lhs, rhs, rel_tol=0, abs_tol=1e-14)


def test_constant_index_accumulates_expected_travel_time_integral():
    n = content_index(2.0, coupling=0.3)
    content = lambda x: 2.0
    gradient = lambda x: np.zeros_like(x)

    states = trace_ray(
        RayState(np.array([0.0, 0.0]), np.array([1.0, 0.0])),
        steps=50,
        ds=0.02,
        content_fn=content,
        gradient_fn=gradient,
        coupling=0.3,
    )
    final = states[-1]
    assert math.isclose(final.path_length, 1.0, abs_tol=1e-14)
    assert math.isclose(
        final.travel_time_index_integral,
        n,
        rel_tol=0,
        abs_tol=1e-12,
    )
