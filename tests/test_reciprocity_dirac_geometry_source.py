import math
import numpy as np

from src.reciprocity_dirac_geometry_source import (
    analytic_geometry_source,
    analytic_reference_residual,
    dirac_energy,
    local_geometry_source_reference,
    rest_mode_source_energy,
    source_sum_residual,
    uniform_geometry_source_sum,
)


def test_rest_dirac_mode_source_equals_energy():
    source,energy=rest_mode_source_energy(
        amplitude=0.7+0.2j,
        mass=1.3,
        psi=0.4,
    )
    assert math.isclose(source,energy,rel_tol=0,abs_tol=1e-15)


def test_local_source_sums_to_uniform_geometry_derivative():
    rng=np.random.default_rng(1701)
    shape=(2,2,2)
    spinor=(
        rng.normal(scale=0.05,size=shape+(4,))
        +1j*rng.normal(scale=0.05,size=shape+(4,))
    )
    psi=rng.normal(scale=0.1,size=shape)

    residual=source_sum_residual(
        spinor,
        psi,
        mass=0.8,
        epsilon=2e-6,
    )
    assert abs(residual)<2e-8


def test_uniform_source_matches_explicit_uniform_shift():
    shape=(2,2,2)
    spinor=np.zeros(shape+(4,),dtype=complex)
    spinor[...,0]=0.1
    psi_value=0.2

    source=uniform_geometry_source_sum(
        spinor,
        psi_value,
        mass=1.0,
        epsilon=1e-6,
    )

    eps=1e-6
    plus=np.full(shape,psi_value+eps)
    minus=np.full(shape,psi_value-eps)
    explicit=-(
        dirac_energy(spinor,plus,1.0)
        -dirac_energy(spinor,minus,1.0)
    )/(2*eps)

    assert math.isclose(source,explicit,rel_tol=0,abs_tol=1e-12)


def test_positive_uniform_rest_spinor_has_positive_geometry_source():
    shape=(2,2,2)
    spinor=np.zeros(shape+(4,),dtype=complex)
    spinor[...,0]=0.05
    psi=np.zeros(shape)

    source=local_geometry_source_reference(
        spinor,
        psi,
        mass=1.2,
        epsilon=1e-6,
    )

    assert np.all(source>0)


def test_analytic_source_matches_finite_difference_oracle():
    rng=np.random.default_rng(1702)
    shape=(3,3,3)
    spinor=(
        rng.normal(scale=0.08,size=shape+(4,))
        +1j*rng.normal(scale=0.08,size=shape+(4,))
    )
    psi=rng.normal(scale=0.15,size=shape)

    analytic=analytic_geometry_source(
        spinor,
        psi,
        mass=0.9,
        spacing=0.7,
    )
    reference=local_geometry_source_reference(
        spinor,
        psi,
        mass=0.9,
        spacing=0.7,
        epsilon=2e-6,
    )

    assert np.allclose(
        analytic,
        reference,
        atol=3e-8,
        rtol=0,
    )


def test_analytic_residual_helper_is_small():
    rng=np.random.default_rng(1703)
    shape=(2,3,2)
    spinor=(
        rng.normal(scale=0.05,size=shape+(4,))
        +1j*rng.normal(scale=0.05,size=shape+(4,))
    )
    psi=rng.normal(scale=0.1,size=shape)

    residual=analytic_reference_residual(
        spinor,
        psi,
        mass=1.1,
        spacing=1.0,
        epsilon=2e-6,
    )
    assert residual<2e-8
