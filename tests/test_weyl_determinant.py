import math

import numpy as np

from src.u1_overlap_dirac_lattice import (
    gamma5_lattice,
)
from src.weyl_determinant import (
    basis_rotation_prediction,
    determinant_basis_covariance_residual,
    determinant_if_square,
    determinant_magnitude_basis_residual,
    ordinary_chiral_basis,
    rotated_weyl_matrix,
    u1_overlap_weyl_matrix,
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
    mask = np.abs(diagonal) > 0
    phases[mask] = diagonal[mask] / np.abs(diagonal[mask])
    return q @ np.diag(np.conj(phases))


def test_ordinary_chiral_basis_has_requested_gamma5_eigenvalue():
    shape = (2, 2, 1, 1)
    g5 = gamma5_lattice(shape)

    for chirality in (-1, 1):
        basis = ordinary_chiral_basis(
            shape,
            chirality=chirality,
        )
        assert np.allclose(
            g5 @ basis,
            chirality * basis,
            atol=1e-12,
            rtol=0,
        )
        assert np.allclose(
            basis.conj().T @ basis,
            np.eye(basis.shape[1]),
            atol=1e-12,
            rtol=0,
        )


def test_u1_overlap_weyl_block_is_square_in_trivial_index_sector():
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(2401)
    links = rng.normal(
        scale=0.025,
        size=(4,) + shape,
    )

    matrix, right, barred = u1_overlap_weyl_matrix(
        links,
        chirality=-1,
        rho=1.0,
    )

    assert matrix.shape[0] == matrix.shape[1]
    assert matrix.shape[1] == right.shape[1]
    assert matrix.shape[0] == barred.shape[1]


def test_determinant_basis_covariance_is_exact():
    rng = np.random.default_rng(2402)
    matrix = (
        rng.normal(size=(5, 5))
        + 1j * rng.normal(size=(5, 5))
    )
    ur = _random_unitary(5, 2403)
    ub = _random_unitary(5, 2404)

    residual = determinant_basis_covariance_residual(
        matrix,
        ur,
        ub,
    )
    scale = max(1.0, abs(np.linalg.det(matrix)))
    assert abs(residual) / scale < 1e-11


def test_determinant_magnitude_is_basis_independent():
    rng = np.random.default_rng(2405)
    matrix = (
        rng.normal(size=(4, 4))
        + 1j * rng.normal(size=(4, 4))
    )
    ur = _random_unitary(4, 2406)
    ub = _random_unitary(4, 2407)

    residual = determinant_magnitude_basis_residual(
        matrix,
        ur,
        ub,
    )
    assert abs(residual) < 1e-11


def test_determinant_phase_changes_by_basis_determinant_phases():
    rng = np.random.default_rng(2408)
    matrix = (
        rng.normal(size=(3, 3))
        + 1j * rng.normal(size=(3, 3))
    )

    theta_r = 0.37
    theta_b = -0.21
    ur = np.eye(3, dtype=complex)
    ub = np.eye(3, dtype=complex)
    ur[0, 0] = np.exp(1j * theta_r)
    ub[0, 0] = np.exp(1j * theta_b)

    original = determinant_if_square(matrix)
    rotated = determinant_if_square(
        rotated_weyl_matrix(
            matrix,
            ur,
            ub,
        )
    )
    predicted = basis_rotation_prediction(
        original,
        ur,
        ub,
    )

    assert abs(rotated - predicted) < 1e-11

    measured_phase_shift = np.angle(rotated / original)
    expected_phase_shift = theta_r - theta_b
    wrapped = (
        measured_phase_shift
        - expected_phase_shift
        + math.pi
    ) % (2.0 * math.pi) - math.pi
    assert abs(wrapped) < 1e-12


def test_rectangular_weyl_block_rejects_determinant():
    matrix = np.zeros((3, 4), dtype=complex)
    try:
        determinant_if_square(matrix)
    except ValueError:
        pass
    else:
        raise AssertionError("rectangular Weyl block should not have determinant")
