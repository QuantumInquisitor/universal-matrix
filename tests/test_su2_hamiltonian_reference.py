import math
import numpy as np

from src.su2_hamiltonian_reference import (
    SU2HamiltonianReference,
    drift_links,
    identity_links,
    max_gauss_residual,
    su2_exp,
    wilson_force_reference,
    zero_electric,
)
from src.su2_lattice_gauge import (
    is_su2,
    random_links,
    wilson_action,
)


def test_su2_exponential_is_special_unitary():
    u = su2_exp(np.array([0.3,-0.2,0.7]))
    assert is_su2(u, tolerance=1e-12)


def test_group_drift_preserves_su2_links():
    rng = np.random.default_rng(1201)
    shape = (2,2,2)
    links = random_links(shape, rng)
    electric = rng.normal(
        scale=0.2,
        size=(3,) + shape + (3,),
    )
    moved = drift_links(links, electric, dt=0.1)

    for axis in range(3):
        for idx in np.ndindex(shape):
            assert is_su2(
                moved[(axis,) + idx],
                tolerance=1e-11,
            )


def test_reference_force_is_negative_group_derivative():
    rng = np.random.default_rng(1202)
    shape = (2,2,2)
    links = random_links(shape, rng)
    beta = 0.7
    eps = 2e-6

    force = wilson_force_reference(
        links,
        beta,
        epsilon=eps,
    )

    axis = 1
    idx = (0,1,1)
    component = 2

    direction = np.zeros(3)
    direction[component] = eps

    plus = links.copy()
    minus = links.copy()
    from src.su2_hamiltonian_reference import su2_exp

    plus[(axis,) + idx] = (
        su2_exp(direction)
        @ links[(axis,) + idx]
    )
    minus[(axis,) + idx] = (
        su2_exp(-direction)
        @ links[(axis,) + idx]
    )

    derivative = (
        wilson_action(plus, beta)
        - wilson_action(minus, beta)
    )/(2.0*eps)

    assert math.isclose(
        force[(axis,) + idx + (component,)],
        -derivative,
        rel_tol=0,
        abs_tol=1e-9,
    )


def test_identity_zero_electric_is_exact_stationary_state():
    state = SU2HamiltonianReference.zeros(
        shape=(2,2,2),
        beta=1.0,
    )
    assert state.energy == 0.0
    assert state.max_gauss == 0.0

    state.step(0.05)

    assert abs(state.energy) < 1e-18
    assert state.max_gauss < 1e-12


def test_gauss_zero_for_identity_links_and_uniform_electric():
    shape = (2,2,2)
    links = identity_links(shape)
    electric = zero_electric(shape)
    electric[...,0] = 0.25

    assert max_gauss_residual(
        links,
        electric,
    ) < 1e-14


def test_small_source_free_evolution_has_small_energy_drift():
    rng = np.random.default_rng(1203)
    shape = (2,2,2)

    links = identity_links(shape)
    # Small pure-gauge-like initial link perturbation created by assigning
    # opposite algebra rotations on neighboring directions is sufficient for
    # an integration stability smoke test.
    for axis in range(3):
        for idx in np.ndindex(shape):
            vec = rng.normal(scale=0.015, size=3)
            links[(axis,) + idx] = su2_exp(vec)

    electric = np.zeros((3,) + shape + (3,))
    state = SU2HamiltonianReference(
        links,
        electric,
        beta=0.5,
        force_epsilon=2e-6,
    )

    e0 = state.energy
    for _ in range(5):
        state.step(0.002)

    assert e0 > 0
    assert abs(state.energy-e0)/e0 < 2e-4
