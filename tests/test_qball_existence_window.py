import math

import pytest

from src.localized_matter_variational import MatterPotential
from src.qball_existence_window import (
    asymptotic_decay_rate,
    effective_radial_density,
    potential_ratio,
    qball_existence_window,
)


DEFAULT = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


def test_default_ratio_factor_has_zero_minimum_at_density_one():
    window = qball_existence_window(DEFAULT)

    assert window.minimizing_density == pytest.approx(1.0)
    assert window.minimum_ratio == pytest.approx(0.0)
    assert potential_ratio(1.0, DEFAULT) == pytest.approx(0.0)


def test_default_qball_window_is_zero_to_free_mass_squared():
    window = qball_existence_window(DEFAULT)

    assert window.has_open_window
    assert window.omega_squared_lower == pytest.approx(0.0)
    assert window.omega_squared_upper == pytest.approx(1.0)
    assert window.omega_lower == pytest.approx(0.0)
    assert window.omega_upper == pytest.approx(1.0)


def test_default_window_accepts_submass_frequency_only():
    window = qball_existence_window(DEFAULT)

    assert window.allows_omega(0.8)
    assert window.allows_omega(0.99)
    assert not window.allows_omega(1.0)
    assert not window.allows_omega(1.1)
    assert not window.allows_omega(0.0)


def test_positive_quartic_potential_has_no_open_qball_window():
    potential = MatterPotential(
        mass2=1.0,
        lambda4=0.5,
        lambda6=0.0,
    )
    window = qball_existence_window(potential)

    assert not window.has_open_window
    assert window.minimizing_density is None
    assert window.minimum_ratio == pytest.approx(1.0)


def test_nonzero_lower_bound_is_computed_analytically():
    potential = MatterPotential(
        mass2=1.0,
        lambda4=-1.0,
        lambda6=1.0,
    )
    window = qball_existence_window(potential)

    assert window.minimizing_density == pytest.approx(0.5)
    assert window.minimum_ratio == pytest.approx(0.75)
    assert window.omega_squared_lower == pytest.approx(0.75)
    assert window.omega_squared_upper == pytest.approx(1.0)
    assert window.allows_omega(0.95)
    assert not window.allows_omega(0.8)


def test_asymptotic_decay_rate_matches_linear_tail():
    rate = asymptotic_decay_rate(0.8, DEFAULT)
    assert rate == pytest.approx(math.sqrt(1.0 - 0.8**2))


def test_effective_radial_density_is_negative_inside_default_window():
    # At rho=1, U=0. For any allowed omega>0, U_eff=-omega^2*rho<0.
    assert effective_radial_density(1.0, 0.8, DEFAULT) == pytest.approx(-0.64)


def test_decay_rate_rejects_frequency_at_or_above_free_mass():
    with pytest.raises(ValueError):
        asymptotic_decay_rate(1.0, DEFAULT)
