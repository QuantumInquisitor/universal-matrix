import numpy as np

from src.su3_hamiltonian import (
    SU3Hamiltonian,
    analytic_wilson_force,
    drift_links,
    max_gauss_residual,
    reference_force,
    su3_exp,
)
from src.su3_lattice_gauge import (
    is_su3,
    random_links,
)


def test_su3_exponential_is_special_unitary():
    u = su3_exp(
        np.array([0.2,-0.1,0.3,0.4,0.0,-0.2,0.1,0.25])
    )
    assert is_su3(u, tolerance=1e-11)


def test_group_drift_preserves_su3_links():
    rng = np.random.default_rng(1401)
    shape = (1,1,1)
    links = random_links(shape, rng)
    electric = rng.normal(
        scale=0.15,
        size=(3,) + shape + (8,),
    )

    moved = drift_links(
        links,
        electric,
        dt=0.07,
    )

    for axis in range(3):
        assert is_su3(
            moved[axis,0,0,0],
            tolerance=2e-11,
        )


def test_analytic_su3_force_matches_group_reference():
    rng = np.random.default_rng(1402)
    shape = (1,1,1)
    links = random_links(shape, rng)
    beta = 0.61

    analytic = analytic_wilson_force(
        links,
        beta,
    )
    reference = reference_force(
        links,
        beta,
        epsilon=2e-6,
    )

    assert np.allclose(
        analytic,
        reference,
        atol=3e-8,
        rtol=3e-8,
    )


def test_su3_force_has_zero_covariant_divergence():
    rng = np.random.default_rng(1403)
    shape = (1,1,1)
    links = random_links(shape, rng)
    force = analytic_wilson_force(
        links,
        beta=0.5,
    )

    assert max_gauss_residual(
        links,
        force,
    ) < 2e-10


def test_su3_evolution_preserves_gauss_from_zero_electric():
    rng = np.random.default_rng(1404)
    shape = (1,1,1)
    links = random_links(shape, rng)
    electric = np.zeros((3,) + shape + (8,))

    state = SU3Hamiltonian(
        links,
        electric,
        beta=0.2,
    )
    for _ in range(20):
        state.step(0.001)

    assert state.max_gauss < 5e-10


def test_su3_small_evolution_has_small_energy_drift():
    rng = np.random.default_rng(1405)
    shape = (1,1,1)

    links = np.empty(
        (3,) + shape + (3,3),
        dtype=complex,
    )
    for axis in range(3):
        links[axis,0,0,0] = su3_exp(
            rng.normal(scale=0.04, size=8)
        )

    electric = np.zeros((3,) + shape + (8,))
    state = SU3Hamiltonian(
        links,
        electric,
        beta=0.35,
    )

    e0 = state.energy
    for _ in range(100):
        state.step(0.001)

    assert e0 > 0.0
    assert abs(state.energy-e0)/e0 < 3e-5
