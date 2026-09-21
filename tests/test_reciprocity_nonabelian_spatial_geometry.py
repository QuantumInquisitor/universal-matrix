import math
import numpy as np

from src.reciprocity_nonabelian_spatial_geometry import (
    link_weight,
    local_geometry_source,
    plaquette_weight,
    source_sum_identity_residual,
    weighted_su2_energy,
    weighted_su3_energy,
)
from src.su2_lattice_gauge import (
    gauge_transform as su2_gauge_transform,
    random_links as su2_random_links,
    random_site_gauge_transform as su2_random_gauge,
    wilson_action as su2_wilson_action,
)
from src.su3_lattice_gauge import (
    gauge_transform as su3_gauge_transform,
    random_links as su3_random_links,
    random_site_gauge_transform as su3_random_gauge,
    wilson_action as su3_wilson_action,
)


def test_uniform_geometry_weights_reduce_to_exp_minus_two_psi():
    psi = np.full((2,2,2), 0.37)
    expected = math.exp(-0.74)

    for axis in range(3):
        assert np.allclose(
            link_weight(psi, axis),
            expected,
            atol=1e-15,
            rtol=0,
        )

    assert np.allclose(
        plaquette_weight(psi, 0, 1),
        expected,
        atol=1e-15,
        rtol=0,
    )


def test_uniform_su2_weighted_energy_matches_scaled_flat_energy():
    rng = np.random.default_rng(1701)
    shape=(2,2,2)
    links=su2_random_links(shape,rng)
    electric=rng.normal(scale=0.2,size=(3,)+shape+(3,))
    psi0=0.21
    psi=np.full(shape,psi0)
    beta=0.6

    flat = (
        0.5*float(np.sum(electric**2))
        + su2_wilson_action(links,beta)
    )
    curved = weighted_su2_energy(
        links,electric,psi,beta
    )

    assert math.isclose(
        curved,
        math.exp(-2*psi0)*flat,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_uniform_su3_weighted_energy_matches_scaled_flat_energy():
    rng = np.random.default_rng(1702)
    shape=(1,1,1)
    links=su3_random_links(shape,rng)
    electric=rng.normal(scale=0.2,size=(3,)+shape+(8,))
    psi0=-0.17
    psi=np.full(shape,psi0)
    beta=0.5

    flat = (
        0.5*float(np.sum(electric**2))
        + su3_wilson_action(links,beta)
    )
    curved = weighted_su3_energy(
        links,electric,psi,beta
    )

    assert math.isclose(
        curved,
        math.exp(-2*psi0)*flat,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_spatially_weighted_su2_energy_is_gauge_invariant():
    rng=np.random.default_rng(1703)
    shape=(2,2,2)
    links=su2_random_links(shape,rng)
    electric=np.zeros((3,)+shape+(3,))
    psi=rng.normal(scale=0.3,size=shape)
    g=su2_random_gauge(shape,rng)

    e0=weighted_su2_energy(
        links,electric,psi,0.7
    )
    e1=weighted_su2_energy(
        su2_gauge_transform(links,g),
        electric,
        psi,
        0.7,
    )

    assert math.isclose(
        e0,e1,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_spatially_weighted_su3_energy_is_gauge_invariant():
    rng=np.random.default_rng(1704)
    shape=(1,1,1)
    links=su3_random_links(shape,rng)
    electric=np.zeros((3,)+shape+(8,))
    psi=rng.normal(scale=0.3,size=shape)
    g=su3_random_gauge(shape,rng)

    e0=weighted_su3_energy(
        links,electric,psi,0.4
    )
    e1=weighted_su3_energy(
        su3_gauge_transform(links,g),
        electric,
        psi,
        0.4,
    )

    assert math.isclose(
        e0,e1,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_local_source_sum_is_exactly_twice_weighted_su2_energy():
    rng=np.random.default_rng(1705)
    shape=(2,2,2)
    links=su2_random_links(shape,rng)
    electric=rng.normal(scale=0.2,size=(3,)+shape+(3,))
    psi=rng.normal(scale=0.25,size=shape)

    residual=source_sum_identity_residual(
        links,electric,psi,0.5,2
    )
    assert abs(residual) < 1e-10


def test_local_source_sum_is_exactly_twice_weighted_su3_energy():
    rng=np.random.default_rng(1706)
    shape=(1,1,1)
    links=su3_random_links(shape,rng)
    electric=rng.normal(scale=0.2,size=(3,)+shape+(8,))
    psi=rng.normal(scale=0.25,size=shape)

    residual=source_sum_identity_residual(
        links,electric,psi,0.5,3
    )
    assert abs(residual) < 1e-10


def test_local_geometry_source_matches_finite_difference_site_derivative():
    rng=np.random.default_rng(1707)
    shape=(2,2,2)
    links=su2_random_links(shape,rng)
    electric=rng.normal(scale=0.1,size=(3,)+shape+(3,))
    psi=rng.normal(scale=0.2,size=shape)
    beta=0.4

    source=local_geometry_source(
        links,electric,psi,beta,2
    )

    idx=(1,0,1)
    eps=1e-7
    plus=psi.copy()
    minus=psi.copy()
    plus[idx]+=eps
    minus[idx]-=eps

    derivative=(
        weighted_su2_energy(
            links,electric,plus,beta
        )
        - weighted_su2_energy(
            links,electric,minus,beta
        )
    )/(2*eps)

    assert math.isclose(
        source[idx],
        -derivative,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )
