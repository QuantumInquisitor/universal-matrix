import numpy as np

from src.reciprocity_dynamic_su2_geometry import (
    weighted_group_force_reference,
)
from src.reciprocity_dynamic_su2_geometry_optimized import (
    SU2DynamicReciprocity,
    analytic_weighted_force,
)
from src.su2_hamiltonian_reference import su2_exp
from src.su2_lattice_gauge import random_links


def test_weighted_analytic_force_matches_reference():
    rng=np.random.default_rng(1801)
    shape=(2,2,2)
    links=random_links(shape,rng)
    psi=rng.normal(scale=0.2,size=shape)
    beta=0.57

    analytic=analytic_weighted_force(
        links,psi,beta
    )
    reference=weighted_group_force_reference(
        links,psi,beta,epsilon=2e-6
    )

    assert np.allclose(
        analytic,
        reference,
        atol=3e-8,
        rtol=3e-8,
    )


def test_optimized_dynamic_geometry_has_small_energy_drift():
    shape=(1,1,1)
    links=np.empty(
        (3,)+shape+(2,2),
        dtype=complex,
    )
    links[0,0,0,0]=su2_exp(
        np.array([0.04,0.01,-0.02])
    )
    links[1,0,0,0]=su2_exp(
        np.array([-0.02,0.03,0.01])
    )
    links[2,0,0,0]=su2_exp(
        np.array([0.01,-0.01,0.02])
    )

    state=SU2DynamicReciprocity(
        psi=np.array([[[0.05]]]),
        psi_momentum=np.array([[[0.01]]]),
        links=links,
        electric=np.zeros((3,)+shape+(3,)),
        kappa=0.6,
        beta=0.3,
    )

    e0=state.energy
    for _ in range(100):
        state.step(0.0002)

    assert e0>0.0
    assert abs(state.energy-e0)/e0 < 4e-4
