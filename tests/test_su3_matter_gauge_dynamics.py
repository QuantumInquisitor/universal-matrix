import math
import numpy as np

from src.su3_hamiltonian import su3_exp
from src.su3_lattice_gauge import (
    identity_links,
    random_site_gauge_transform,
)
from src.su3_matter_gauge_dynamics import (
    SU3MatterGaugeDynamics,
    SU3ScalarMatterParameters,
    gauge_transform_state,
    matter_hopping_energy,
    matter_link_current,
    total_energy,
)


def test_su3_matter_current_matches_hopping_group_derivative():
    rng = np.random.default_rng(1601)
    shape = (1,1,1)
    psi = (
        rng.normal(size=shape + (3,))
        + 1j*rng.normal(size=shape + (3,))
    )
    links = identity_links(shape)

    current = matter_link_current(psi, links)
    axis = 2
    idx = (0,0,0)
    component = 5
    eps = 1e-7

    direction = np.zeros(8)
    direction[component] = eps

    plus = links.copy()
    minus = links.copy()
    plus[(axis,) + idx] = (
        su3_exp(direction)
        @ links[(axis,) + idx]
    )
    minus[(axis,) + idx] = (
        su3_exp(-direction)
        @ links[(axis,) + idx]
    )

    derivative = (
        matter_hopping_energy(psi, plus)
        - matter_hopping_energy(psi, minus)
    )/(2.0*eps)

    assert math.isclose(
        current[(axis,) + idx + (component,)],
        derivative,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )


def test_su3_total_energy_is_locally_gauge_invariant():
    rng = np.random.default_rng(1602)
    shape = (1,1,1)
    psi = (
        rng.normal(size=shape + (3,))
        + 1j*rng.normal(size=shape + (3,))
    )
    momentum = (
        rng.normal(size=shape + (3,))
        + 1j*rng.normal(size=shape + (3,))
    )
    links = identity_links(shape)
    electric = rng.normal(
        scale=0.1,
        size=(3,) + shape + (8,),
    )
    transforms = random_site_gauge_transform(
        shape,
        rng,
    )

    params = SU3ScalarMatterParameters(
        mass2=0.8,
        lambda4=0.15,
    )

    e0 = total_energy(
        psi,momentum,links,electric,0.4,params
    )

    p2,m2,l2,e2 = gauge_transform_state(
        psi,
        momentum,
        links,
        electric,
        transforms,
    )

    e1 = total_energy(
        p2,m2,l2,e2,0.4,params
    )

    assert math.isclose(
        e0,e1,
        rel_tol=0,
        abs_tol=1e-9,
    )


def test_su3_coupled_evolution_preserves_gauss_and_energy():
    shape = (1,1,1)
    links = identity_links(shape)

    psi = np.zeros(shape + (3,), dtype=complex)
    psi[0,0,0] = np.array(
        [0.02,0.015,0.01],
        dtype=complex,
    )
    momentum = np.zeros_like(psi)
    electric = np.zeros((3,) + shape + (8,))

    state = SU3MatterGaugeDynamics(
        psi,
        momentum,
        links,
        electric,
        beta=0.25,
        matter_params=SU3ScalarMatterParameters(
            mass2=0.6,
            lambda4=0.1,
        ),
    )

    assert state.max_gauss == 0.0
    e0 = state.energy

    for _ in range(100):
        state.step(0.001)

    assert state.max_gauss < 3e-8
    assert abs(state.energy-e0)/e0 < 3e-5
