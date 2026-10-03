from pathlib import Path

import numpy as np
import pytest

from scripts.audit_recovered_neumann import audit, face_arrays
from src.open_boundary_solver import solve_open_gauss_with_face_flux


@pytest.fixture(scope="module")
def report():
    return audit(Path(__file__).resolve().parents[1] / "src/open_boundary_solver.py")


@pytest.mark.parametrize("case", range(3))
def test_manufactured_state_dense_solve_gauss_and_energy(report, case):
    assert report["numerical_cases"][case]["passed"]


@pytest.mark.parametrize("case", range(6))
def test_reject_invalid_inputs_before_solving(report, case):
    record = report["invalid_input_cases"][case]
    assert record["rejected_at_input"], record
    assert record["warnings"] == []


def test_nonconvergence_does_not_return_a_solution():
    rho = np.zeros((4, 5, 6))
    rho[1, 1, 1], rho[2, 3, 4] = 1.0, -1.0
    with pytest.raises(RuntimeError, match="did not converge"):
        solve_open_gauss_with_face_flux(rho, face_arrays(rho.shape), max_iterations=1)


def test_prescribed_faces_are_copied():
    rho = np.zeros((3, 4, 5))
    faces = face_arrays(rho.shape)
    solution = solve_open_gauss_with_face_flux(rho, faces)
    faces["z_pos"][:] = 100
    assert np.all(solution.boundary_flux_density["z_pos"] == 0)
