import math
import numpy as np

from src.classical_matter_dynamics import (
    ClassicalMatterDynamics,
    gauge_covariant_laplacian,
    matter_charge,
    matter_energy,
)
from src.localized_matter_variational import MatterPotential
from src.unified_variational_action import gauge_transform


def test_uniform_free_field_has_zero_spatial_laplacian():
    phi = np.ones((4, 4, 4), dtype=complex)
    links = np.zeros((3, 4, 4, 4))
    lap = gauge_covariant_laplacian(phi, links)
    assert np.allclose(lap, 0.0, atol=1e-15, rtol=0)


def test_charge_and_energy_are_gauge_invariant_for_fixed_time_slice():
    rng = np.random.default_rng(101)
    shape = (4, 4, 4)
    phi = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    momentum = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    links = rng.normal(scale=0.2, size=(3,) + shape)
    alpha = rng.normal(size=shape)

    potential = MatterPotential(
        mass2=1.0,
        lambda4=-0.2,
        lambda6=0.05,
    )

    e0 = matter_energy(phi, momentum, links, potential)
    q0 = matter_charge(phi, momentum)

    phi2, links2 = gauge_transform(phi, links, alpha)
    momentum2 = np.exp(1j * alpha) * momentum

    e1 = matter_energy(phi2, momentum2, links2, potential)
    q1 = matter_charge(phi2, momentum2)

    assert math.isclose(e0, e1, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(q0, q1, rel_tol=0, abs_tol=1e-10)


def test_small_free_uniform_mode_conserves_energy_and_charge():
    shape = (3, 3, 3)
    amplitude = 1e-3
    mass = 1.0
    phi = np.full(shape, amplitude + 0j, dtype=complex)
    momentum = 1j * mass * phi
    links = np.zeros((3,) + shape)
    potential = MatterPotential(
        mass2=mass**2,
        lambda4=0.0,
        lambda6=1e-12,
    )

    state = ClassicalMatterDynamics(
        phi=phi,
        momentum=momentum,
        links=links,
        potential=potential,
    )

    e0 = state.energy
    q0 = state.charge
    for _ in range(1000):
        state.step(0.002)

    assert abs(state.energy - e0) / e0 < 1e-5
    assert abs(state.charge - q0) / q0 < 1e-10


def test_zero_field_remains_zero():
    shape = (3, 3, 3)
    state = ClassicalMatterDynamics(
        phi=np.zeros(shape, dtype=complex),
        momentum=np.zeros(shape, dtype=complex),
        links=np.zeros((3,) + shape),
    )
    state.step(0.1)
    assert np.all(state.phi == 0)
    assert np.all(state.momentum == 0)
    assert state.energy == 0.0
    assert state.charge == 0.0



def test_plane_wave_laplacian_scales_with_inverse_spacing_squared():
    n = 8
    shape = (n, 3, 3)
    spacing = 0.5
    k = 2.0 * math.pi / n
    x = np.arange(n, dtype=float)[:, None, None]
    phi = np.broadcast_to(np.exp(1j * k * x), shape).copy()
    links = np.zeros((3,) + shape)

    lap = gauge_covariant_laplacian(
        phi,
        links,
        spacing=spacing,
    )
    eigenvalue = -4.0 * math.sin(0.5 * k) ** 2 / spacing**2

    assert np.allclose(lap, eigenvalue * phi, atol=1e-12)


def test_uniform_charge_and_energy_scale_with_cell_volume():
    shape = (3, 3, 3)
    phi = np.full(shape, 0.2 + 0.1j, dtype=complex)
    momentum = np.full(shape, -0.3 + 0.4j, dtype=complex)
    links = np.zeros((3,) + shape)
    potential = MatterPotential(
        mass2=1.2,
        lambda4=0.0,
        lambda6=0.0,
    )

    q1 = matter_charge(phi, momentum, spacing=1.0)
    e1 = matter_energy(phi, momentum, links, potential, spacing=1.0)

    spacing = 0.5
    qh = matter_charge(phi, momentum, spacing=spacing)
    eh = matter_energy(phi, momentum, links, potential, spacing=spacing)

    assert math.isclose(qh, q1 * spacing**3, rel_tol=0, abs_tol=1e-14)
    assert math.isclose(eh, e1 * spacing**3, rel_tol=0, abs_tol=1e-14)


def test_nonunit_spacing_state_preserves_free_uniform_charge_and_energy():
    shape = (4, 4, 4)
    spacing = 0.5
    amplitude = 1e-3
    mass = 1.0
    phi = np.full(shape, amplitude + 0j, dtype=complex)
    momentum = 1j * mass * phi
    links = np.zeros((3,) + shape)
    potential = MatterPotential(
        mass2=mass**2,
        lambda4=0.0,
        lambda6=1e-12,
    )
    state = ClassicalMatterDynamics(
        phi=phi,
        momentum=momentum,
        links=links,
        potential=potential,
        lattice_spacing=spacing,
    )

    e0 = state.energy
    q0 = state.charge
    for _ in range(500):
        state.step(0.001)

    assert abs(state.energy - e0) / e0 < 1e-6
    assert abs(state.charge - q0) / q0 < 1e-10
    assert state.lattice_spacing == spacing
