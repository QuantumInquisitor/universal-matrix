import math
import numpy as np

from src.unified_variational_action import (
    UnifiedActionParameters,
    chi_euler_lagrange_residual,
    gauge_transform,
    global_u1_charge,
    total_static_energy,
)


def _random_state(seed=1234):
    rng = np.random.default_rng(seed)
    shape = (4, 4, 4)
    phi = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    chi = rng.normal(size=shape)
    links = rng.normal(scale=0.2, size=(3,) + shape)
    return phi, chi, links


def test_total_energy_is_locally_gauge_invariant():
    phi, chi, links = _random_state()
    rng = np.random.default_rng(44)
    alpha = rng.normal(size=phi.shape)

    params = UnifiedActionParameters(
        kappa_chi=0.8,
        g_chi=0.2,
        beta=1.3,
        mass2=0.7,
        lambda4=-0.1,
        lambda6=0.02,
    )

    e0 = total_static_energy(phi, chi, links, params)["total"]
    phi2, links2 = gauge_transform(phi, links, alpha)
    e1 = total_static_energy(phi2, chi, links2, params)["total"]

    assert math.isclose(e0, e1, rel_tol=0, abs_tol=1e-10)


def test_global_u1_norm_is_gauge_invariant():
    phi, _, links = _random_state()
    rng = np.random.default_rng(45)
    alpha = rng.normal(size=phi.shape)
    phi2, _ = gauge_transform(phi, links, alpha)
    assert math.isclose(
        global_u1_charge(phi),
        global_u1_charge(phi2),
        rel_tol=0,
        abs_tol=1e-12,
    )


def test_chi_variation_matches_finite_difference_energy_derivative():
    phi, chi, links = _random_state()
    params = UnifiedActionParameters(
        kappa_chi=1.2,
        g_chi=0.3,
        beta=0.5,
        mass2=0.8,
        lambda4=0.0,
        lambda6=0.01,
    )

    residual = chi_euler_lagrange_residual(phi, chi, params)
    idx = (1, 2, 3)
    eps = 1e-6

    chi_plus = chi.copy()
    chi_minus = chi.copy()
    chi_plus[idx] += eps
    chi_minus[idx] -= eps

    e_plus = total_static_energy(phi, chi_plus, links, params)["total"]
    e_minus = total_static_energy(phi, chi_minus, links, params)["total"]
    finite_difference = (e_plus - e_minus) / (2.0 * eps)

    assert math.isclose(
        finite_difference,
        residual[idx],
        rel_tol=1e-7,
        abs_tol=1e-7,
    )


def test_zero_fields_have_zero_gradient_and_gauge_energy():
    shape = (3, 3, 3)
    phi = np.zeros(shape, dtype=complex)
    chi = np.zeros(shape)
    links = np.zeros((3,) + shape)
    params = UnifiedActionParameters()

    energies = total_static_energy(phi, chi, links, params)
    assert energies["total"] == 0.0
    assert energies["scalar_gradient"] == 0.0
    assert energies["matter_gradient"] == 0.0
    assert energies["gauge_wilson"] == 0.0


def test_positive_sextic_stabilizes_large_amplitude_potential():
    shape = (2, 2, 2)
    chi = np.zeros(shape)
    links = np.zeros((3,) + shape)
    params = UnifiedActionParameters(
        mass2=1.0,
        lambda4=-2.0,
        lambda6=1.0,
    )

    moderate = total_static_energy(
        np.full(shape, 1.0 + 0j), chi, links, params
    )["matter_potential"]
    large = total_static_energy(
        np.full(shape, 10.0 + 0j), chi, links, params
    )["matter_potential"]

    assert large > moderate
