import math
import numpy as np

from src.su2_lattice_gauge import (
    gauge_transform,
    random_links,
    random_site_gauge_transform,
)
from src.su2_matter_doublet import (
    SU2MatterPotential,
    covariant_forward_difference,
    gauge_invariant_norm,
    gauge_transform_matter,
    matter_density,
    total_matter_energy,
)


def _random_doublet(shape, rng):
    return (
        rng.normal(size=shape + (2,))
        + 1j * rng.normal(size=shape + (2,))
    )


def test_doublet_norm_is_locally_gauge_invariant():
    rng = np.random.default_rng(601)
    shape = (2, 2, 2)
    psi = _random_doublet(shape, rng)
    g = random_site_gauge_transform(shape, rng)

    psi2 = gauge_transform_matter(psi, g)

    assert np.allclose(
        matter_density(psi),
        matter_density(psi2),
        atol=1e-11,
        rtol=0,
    )
    assert math.isclose(
        gauge_invariant_norm(psi),
        gauge_invariant_norm(psi2),
        abs_tol=1e-11,
    )


def test_covariant_difference_transforms_as_doublet():
    rng = np.random.default_rng(602)
    shape = (2, 2, 2)
    psi = _random_doublet(shape, rng)
    links = random_links(shape, rng)
    g = random_site_gauge_transform(shape, rng)

    psi2 = gauge_transform_matter(psi, g)
    links2 = gauge_transform(links, g)

    d0 = covariant_forward_difference(psi, links, axis=1)
    d1 = covariant_forward_difference(psi2, links2, axis=1)

    for idx in np.ndindex(shape):
        expected = g[idx] @ d0[idx]
        assert np.allclose(d1[idx], expected, atol=1e-10, rtol=0)


def test_total_matter_energy_is_locally_gauge_invariant():
    rng = np.random.default_rng(603)
    shape = (2, 2, 2)
    psi = _random_doublet(shape, rng)
    links = random_links(shape, rng)
    g = random_site_gauge_transform(shape, rng)

    potential = SU2MatterPotential(
        mass2=0.7,
        lambda4=0.2,
    )

    e0 = total_matter_energy(psi, links, potential)
    e1 = total_matter_energy(
        gauge_transform_matter(psi, g),
        gauge_transform(links, g),
        potential,
    )

    assert math.isclose(e0, e1, rel_tol=0, abs_tol=1e-10)


def test_zero_doublet_has_zero_energy():
    shape = (2, 2, 2)
    psi = np.zeros(shape + (2,), dtype=complex)
    links = random_links(shape, np.random.default_rng(604))
    assert total_matter_energy(psi, links) == 0.0
