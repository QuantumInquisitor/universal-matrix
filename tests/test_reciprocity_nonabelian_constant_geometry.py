import math
import numpy as np

from src.reciprocity_nonabelian_constant_geometry import (
    SU2ReciprocityBackground,
    SU3ReciprocityBackground,
    geometry_active_source_from_energy,
    geometry_weight,
    metric_null_coordinate_speed,
    yang_mills_characteristic_speed,
)
from src.su2_hamiltonian import SU2Hamiltonian
from src.su2_hamiltonian_reference import su2_exp
from src.su3_hamiltonian import SU3Hamiltonian, su3_exp


def test_nonabelian_characteristic_speed_matches_metric_null_speed():
    for psi in (-0.5,0.0,0.3,0.9):
        assert math.isclose(
            yang_mills_characteristic_speed(psi),
            metric_null_coordinate_speed(psi),
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_geometry_source_is_twice_free_gauge_energy():
    energy = 3.7
    assert geometry_active_source_from_energy(energy) == 7.4


def test_su2_uniform_geometry_step_equals_flat_step_at_rescaled_time():
    shape=(1,1,1)
    links=np.empty((3,)+shape+(2,2),dtype=complex)
    for axis in range(3):
        links[axis,0,0,0]=su2_exp(
            np.array([0.03*(axis+1),-0.02,0.01])
        )
    electric=np.zeros((3,)+shape+(3,))
    psi=0.4
    dt=0.002
    w=geometry_weight(psi)

    curved=SU2ReciprocityBackground(
        links.copy(),electric.copy(),beta=0.4,psi=psi
    )
    flat=SU2Hamiltonian(
        links.copy(),electric.copy(),beta=0.4
    )

    curved.step(dt)
    flat.step(dt*w)

    assert np.allclose(curved.links,flat.links,atol=1e-12,rtol=0)
    assert np.allclose(curved.electric,flat.electric,atol=1e-12,rtol=0)


def test_su3_uniform_geometry_step_equals_flat_step_at_rescaled_time():
    shape=(1,1,1)
    links=np.empty((3,)+shape+(3,3),dtype=complex)
    for axis in range(3):
        vector=np.zeros(8)
        vector[axis]=0.04
        vector[7]=0.01
        links[axis,0,0,0]=su3_exp(vector)
    electric=np.zeros((3,)+shape+(8,))
    psi=-0.2
    dt=0.001
    w=geometry_weight(psi)

    curved=SU3ReciprocityBackground(
        links.copy(),electric.copy(),beta=0.3,psi=psi
    )
    flat=SU3Hamiltonian(
        links.copy(),electric.copy(),beta=0.3
    )

    curved.step(dt)
    flat.step(dt*w)

    assert np.allclose(curved.links,flat.links,atol=2e-12,rtol=0)
    assert np.allclose(curved.electric,flat.electric,atol=2e-12,rtol=0)
