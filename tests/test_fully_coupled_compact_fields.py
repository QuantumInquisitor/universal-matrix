import math
import numpy as np

from src.fully_coupled_classical_fields import FullyCoupledParameters
from src.fully_coupled_compact_fields import (
    FullyCoupledCompactFields,
    compact_gauge_energy,
    compact_gauge_force,
    principal_angle,
)
from src.localized_matter_variational import MatterPotential


def test_compact_gauge_force_matches_finite_difference():
    rng = np.random.default_rng(301)
    shape = (3, 3, 3)
    links = rng.normal(scale=0.4, size=(3,) + shape)
    beta = 0.9

    force = compact_gauge_force(links, beta)
    axis = 1
    idx = (1, 2, 0)
    eps = 1e-7

    plus = links.copy()
    minus = links.copy()
    plus[(axis,) + idx] += eps
    minus[(axis,) + idx] -= eps

    fd = (
        compact_gauge_energy(plus, beta)
        - compact_gauge_energy(minus, beta)
    ) / (2.0*eps)

    assert math.isclose(force[(axis,) + idx], -fd, rel_tol=1e-6, abs_tol=1e-6)


def test_compact_energy_is_two_pi_periodic_in_single_link():
    rng = np.random.default_rng(302)
    shape = (3, 3, 3)
    links = rng.normal(scale=0.3, size=(3,) + shape)
    shifted = links.copy()
    shifted[0, 1, 1, 1] += 2.0*math.pi

    e0 = compact_gauge_energy(links, 1.0)
    e1 = compact_gauge_energy(shifted, 1.0)
    assert math.isclose(e0, e1, rel_tol=0, abs_tol=1e-12)


def test_principal_angle_wraps_links():
    values = np.array([-4*math.pi, -3.2, 0.0, 3.2, 4*math.pi])
    wrapped = principal_angle(values)
    assert np.all(wrapped >= -math.pi)
    assert np.all(wrapped < math.pi)


def test_small_compact_coupled_system_conserves_energy_charge_and_gauss():
    rng = np.random.default_rng(303)
    shape = (4, 4, 4)
    amplitude = 1e-3
    phases = rng.normal(scale=0.2, size=shape)

    phi = amplitude*np.exp(1j*phases)
    momentum = np.zeros(shape, dtype=complex)
    chi = np.zeros(shape)
    chi_velocity = np.zeros(shape)
    links = np.zeros((3,) + shape)
    electric = np.zeros((3,) + shape)

    params = FullyCoupledParameters(
        matter=MatterPotential(
            mass2=1.0,
            lambda4=-0.1,
            lambda6=0.02,
        ),
        beta=1.0,
        scalar_field_kappa=0.7,
        matter_content_coupling=0.03,
        content_wave_speed=1.0,
    )

    state = FullyCoupledCompactFields(
        phi,
        momentum,
        chi,
        chi_velocity,
        links,
        electric,
        params,
    )

    e0 = state.energy
    q0 = state.charge
    g0 = state.max_abs_gauss_residual()

    for _ in range(300):
        state.step(0.001)

    assert abs(state.energy - e0)/abs(e0) < 5e-4
    assert abs(state.charge - q0) < 1e-10
    assert state.max_abs_gauss_residual() < g0 + 1e-8
