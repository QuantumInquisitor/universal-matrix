import math
import numpy as np

from src.su2_lattice_gauge import (
    IDENTITY2,
    gauge_transform,
    identity_links,
    is_su2,
    plaquette,
    random_links,
    random_site_gauge_transform,
    random_su2,
    wilson_action,
)


def test_random_su2_matrices_are_unitary_with_unit_determinant():
    rng = np.random.default_rng(501)
    for _ in range(20):
        assert is_su2(random_su2(rng))


def test_identity_configuration_has_zero_wilson_action():
    links = identity_links((2, 2, 2))
    assert wilson_action(links, beta=1.3) == 0.0


def test_plaquette_of_su2_links_is_su2():
    rng = np.random.default_rng(502)
    links = random_links((2, 2, 2), rng)
    p = plaquette(links, (0, 1, 1), 0, 2)
    assert is_su2(p, tolerance=1e-11)


def test_wilson_action_is_locally_gauge_invariant():
    rng = np.random.default_rng(503)
    shape = (2, 2, 2)
    links = random_links(shape, rng)
    transforms = random_site_gauge_transform(shape, rng)

    s0 = wilson_action(links, beta=0.9)
    transformed = gauge_transform(links, transforms)
    s1 = wilson_action(transformed, beta=0.9)

    assert math.isclose(s0, s1, rel_tol=0, abs_tol=1e-11)


def test_identity_links_transform_to_pure_gauge_with_zero_action():
    rng = np.random.default_rng(504)
    shape = (2, 2, 2)
    links = identity_links(shape)
    transforms = random_site_gauge_transform(shape, rng)
    transformed = gauge_transform(links, transforms)

    assert math.isclose(
        wilson_action(transformed),
        0.0,
        rel_tol=0,
        abs_tol=1e-11,
    )


def test_global_constant_gauge_rotation_conjugates_plaquette():
    rng = np.random.default_rng(505)
    shape = (2, 2, 2)
    links = random_links(shape, rng)
    g = random_su2(rng)
    transforms = np.empty(shape + (2, 2), dtype=complex)
    transforms[...] = g

    p0 = plaquette(links, (0, 0, 0), 0, 1)
    p1 = plaquette(
        gauge_transform(links, transforms),
        (0, 0, 0),
        0,
        1,
    )
    expected = g @ p0 @ g.conj().T

    assert np.allclose(p1, expected, atol=1e-11, rtol=0)
    assert np.allclose(g.conj().T @ g, IDENTITY2, atol=1e-12, rtol=0)
