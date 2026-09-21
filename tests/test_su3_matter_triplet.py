import math
import numpy as np

from src.su3_lattice_gauge import (
    gauge_transform,
    random_links,
    random_site_gauge_transform,
)
from src.su3_matter_triplet import (
    SU3MatterPotential,
    covariant_forward_difference,
    gauge_invariant_norm,
    gauge_transform_matter,
    matter_density,
    total_matter_energy,
)


def _random_triplet(shape, rng):
    return (
        rng.normal(size=shape + (3,))
        + 1j*rng.normal(size=shape + (3,))
    )


def test_triplet_density_is_locally_gauge_invariant():
    rng = np.random.default_rng(801)
    shape = (2,2,2)
    psi = _random_triplet(shape, rng)
    g = random_site_gauge_transform(shape, rng)
    psi2 = gauge_transform_matter(psi, g)

    assert np.allclose(
        matter_density(psi),
        matter_density(psi2),
        atol=1e-10,
        rtol=0,
    )
    assert math.isclose(
        gauge_invariant_norm(psi),
        gauge_invariant_norm(psi2),
        abs_tol=1e-10,
    )


def test_covariant_difference_transforms_as_triplet():
    rng = np.random.default_rng(802)
    shape = (2,2,2)
    psi = _random_triplet(shape, rng)
    links = random_links(shape, rng)
    g = random_site_gauge_transform(shape, rng)

    psi2 = gauge_transform_matter(psi, g)
    links2 = gauge_transform(links, g)

    d0 = covariant_forward_difference(psi, links, axis=2)
    d1 = covariant_forward_difference(psi2, links2, axis=2)

    for idx in np.ndindex(shape):
        assert np.allclose(
            d1[idx],
            g[idx] @ d0[idx],
            atol=1e-10,
            rtol=0,
        )


def test_total_triplet_energy_is_locally_gauge_invariant():
    rng = np.random.default_rng(803)
    shape = (2,2,2)
    psi = _random_triplet(shape, rng)
    links = random_links(shape, rng)
    g = random_site_gauge_transform(shape, rng)

    potential = SU3MatterPotential(
        mass2=0.8,
        lambda4=0.15,
    )

    e0 = total_matter_energy(psi, links, potential)
    e1 = total_matter_energy(
        gauge_transform_matter(psi, g),
        gauge_transform(links, g),
        potential,
    )

    assert math.isclose(e0, e1, rel_tol=0, abs_tol=1e-9)


def test_zero_triplet_has_zero_energy():
    shape = (2,2,2)
    psi = np.zeros(shape + (3,), dtype=complex)
    links = random_links(shape, np.random.default_rng(804))
    assert total_matter_energy(psi, links) == 0.0
