import math
import numpy as np

from src.reciprocity_dynamic_su3_geometry import (
    SU3DynamicReciprocity,
    analytic_weighted_force,
    geometry_rhs,
    total_energy,
    weighted_group_force_reference,
)
from src.reciprocity_nonabelian_spatial_geometry import (
    source_sum_identity_residual,
    weighted_su3_energy,
)
from src.su3_lattice_gauge import random_links
from src.su3_hamiltonian import max_gauss_residual


def _state(seed=1201):
    rng = np.random.default_rng(seed)
    shape = (2, 2, 2)
    links = random_links(shape, rng)
    electric = rng.normal(scale=0.03, size=(3,) + shape + (8,))
    psi = rng.normal(scale=0.05, size=shape)
    psi_momentum = rng.normal(scale=0.02, size=shape)
    return psi, psi_momentum, links, electric


def test_weighted_su3_force_matches_group_finite_difference():
    psi, _, links, _ = _state()
    beta = 0.7

    analytic = analytic_weighted_force(links, psi, beta)
    reference = weighted_group_force_reference(
        links,
        psi,
        beta,
        epsilon=2e-6,
    )

    assert np.allclose(
        analytic,
        reference,
        atol=2e-5,
        rtol=2e-5,
    )


def test_geometry_source_sum_is_twice_weighted_su3_energy():
    psi, _, links, electric = _state(1202)
    residual = source_sum_identity_residual(
        links,
        electric,
        psi,
        beta=0.8,
        group_dimension=3,
    )
    assert abs(residual) < 1e-10


def test_zero_gauge_field_does_not_source_geometry():
    shape = (2, 2, 2)
    psi = np.zeros(shape)
    momentum = np.zeros(shape)
    links = np.empty((3,) + shape + (3, 3), dtype=complex)
    links[...] = np.eye(3)
    electric = np.zeros((3,) + shape + (8,))

    _, p_dot = geometry_rhs(
        psi,
        momentum,
        links,
        electric,
        kappa=1.0,
        beta=1.0,
    )
    assert np.allclose(p_dot, 0.0, atol=1e-14, rtol=0)


def test_dynamic_step_keeps_energy_close_for_small_dt():
    psi, momentum, links, electric = _state(1203)
    state = SU3DynamicReciprocity(
        psi,
        momentum,
        links,
        electric,
        kappa=0.9,
        beta=0.6,
    )

    e0 = state.energy
    for _ in range(5):
        state.step(2e-5)

    assert abs(state.energy - e0) / abs(e0) < 2e-5


def test_uniform_zero_psi_recovers_unweighted_su3_energy():
    _, _, links, electric = _state(1204)
    psi = np.zeros((2, 2, 2))
    weighted = weighted_su3_energy(
        links,
        electric,
        psi,
        beta=0.8,
    )

    kinetic = 0.5 * float(np.sum(electric**2))
    from src.su3_lattice_gauge import wilson_action
    expected = kinetic + wilson_action(links, beta=0.8)

    assert math.isclose(
        weighted,
        expected,
        rel_tol=0,
        abs_tol=1e-11,
    )


def test_gauss_residual_stays_finite_after_small_step():
    psi, momentum, links, electric = _state(1205)
    state = SU3DynamicReciprocity(
        psi,
        momentum,
        links,
        electric,
        kappa=1.0,
        beta=0.5,
    )
    before = max_gauss_residual(state.links, state.electric)
    state.step(1e-5)
    after = max_gauss_residual(state.links, state.electric)

    assert math.isfinite(before)
    assert math.isfinite(after)


def test_total_energy_function_matches_state_property():
    psi, momentum, links, electric = _state(1206)
    state = SU3DynamicReciprocity(
        psi,
        momentum,
        links,
        electric,
        kappa=0.8,
        beta=0.9,
    )

    assert math.isclose(
        state.energy,
        total_energy(
            state.psi,
            state.psi_momentum,
            state.links,
            state.electric,
            state.kappa,
            state.beta,
        ),
        rel_tol=0,
        abs_tol=1e-12,
    )
