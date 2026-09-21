import math
import numpy as np

from src.reciprocity_dirac_constant_background import (
    hamiltonian as constant_hamiltonian,
)
from src.reciprocity_dirac_time_background import (
    HomogeneousReciprocityDiracMode,
    curved_norm,
    from_rescaled,
    massless_coordinate_speed,
    metric_null_coordinate_speed,
    rescaled_hamiltonian,
    rescaled_rhs,
    to_rescaled,
    unrescaled_rhs,
)


def test_rescaled_hamiltonian_is_hermitian():
    h = rescaled_hamiltonian(
        (0.2, -0.4, 0.5),
        mass=0.7,
        psi=0.3,
    )
    assert np.allclose(h, h.conj().T, atol=1e-14, rtol=0)


def test_static_limit_matches_constant_background_bridge():
    p = (0.2, 0.1, -0.4)
    mass = 0.8
    psi = 0.25
    assert np.allclose(
        rescaled_hamiltonian(p, mass, psi),
        constant_hamiltonian(p, mass, psi),
        atol=1e-14,
        rtol=0,
    )


def test_rescaled_and_unrescaled_rhs_are_consistent():
    spinor = np.array(
        [1.0, 0.2j, -0.3, 0.4+0.1j],
        dtype=complex,
    )
    p = (0.3, -0.1, 0.2)
    mass = 0.9
    psi = 0.17
    psi_dot = -0.08

    chi = to_rescaled(spinor, psi)
    chi_dot_direct = rescaled_rhs(chi, p, mass, psi)

    spinor_dot = unrescaled_rhs(
        spinor,
        p,
        mass,
        psi,
        psi_dot,
    )
    scale = math.exp(1.5*psi)
    chi_dot_from_product = scale * (
        spinor_dot + 1.5*psi_dot*spinor
    )

    assert np.allclose(
        chi_dot_direct,
        chi_dot_from_product,
        atol=1e-13,
        rtol=0,
    )


def test_curved_norm_equals_rescaled_flat_norm():
    spinor = np.array(
        [0.8, 0.2j, -0.1, 0.3+0.2j],
        dtype=complex,
    )
    psi = 0.31
    chi = to_rescaled(spinor, psi)

    assert math.isclose(
        curved_norm(spinor, psi),
        float(np.vdot(chi, chi).real),
        rel_tol=0,
        abs_tol=1e-14,
    )
    assert np.allclose(
        from_rescaled(chi, psi),
        spinor,
        atol=1e-14,
        rtol=0,
    )


def test_time_dependent_rescaled_evolution_conserves_norm():
    psi_function = lambda t: 0.15*math.sin(0.4*t)
    state = HomogeneousReciprocityDiracMode(
        momentum=(0.2, -0.1, 0.3),
        mass=0.7,
        chi=np.array(
            [1.0, 0.2j, -0.1, 0.05],
            dtype=complex,
        ),
        psi_function=psi_function,
    )

    n0 = state.norm
    for _ in range(1000):
        state.step(0.001)

    assert abs(state.norm-n0)/n0 < 1e-11


def test_massless_spinor_speed_matches_metric_null_speed():
    for psi in (-0.4, 0.0, 0.8):
        assert math.isclose(
            massless_coordinate_speed(psi),
            metric_null_coordinate_speed(psi),
            rel_tol=0,
            abs_tol=1e-15,
        )
