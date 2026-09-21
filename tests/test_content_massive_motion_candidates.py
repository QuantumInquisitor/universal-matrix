import numpy as np

from src.content_massive_motion_candidates import (
    acceleration_from_content_gradient,
    massive_force,
    specific_potential,
)


def test_toward_higher_content_branch_points_with_gradient():
    gradient = np.array([1.0, -2.0, 0.5])
    acceleration = acceleration_from_content_gradient(
        gradient,
        coupling=0.2,
        speed_scale=3.0,
        branch="toward_higher_content",
    )
    assert np.dot(acceleration, gradient) > 0


def test_toward_lower_content_branch_points_against_gradient():
    gradient = np.array([1.0, -2.0, 0.5])
    acceleration = acceleration_from_content_gradient(
        gradient,
        coupling=0.2,
        speed_scale=3.0,
        branch="toward_lower_content",
    )
    assert np.dot(acceleration, gradient) < 0


def test_two_branches_are_exact_opposites():
    gradient = [0.4, 0.2, -0.7]
    high = acceleration_from_content_gradient(
        gradient, 0.3, 2.0, "toward_higher_content"
    )
    low = acceleration_from_content_gradient(
        gradient, 0.3, 2.0, "toward_lower_content"
    )
    assert np.allclose(high, -low, atol=0, rtol=0)


def test_acceleration_is_independent_of_test_mass():
    gradient = [0.1, 0.0, -0.2]
    a = acceleration_from_content_gradient(
        gradient,
        coupling=0.4,
        speed_scale=5.0,
        branch="toward_higher_content",
    )
    force_1 = massive_force(
        1.5,
        gradient,
        coupling=0.4,
        speed_scale=5.0,
        branch="toward_higher_content",
    )
    force_2 = massive_force(
        7.0,
        gradient,
        coupling=0.4,
        speed_scale=5.0,
        branch="toward_higher_content",
    )

    assert np.allclose(force_1 / 1.5, a)
    assert np.allclose(force_2 / 7.0, a)


def test_branch_potentials_have_opposite_sign():
    high = specific_potential(
        2.0, 0.2, 3.0, "toward_higher_content", reference_content=1.0
    )
    low = specific_potential(
        2.0, 0.2, 3.0, "toward_lower_content", reference_content=1.0
    )
    assert high == -low
