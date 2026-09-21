import math
import numpy as np

from src.su3_lattice_gauge import (
    gauge_transform,
    identity_links,
    is_su3,
    plaquette,
    project_to_su3,
    random_links,
    random_site_gauge_transform,
    random_su3,
    wilson_action,
)


def test_projection_produces_su3():
    rng = np.random.default_rng(701)
    for _ in range(10):
        z = rng.normal(size=(3,3)) + 1j*rng.normal(size=(3,3))
        assert is_su3(project_to_su3(z))


def test_random_su3_is_special_unitary():
    rng = np.random.default_rng(702)
    for _ in range(20):
        assert is_su3(random_su3(rng))


def test_identity_links_have_zero_wilson_action():
    links = identity_links((2,2,2))
    assert wilson_action(links, beta=1.4) == 0.0


def test_plaquette_remains_su3():
    rng = np.random.default_rng(703)
    links = random_links((2,2,2), rng)
    p = plaquette(links, (1,0,1), 0, 2)
    assert is_su3(p, tolerance=1e-10)


def test_su3_wilson_action_is_locally_gauge_invariant():
    rng = np.random.default_rng(704)
    shape = (2,2,2)
    links = random_links(shape, rng)
    transforms = random_site_gauge_transform(shape, rng)

    s0 = wilson_action(links, beta=0.8)
    s1 = wilson_action(
        gauge_transform(links, transforms),
        beta=0.8,
    )

    assert math.isclose(s0, s1, rel_tol=0, abs_tol=1e-10)


def test_pure_gauge_transform_of_identity_has_zero_action():
    rng = np.random.default_rng(705)
    shape = (2,2,2)
    links = identity_links(shape)
    transforms = random_site_gauge_transform(shape, rng)
    transformed = gauge_transform(links, transforms)

    assert math.isclose(
        wilson_action(transformed),
        0.0,
        rel_tol=0,
        abs_tol=1e-10,
    )
