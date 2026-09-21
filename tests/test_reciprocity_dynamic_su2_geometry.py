import math
import numpy as np

from src.reciprocity_dynamic_su2_geometry import (
    SU2DynamicReciprocityReference,
    geometry_rhs,
    total_energy,
    weighted_group_force_reference,
    weighted_magnetic_energy,
)
from src.reciprocity_nonabelian_spatial_geometry import (
    local_geometry_source,
)
from src.su2_hamiltonian_reference import su2_exp
from src.su2_lattice_gauge import identity_links


def test_geometry_source_matches_total_energy_psi_derivative():
    shape=(2,2,2)
    links=identity_links(shape)
    electric=np.zeros((3,)+shape+(3,))
    electric[0,...,0]=0.2
    psi=np.zeros(shape)
    p=np.zeros(shape)
    kappa=0.7
    beta=0.4

    _,pdot=geometry_rhs(
        psi,p,links,electric,kappa,beta
    )
    source=local_geometry_source(
        links,electric,psi,beta,2
    )

    # With psi=0 and P=0 and spatially uniform psi, only the gauge source remains.
    assert np.allclose(
        pdot,
        source,
        atol=1e-14,
        rtol=0,
    )


def test_weighted_group_force_matches_magnetic_energy_derivative():
    shape=(1,1,1)
    links=identity_links(shape)
    links[0,0,0,0]=su2_exp(
        np.array([0.03,-0.02,0.01])
    )
    psi=np.array([[[0.2]]])
    beta=0.5
    eps=1e-7

    force=weighted_group_force_reference(
        links,psi,beta,epsilon=eps
    )

    axis=0
    idx=(0,0,0)
    component=1
    direction=np.zeros(3)
    direction[component]=eps

    plus=links.copy()
    minus=links.copy()
    plus[(axis,)+idx]=(
        su2_exp(direction)
        @ links[(axis,)+idx]
    )
    minus[(axis,)+idx]=(
        su2_exp(-direction)
        @ links[(axis,)+idx]
    )

    derivative=(
        weighted_magnetic_energy(
            plus,psi,beta
        )
        - weighted_magnetic_energy(
            minus,psi,beta
        )
    )/(2*eps)

    assert math.isclose(
        force[(axis,)+idx+(component,)],
        -derivative,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )


def test_zero_field_zero_geometry_is_stationary():
    shape=(1,1,1)
    state=SU2DynamicReciprocityReference(
        psi=np.zeros(shape),
        psi_momentum=np.zeros(shape),
        links=identity_links(shape),
        electric=np.zeros((3,)+shape+(3,)),
        kappa=0.8,
        beta=0.4,
    )

    e0=state.energy
    state.step(0.01)

    assert e0 == 0.0
    assert state.energy == 0.0
    assert np.all(state.psi == 0.0)
    assert np.all(state.psi_momentum == 0.0)


def test_small_coupled_geometry_gauge_step_has_small_energy_drift():
    shape=(1,1,1)
    links=identity_links(shape)
    links[0,0,0,0]=su2_exp(
        np.array([0.04,0.01,-0.02])
    )
    links[1,0,0,0]=su2_exp(
        np.array([-0.02,0.03,0.01])
    )

    state=SU2DynamicReciprocityReference(
        psi=np.array([[[0.05]]]),
        psi_momentum=np.array([[[0.01]]]),
        links=links,
        electric=np.zeros((3,)+shape+(3,)),
        kappa=0.6,
        beta=0.3,
        force_epsilon=2e-6,
    )

    e0=state.energy
    for _ in range(20):
        state.step(0.0005)

    assert e0 > 0.0
    assert abs(state.energy-e0)/e0 < 5e-4
