import math
import numpy as np

from src.localized_matter_variational import MatterPotential
from src.self_consistent_reciprocity_action import (
    ReciprocityActionParameters,
    SelfConsistentReciprocityDynamics,
    active_source_density_canonical,
    active_source_density_velocity_form,
    null_coordinate_speed,
    rest_harmonic_source_energy_identity,
    scalar_characteristic_speed,
)


def test_rest_harmonic_mode_sources_exact_rest_energy_density():
    source, energy = rest_harmonic_source_energy_identity(
        amplitude=0.7,
        mass=1.3,
    )
    assert math.isclose(source, energy, rel_tol=0, abs_tol=1e-15)


def test_velocity_and_canonical_source_forms_agree():
    rng = np.random.default_rng(1001)
    shape = (3,3,3)
    phi = rng.normal(size=shape) + 1j*rng.normal(size=shape)
    psi = rng.normal(scale=0.1, size=shape)
    velocity = (
        rng.normal(size=shape)
        + 1j*rng.normal(size=shape)
    )
    momentum = np.exp(4.0*psi) * velocity
    potential = MatterPotential(
        mass2=1.0,
        lambda4=-0.2,
        lambda6=0.05,
    )

    a = active_source_density_velocity_form(
        phi, velocity, psi, potential
    )
    b = active_source_density_canonical(
        phi, momentum, psi, potential
    )

    assert np.allclose(a, b, atol=1e-11, rtol=0)


def test_scalar_characteristic_speed_matches_metric_null_speed():
    for psi in (-0.5, 0.0, 0.4, 1.0):
        assert math.isclose(
            scalar_characteristic_speed(psi),
            null_coordinate_speed(psi),
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_small_homogeneous_system_conserves_energy_and_u1_charge():
    shape = (3,3,3)
    amplitude = 1e-3
    mass = 1.0

    phi = np.full(shape, amplitude + 0j, dtype=complex)
    momentum = 1j * mass * phi
    psi = np.zeros(shape)
    psi_momentum = np.zeros(shape)

    params = ReciprocityActionParameters(
        kappa=0.2,
        matter=MatterPotential(
            mass2=mass**2,
            lambda4=0.0,
            lambda6=1e-12,
        ),
    )

    state = SelfConsistentReciprocityDynamics(
        phi=phi,
        momentum=momentum,
        psi=psi,
        psi_momentum=psi_momentum,
        params=params,
    )

    e0 = state.energy
    q0 = state.charge

    for _ in range(500):
        state.step_rk4(0.001)

    assert abs(state.energy - e0) / e0 < 1e-8
    assert abs(state.charge - q0) / q0 < 1e-9


def test_zero_state_remains_zero():
    shape = (3,3,3)
    state = SelfConsistentReciprocityDynamics(
        phi=np.zeros(shape, dtype=complex),
        momentum=np.zeros(shape, dtype=complex),
        psi=np.zeros(shape),
        psi_momentum=np.zeros(shape),
    )
    state.step_rk4(0.1)
    assert state.energy == 0.0
    assert state.charge == 0.0
    assert np.all(state.psi == 0.0)
    assert np.all(state.phi == 0.0)
