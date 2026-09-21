import math

import numpy as np

from src.u1_overlap_dirac_lattice import zero_links
from src.weyl_measure_curvature import weyl_basis
from src.weyl_measure_holonomy import (
    closed_loop_holonomy_from_bases,
    closed_loop_measure_phase,
    closed_loop_measure_phase_from_bases,
    holonomy_unitarity_residual,
    polar_unitary,
    principal_phase_difference,
    rectangular_link_loop,
    transport_unitarity_residual,
)


def _random_unitary(n, seed):
    rng = np.random.default_rng(seed)
    z = (
        rng.normal(size=(n, n))
        + 1j * rng.normal(size=(n, n))
    )
    q, r = np.linalg.qr(z)
    diagonal = np.diag(r)
    phases = np.ones_like(diagonal, dtype=complex)
    nonzero = np.abs(diagonal) > 0
    phases[nonzero] = diagonal[nonzero] / np.abs(diagonal[nonzero])
    return q @ np.diag(np.conj(phases))


def _small_link_loop(seed=2101, scale=0.01):
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(seed)
    base = rng.normal(
        scale=0.005,
        size=(4,) + shape,
    )
    da = rng.normal(
        scale=0.1,
        size=(4,) + shape,
    )
    db = rng.normal(
        scale=0.1,
        size=(4,) + shape,
    )
    return rectangular_link_loop(
        base,
        da,
        db,
        side_a=scale,
        side_b=scale,
    )


def test_polar_unitary_is_unitary():
    rng = np.random.default_rng(2102)
    matrix = (
        np.eye(5)
        + 0.05 * rng.normal(size=(5, 5))
        + 0.05j * rng.normal(size=(5, 5))
    )
    q = polar_unitary(matrix)
    assert np.allclose(
        q.conj().T @ q,
        np.eye(5),
        atol=1e-12,
        rtol=0,
    )


def test_neighbor_transport_is_unitary():
    path = _small_link_loop(seed=2103)
    a = weyl_basis(path[0], chirality=-1)
    b = weyl_basis(path[1], chirality=-1)
    assert transport_unitarity_residual(a, b) < 1e-10


def test_closed_loop_holonomy_is_unitary():
    path = _small_link_loop(seed=2104)
    bases = [
        weyl_basis(links, chirality=-1)
        for links in path
    ]
    holonomy = closed_loop_holonomy_from_bases(bases)
    assert holonomy_unitarity_residual(holonomy) < 1e-9


def test_constant_subspace_loop_has_zero_measure_phase():
    links = zero_links((2, 2, 1, 1))
    basis = weyl_basis(links, chirality=-1)
    phase = closed_loop_measure_phase_from_bases(
        [basis, basis.copy(), basis.copy()]
    )
    assert abs(phase) < 1e-12


def test_measure_phase_is_invariant_under_independent_internal_basis_rotations():
    path = _small_link_loop(seed=2105)
    bases = [
        weyl_basis(links, chirality=-1)
        for links in path
    ]
    reference = closed_loop_measure_phase_from_bases(bases)

    rotated = []
    for i, basis in enumerate(bases):
        u = _random_unitary(
            basis.shape[1],
            seed=2200 + i,
        )
        rotated.append(basis @ u)

    transformed = closed_loop_measure_phase_from_bases(rotated)
    assert abs(
        principal_phase_difference(
            transformed,
            reference,
        )
    ) < 1e-9


def test_reversing_loop_reverses_measure_phase():
    path = _small_link_loop(seed=2106, scale=0.015)
    forward = closed_loop_measure_phase(
        path,
        chirality=-1,
    )

    reverse_path = [
        path[0],
        path[3],
        path[2],
        path[1],
    ]
    reverse = closed_loop_measure_phase(
        reverse_path,
        chirality=-1,
    )

    assert abs(
        principal_phase_difference(
            reverse,
            -forward,
        )
    ) < 2e-8


def test_measure_phase_shrinks_for_smaller_rectangular_loop():
    path_large = _small_link_loop(
        seed=2107,
        scale=0.02,
    )
    path_small = _small_link_loop(
        seed=2107,
        scale=0.005,
    )

    phase_large = abs(
        closed_loop_measure_phase(
            path_large,
            chirality=-1,
        )
    )
    phase_small = abs(
        closed_loop_measure_phase(
            path_small,
            chirality=-1,
        )
    )

    # A sufficiently small contractible loop should have holonomy approaching
    # the identity. Allow the trivial case where both phases are essentially
    # zero on this finite test background.
    assert phase_small <= phase_large + 1e-10
    assert phase_small < 5e-3
