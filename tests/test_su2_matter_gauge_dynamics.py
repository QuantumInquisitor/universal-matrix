import math
import numpy as np

from src.su2_hamiltonian_reference import su2_exp
from src.su2_lattice_gauge import (
    identity_links,
    random_site_gauge_transform,
)
from src.su2_matter_gauge_dynamics import (
    SU2MatterGaugeDynamics,
    SU2ScalarMatterParameters,
    gauge_transform_state,
    matter_hopping_energy,
    matter_link_current,
    total_energy,
)


def test_matter_link_current_matches_hopping_energy_group_derivative():
    rng = np.random.default_rng(1501)
    shape = (2,2,2)
    psi = (
        rng.normal(size=shape + (2,))
        + 1j*rng.normal(size=shape + (2,))
    )
    links = identity_links(shape)

    current = matter_link_current(psi, links)
    axis = 1
    idx = (0,1,1)
    component = 2
    eps = 1e-7

    direction = np.zeros(3)
    direction[component] = eps

    plus = links.copy()
    minus = links.copy()
    plus[(axis,) + idx] = (
        su2_exp(direction)
        @ links[(axis,) + idx]
    )
    minus[(axis,) + idx] = (
        su2_exp(-direction)
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


def test_total_energy_is_locally_su2_gauge_invariant():
    rng = np.random.default_rng(1502)
    shape = (2,2,2)
    psi = (
        rng.normal(size=shape + (2,))
        + 1j*rng.normal(size=shape + (2,))
    )
    momentum = (
        rng.normal(size=shape + (2,))
        + 1j*rng.normal(size=shape + (2,))
    )
    links = identity_links(shape)
    electric = rng.normal(
        scale=0.1,
        size=(3,) + shape + (3,),
    )
    transforms = random_site_gauge_transform(
        shape,
        rng,
    )

    params = SU2ScalarMatterParameters(
        mass2=0.7,
        lambda4=0.2,
    )

    e0 = total_energy(
        psi,momentum,links,electric,0.5,params
    )

    p2,m2,l2,e2 = gauge_transform_state(
        psi,
        momentum,
        links,
        electric,
        transforms,
    )

    e1 = total_energy(
        p2,m2,l2,e2,0.5,params
    )

    assert math.isclose(
        e0,e1,
        rel_tol=0,
        abs_tol=1e-9,
    )


def test_coupled_evolution_preserves_gauss_from_zero_charge_initial_state():
    shape = (2,2,2)
    links = identity_links(shape)

    # Spatially varying real doublet, zero momentum: rho_a=0 initially.
    psi = np.zeros(shape + (2,), dtype=complex)
    for idx in np.ndindex(shape):
        psi[idx] = np.array(
            [
                0.02*(1+idx[0]),
                0.015*(1+idx[1]),
            ],
            dtype=complex,
        )

    momentum = np.zeros_like(psi)
    electric = np.zeros((3,) + shape + (3,))

    state = SU2MatterGaugeDynamics(
        psi,
        momentum,
        links,
        electric,
        beta=0.3,
        matter_params=SU2ScalarMatterParameters(
            mass2=0.5,
            lambda4=0.1,
        ),
    )

    assert state.max_gauss == 0.0
    e0 = state.energy

    for _ in range(100):
        state.step(0.001)

    assert state.max_gauss < 2e-8
    assert abs(state.energy-e0)/e0 < 2e-5
