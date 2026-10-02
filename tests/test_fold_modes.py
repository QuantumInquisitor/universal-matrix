"""Independent modal eigenproblem and nonlinear small-amplitude limits."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0, STIFFNESS, rhs
from scripts.report_fold_modes import compare, linear_modes


def test_generalized_eigenpairs_and_mass_orthogonality():
    mass, omega, shapes = linear_modes()
    assert np.all(omega > 0)
    np.testing.assert_allclose(STIFFNESS @ shapes, mass @ shapes @ np.diag(omega**2), atol=1e-15)
    assert abs(shapes[:, 0] @ mass @ shapes[:, 1]) < 1e-17
    # Independent characteristic invariants of M^-1 K.
    dynamic = np.linalg.solve(mass, STIFFNESS)
    assert sum(omega**2) == pytest.approx(np.trace(dynamic), rel=1e-13)
    assert np.prod(omega**2) == pytest.approx(np.linalg.det(dynamic), rel=1e-13)


def test_independent_equilibrium_dynamics_jacobian():
    mass, _, _ = linear_modes()
    equilibrium = np.r_[Q0, 0.0, 0.0, 0.0, 0.0]
    jacobian = np.empty((4, 4))
    for column in range(4):
        perturbation = np.zeros(6)
        perturbation[column] = 1e-6
        jacobian[:, column] = (
            rhs(0, equilibrium + perturbation, damping=0)[:4]
            - rhs(0, equilibrium - perturbation, damping=0)[:4]
        ) / 2e-6
    expected = np.block(
        [[np.zeros((2, 2)), np.eye(2)], [-np.linalg.solve(mass, STIFFNESS), np.zeros((2, 2))]]
    )
    np.testing.assert_allclose(jacobian, expected, atol=2e-9, rtol=0)


@pytest.mark.parametrize("mode", [0, 1])
def test_linearized_modal_motion_conserves_frozen_mass_energy(mode):
    mass, omega, shapes = linear_modes()
    a = 0.01 * shapes[:, mode]
    energies = []
    for t in np.linspace(0, 10, 31):
        x = a * np.cos(omega[mode] * t)
        velocity = -a * omega[mode] * np.sin(omega[mode] * t)
        energies.append((velocity @ mass @ velocity + x @ STIFFNESS @ x) / 2)
    np.testing.assert_allclose(energies, energies[0], rtol=1e-14, atol=0)


@pytest.mark.parametrize("mode", [0, 1])
def test_nonlinear_discrepancy_reduces_with_amplitude(mode):
    coarse = compare(mode, 0.02, duration=0.8)
    fine = compare(mode, 0.01, duration=0.8)
    for field in ("max_scale_error", "max_angle_error_rad"):
        assert 3 < coarse[field] / fine[field] < 5
    assert fine["maximum_balance_residual_j"] < 1e-13


@pytest.mark.parametrize(
    "mode,amplitude",
    [
        (2, 0.01),
        (True, 0.01),
        (0, 0),
        (0, -0.01),
        (0, 0.1),
        (0, float("nan")),
        (0, np.bool_(True)),
        (0, "0.01"),
        (0, 1j),
        (0, 10**400),
    ],
)
def test_invalid_mode_or_amplitude(mode, amplitude):
    with pytest.raises(ValueError):
        compare(mode, amplitude)
