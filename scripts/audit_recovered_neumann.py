"""Audit the historical candidate against independently assembled graph equations.

Pass the trusted recovered Python source explicitly; this script does not fetch
or modify it. The report records both numerical successes and rejection gaps.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import warnings
from pathlib import Path

import numpy as np


def load_candidate(path):
    spec = importlib.util.spec_from_file_location("recovered_neumann", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def face_arrays(shape):
    return {
        f"{axis}_{sign}": np.zeros(tuple(n for j, n in enumerate(shape) if j != i))
        for i, axis in enumerate("xyz")
        for sign in ("neg", "pos")
    }


def independent_system(shape, faces):
    """Enumerate physical links/faces without the candidate's stencil helpers."""
    count = int(np.prod(shape))
    laplacian = np.zeros((count, count))
    boundary = np.zeros(count)
    for cell in np.ndindex(shape):
        row = int(np.ravel_multi_index(cell, shape))
        for axis, name in enumerate("xyz"):
            face_index = tuple(n for j, n in enumerate(cell) if j != axis)
            if cell[axis] == 0:
                boundary[row] += faces[f"{name}_neg"][face_index]
            if cell[axis] == shape[axis] - 1:
                boundary[row] += faces[f"{name}_pos"][face_index]
            if cell[axis] + 1 < shape[axis]:
                neighbor = list(cell)
                neighbor[axis] += 1
                col = int(np.ravel_multi_index(tuple(neighbor), shape))
                laplacian[row, row] += 1
                laplacian[col, col] += 1
                laplacian[row, col] -= 1
                laplacian[col, row] -= 1
    return laplacian, boundary


def audit(path):
    candidate = load_candidate(path)
    rng = np.random.default_rng(20260930)
    numerical = []
    for shape in ((2, 3, 4), (3, 4, 5), (4, 4, 4)):
        faces = {k: rng.normal(size=v.shape) for k, v in face_arrays(shape).items()}
        matrix, boundary = independent_system(shape, faces)
        expected = rng.normal(size=int(np.prod(shape)))
        expected -= expected.mean()
        rho = (matrix @ expected + boundary).reshape(shape)
        solution = candidate.solve_open_gauss_with_face_flux(rho, faces, tolerance=1e-12)
        actual = solution.potential.ravel()
        direct = np.linalg.lstsq(
            np.vstack([matrix, np.ones(len(expected))]),
            np.append(rho.ravel() - boundary, 0),
            rcond=None,
        )[0]
        potential_error = float(np.max(np.abs(actual - expected)))
        direct_error = float(np.max(np.abs(actual - direct)))
        residual = float(np.max(np.abs(matrix @ actual + boundary - rho.ravel())))
        energy_error = abs(solution.field_energy() - float(actual @ matrix @ actual / 2))
        numerical.append(
            {
                "shape": list(shape),
                "potential_error": potential_error,
                "direct_solve_error": direct_error,
                "independent_gauss_residual": residual,
                "energy_identity_error": energy_error,
                "passed": bool(max(potential_error, direct_error, residual, energy_error) < 1e-9),
            }
        )

    shape = (3, 4, 5)
    zero = np.zeros(shape)
    faces = face_arrays(shape)
    rejection = []
    cases = [
        ("nan_tolerance", zero, faces, {"tolerance": float("nan")}),
        ("infinite_tolerance", zero, faces, {"tolerance": float("inf")}),
        ("fractional_iteration_limit", zero, faces, {"max_iterations": 1.5}),
        ("boolean_iteration_limit", zero, faces, {"max_iterations": True}),
        ("complex_source", zero.astype(complex) + 1j, faces, {}),
        ("complex_face", zero, {**faces, "x_pos": faces["x_pos"].astype(complex) + 1j}, {}),
    ]
    for name, rho, boundary, options in cases:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                candidate.solve_open_gauss_with_face_flux(rho, boundary, **options)
                rejected, exception = False, None
            except (ValueError, TypeError) as exc:
                rejected, exception = True, type(exc).__name__
            except Exception as exc:
                rejected, exception = False, type(exc).__name__
        rejection.append(
            {
                "case": name,
                "rejected_at_input": rejected,
                "exception": exception,
                "warnings": [str(w.message) for w in caught],
            }
        )
    return {
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "seed": 20260930,
        "scope": "Finite dimensionless graph controls, not continuum or material validation",
        "numerical_cases": numerical,
        "invalid_input_cases": rejection,
        "numerical_pass": all(r["passed"] for r in numerical),
        "input_rejection_pass": all(r["rejected_at_input"] for r in rejection),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.candidate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
