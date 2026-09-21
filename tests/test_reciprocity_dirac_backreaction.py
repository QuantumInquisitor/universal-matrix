import math

import numpy as np

from src.reciprocity_dirac_backreaction import (
    DiracReciprocityBackreaction,
    geometry_energy,
    rhs,
    total_energy,
)


def _small_state(seed=1801):
    rng = np.random.default_rng(seed)
    shape = (2, 2, 2)
    chi = (
        rng.normal(scale=0.03, size=shape + (4,))
        + 1j * rng.normal(scale=0.03, size=shape + (4,))
    )
    psi = rng.normal(scale=0.02, size=shape)
    psi_momentum = rng.normal(scale=0.01, size=shape)
    return chi, psi, psi_momentum


def test_geometry_energy_is_nonnegative():
    _, psi, momentum = _small_state()
    assert geometry_energy(psi, momentum, kappa=0.8) >= 0.0


def test_rhs_shapes_match_state():
    chi, psi, momentum = _small_state()
    dchi, dpsi, dp = rhs(
        chi,
        psi,
        momentum,
        mass=0.7,
        kappa=1.2,
    )
    assert dchi.shape == chi.shape
    assert dpsi.shape == psi.shape
    assert dp.shape == momentum.shape


def test_zero_spinor_removes_dirac_backreaction():
    shape = (2, 2, 2)
    chi = np.zeros(shape + (4,), dtype=complex)
    psi = np.zeros(shape)
    momentum = np.zeros(shape)

    _, _, dp = rhs(
        chi,
        psi,
        momentum,
        mass=1.0,
        kappa=1.0,
    )
    assert np.allclose(dp, 0.0, atol=0, rtol=0)


def test_rest_spinor_sources_geometry_positive():
    shape = (2, 2, 2)
    chi = np.zeros(shape + (4,), dtype=complex)
    chi[..., 0] = 0.05
    psi = np.zeros(shape)
    momentum = np.zeros(shape)

    _, _, dp = rhs(
        chi,
        psi,
        momentum,
        mass=1.3,
        kappa=1.0,
    )
    assert np.all(dp > 0.0)


def test_short_coupled_evolution_preserves_spinor_norm():
    chi, psi, momentum = _small_state()
    system = DiracReciprocityBackreaction(
        chi=chi,
        psi=psi,
        psi_momentum=momentum,
        mass=0.8,
        kappa=1.0,
    )
    before = system.norm

    for _ in range(40):
        system.step_rk4(2e-4)

    after = system.norm
    assert math.isclose(
        before,
        after,
        rel_tol=0,
        abs_tol=2e-11,
    )


def test_short_coupled_evolution_has_small_total_energy_drift():
    chi, psi, momentum = _small_state(seed=1802)
    system = DiracReciprocityBackreaction(
        chi=chi,
        psi=psi,
        psi_momentum=momentum,
        mass=0.6,
        kappa=0.9,
    )
    before = system.energy

    for _ in range(30):
        system.step_rk4(1e-4)

    after = system.energy
    scale = max(1.0, abs(before))
    assert abs(after - before) / scale < 5e-10


def test_total_energy_function_matches_system_property():
    chi, psi, momentum = _small_state(seed=1803)
    system = DiracReciprocityBackreaction(
        chi=chi,
        psi=psi,
        psi_momentum=momentum,
        mass=1.1,
        kappa=1.4,
        spacing=0.8,
    )
    explicit = total_energy(
        chi,
        psi,
        momentum,
        mass=1.1,
        kappa=1.4,
        spacing=0.8,
    )
    assert math.isclose(
        system.energy,
        explicit,
        rel_tol=0,
        abs_tol=1e-15,
    )
