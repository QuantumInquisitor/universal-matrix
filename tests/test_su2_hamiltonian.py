import numpy as np

from src.su2_hamiltonian import (
    SU2Hamiltonian,
    analytic_wilson_force,
    force_gauss_residual,
)
from src.su2_hamiltonian_reference import (
    su2_exp,
    wilson_force_reference,
)
from src.su2_lattice_gauge import random_links


def test_analytic_force_matches_group_finite_difference_reference():
    rng = np.random.default_rng(1301)
    shape = (2,2,2)
    links = random_links(shape, rng)
    beta = 0.73

    analytic = analytic_wilson_force(
        links,
        beta,
    )
    reference = wilson_force_reference(
        links,
        beta,
        epsilon=2e-6,
    )

    assert np.allclose(
        analytic,
        reference,
        atol=2e-8,
        rtol=2e-8,
    )


def test_analytic_force_has_zero_covariant_divergence():
    rng = np.random.default_rng(1302)
    links = random_links((2,2,2), rng)

    assert force_gauss_residual(
        links,
        beta=0.6,
    ) < 1e-11


def test_optimized_evolution_preserves_gauss_from_zero_electric():
    rng = np.random.default_rng(1303)
    shape = (2,2,2)
    links = random_links(shape, rng)
    electric = np.zeros((3,) + shape + (3,))

    state = SU2Hamiltonian(
        links,
        electric,
        beta=0.2,
    )

    g0 = state.max_gauss
    for _ in range(20):
        state.step(0.002)

    assert g0 == 0.0
    assert state.max_gauss < 2e-10


def test_optimized_evolution_has_small_energy_drift():
    rng = np.random.default_rng(1304)
    shape = (2,2,2)

    links = np.empty(
        (3,) + shape + (2,2),
        dtype=complex,
    )
    for axis in range(3):
        for idx in np.ndindex(shape):
            links[(axis,) + idx] = su2_exp(
                rng.normal(scale=0.05, size=3)
            )

    electric = np.zeros((3,) + shape + (3,))

    state = SU2Hamiltonian(
        links,
        electric,
        beta=0.4,
    )
    e0 = state.energy

    for _ in range(100):
        state.step(0.001)

    assert e0 > 0.0
    assert abs(state.energy-e0)/e0 < 2e-5
