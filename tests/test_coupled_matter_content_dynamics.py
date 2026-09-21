import math
import numpy as np

from src.coupled_matter_content_dynamics import (
    CoupledMatterContentDynamics,
    content_acceleration,
    coupled_total_energy,
)
from src.localized_matter_variational import MatterPotential
from src.unified_variational_action import gauge_transform


def test_positive_matter_density_sources_positive_content_acceleration():
    shape = (5, 5, 5)
    phi = np.zeros(shape, dtype=complex)
    phi[2, 2, 2] = 1.0
    chi = np.zeros(shape)

    acceleration = content_acceleration(
        phi,
        chi,
        scalar_field_kappa=0.8,
        matter_content_coupling=0.5,
        content_wave_speed=1.2,
    )

    assert acceleration[2, 2, 2] > 0
    assert acceleration[0, 0, 0] == 0.0


def test_coupled_energy_is_gauge_invariant():
    rng = np.random.default_rng(222)
    shape = (4, 4, 4)
    phi = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    momentum = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    chi = rng.normal(scale=0.1, size=shape)
    chi_velocity = rng.normal(scale=0.1, size=shape)
    links = rng.normal(scale=0.2, size=(3,) + shape)
    alpha = rng.normal(size=shape)

    potential = MatterPotential(
        mass2=1.0,
        lambda4=-0.1,
        lambda6=0.02,
    )

    e0 = coupled_total_energy(
        phi,
        momentum,
        chi,
        chi_velocity,
        links,
        potential,
        0.9,
        0.2,
        1.0,
    )

    phi2, links2 = gauge_transform(phi, links, alpha)
    momentum2 = np.exp(1j * alpha) * momentum

    e1 = coupled_total_energy(
        phi2,
        momentum2,
        chi,
        chi_velocity,
        links2,
        potential,
        0.9,
        0.2,
        1.0,
    )

    assert math.isclose(e0, e1, rel_tol=0, abs_tol=1e-10)


def test_small_coupled_configuration_conserves_energy_and_charge():
    shape = (5, 5, 5)
    coords = np.indices(shape, dtype=float)
    center = np.array([(n - 1) / 2 for n in shape])[:, None, None, None]
    r2 = np.sum((coords - center) ** 2, axis=0)

    phi = (1e-3 * np.exp(-r2 / 4.0)).astype(complex)
    momentum = 1j * 0.9 * phi
    chi = np.zeros(shape)
    chi_velocity = np.zeros(shape)
    links = np.zeros((3,) + shape)

    state = CoupledMatterContentDynamics(
        phi=phi,
        momentum=momentum,
        chi=chi,
        chi_velocity=chi_velocity,
        links=links,
        potential=MatterPotential(
            mass2=1.0,
            lambda4=-0.2,
            lambda6=0.05,
        ),
        scalar_field_kappa=0.5,
        matter_content_coupling=0.05,
        content_wave_speed=1.0,
    )

    e0 = state.energy
    q0 = state.charge

    for _ in range(500):
        state.step(0.001)

    assert abs(state.energy - e0) / abs(e0) < 2e-4
    assert abs(state.charge - q0) / abs(q0) < 1e-8


def test_zero_coupling_keeps_zero_content_field_zero():
    shape = (3, 3, 3)
    phi = np.ones(shape, dtype=complex) * 1e-3
    state = CoupledMatterContentDynamics(
        phi=phi,
        momentum=1j * phi,
        chi=np.zeros(shape),
        chi_velocity=np.zeros(shape),
        links=np.zeros((3,) + shape),
        matter_content_coupling=0.0,
    )

    for _ in range(10):
        state.step(0.01)

    assert np.allclose(state.chi, 0.0, atol=0, rtol=0)
    assert np.allclose(state.chi_velocity, 0.0, atol=0, rtol=0)
