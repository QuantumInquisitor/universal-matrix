import math
import numpy as np

from src.fully_coupled_classical_fields import (
    FullyCoupledClassicalFields,
    FullyCoupledParameters,
    electric_force,
    gauge_magnetic_energy,
    matter_link_energy,
    matter_link_gradient,
    total_energy,
)
from src.localized_matter_variational import MatterPotential


def test_matter_link_gradient_matches_finite_difference():
    rng = np.random.default_rng(9)
    shape = (3, 3, 3)
    phi = rng.normal(size=shape) + 1j*rng.normal(size=shape)
    links = rng.normal(scale=0.1, size=(3,) + shape)

    grad = matter_link_gradient(phi, links)
    idx = (1, 1, 1)
    axis = 2
    eps = 1e-7

    plus = links.copy()
    minus = links.copy()
    plus[(axis,) + idx] += eps
    minus[(axis,) + idx] -= eps

    fd = (
        matter_link_energy(phi, plus)
        - matter_link_energy(phi, minus)
    ) / (2.0*eps)

    assert math.isclose(fd, grad[(axis,) + idx], rel_tol=1e-6, abs_tol=1e-6)


def test_gauge_force_matches_negative_finite_difference():
    rng = np.random.default_rng(10)
    shape = (3, 3, 3)
    links = rng.normal(scale=0.1, size=(3,) + shape)
    phi = np.zeros(shape, dtype=complex)
    params = FullyCoupledParameters(beta=0.7)

    force = electric_force(phi, links, params)
    idx = (0, 1, 2)
    axis = 1
    eps = 1e-7

    plus = links.copy()
    minus = links.copy()
    plus[(axis,) + idx] += eps
    minus[(axis,) + idx] -= eps

    fd = (
        gauge_magnetic_energy(plus, params.beta)
        - gauge_magnetic_energy(minus, params.beta)
    ) / (2.0*eps)

    assert math.isclose(force[(axis,) + idx], -fd, rel_tol=1e-6, abs_tol=1e-6)


def test_fully_coupled_small_system_conserves_energy_charge_and_gauss():
    rng = np.random.default_rng(11)
    shape = (4, 4, 4)

    amplitude = 1e-3
    phases = rng.normal(scale=0.2, size=shape)
    phi = amplitude * np.exp(1j * phases)
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

    state = FullyCoupledClassicalFields(
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

    assert abs(state.energy - e0) / abs(e0) < 5e-4
    assert abs(state.charge - q0) < 1e-10
    assert state.max_abs_gauss_residual() < g0 + 1e-8


def test_zero_state_remains_zero():
    shape = (3, 3, 3)
    state = FullyCoupledClassicalFields(
        phi=np.zeros(shape, dtype=complex),
        momentum=np.zeros(shape, dtype=complex),
        chi=np.zeros(shape),
        chi_velocity=np.zeros(shape),
        links=np.zeros((3,) + shape),
        electric=np.zeros((3,) + shape),
    )
    state.step(0.1)
    assert state.energy == 0.0
    assert state.charge == 0.0
    assert state.max_abs_gauss_residual() == 0.0
