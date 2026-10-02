"""Reproduce declared synthetic controls, without historical apparatus claims."""

import argparse
import json
import math
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from src.coupled_lc_reference import CoupledLC


def assert_rejected(**changes):
    try:
        replace(CoupledLC(2.0, 3.0, 0.5, 0.25, 0.8), **changes)
    except ValueError:
        return
    raise AssertionError(f"invalid model accepted: {changes}")


def audit_case(name, model):
    L, K, R = model.matrices()
    roots, v = model.numerical_modes()
    analytic = model.analytic_omega_squared()
    np.testing.assert_allclose(roots, analytic, rtol=2e-13, atol=0)
    np.testing.assert_allclose(v.T @ L @ v, np.eye(2), rtol=2e-13, atol=2e-14)
    equation_error = K @ v - (L @ v) * roots
    modal_relative = np.linalg.norm(equation_error) / (
        np.linalg.norm(K @ v) + np.linalg.norm((L @ v) * roots)
    )
    assert modal_relative < 2e-14

    # A signed winding reversal is the coordinate transformation P=diag(1,-1).
    flipped = replace(model, M_h=-model.M_h)
    flipped_roots, flipped_v = flipped.numerical_modes()
    P = np.diag((1.0, -1.0))
    np.testing.assert_allclose(flipped_roots, roots, rtol=2e-13, atol=0)
    if model.M_h != 0:
        np.testing.assert_allclose(flipped_v, P @ v, rtol=2e-13, atol=2e-14)

    # The global energy metric verifies the rate identity for every real state.
    # z=(q1,q2,i1,i2), H=diag(C^-1,L), zdot=A z.
    A = model.state_matrix()
    H = np.block([[K, np.zeros((2, 2))], [np.zeros((2, 2)), L]])
    expected_symmetric = np.block(
        [[np.zeros((2, 2)), np.zeros((2, 2))], [np.zeros((2, 2)), -2 * R]]
    )
    identity_error = A.T @ H + H @ A - expected_symmetric
    identity_scale = (
        np.linalg.norm(A.T @ H) + np.linalg.norm(H @ A) + np.linalg.norm(expected_symmetric)
    )
    identity_residual = np.linalg.norm(identity_error) / identity_scale
    assert identity_residual < 2e-15

    # Signed, nonmodal states check actual instantaneous work/loss in SI units.
    power_residuals = []
    for q, i, voltage in (
        (np.array((2e-7, -8e-8)), np.array((0.02, -0.013)), np.zeros(2)),
        (np.array((-7e-8, 4e-7)), np.array((-0.017, 0.011)), np.array((0.7, -0.2))),
        (np.zeros(2), np.array((0.006, 0.013)), np.array((-0.3, 0.4))),
    ):
        idot = np.linalg.solve(L, voltage - R @ i - K @ q)
        actual_rate = float(q @ K @ i + i @ L @ idot)
        loss, input_power = float(i @ R @ i), float(voltage @ i)
        residual = abs(actual_rate - (input_power - loss))
        scale = abs(float(q @ K @ i)) + abs(float(i @ L @ idot)) + abs(input_power) + loss
        assert residual <= 5e-14 * max(scale, np.finfo(float).tiny)
        assert model.energy(q, i) > 0
        if not np.any(voltage):
            assert actual_rate <= 5e-14 * max(scale, np.finfo(float).tiny)
        np.testing.assert_allclose(
            flipped.energy(P @ q, P @ i), model.energy(q, i), rtol=2e-14, atol=0
        )
        Lf, Kf, Rf = flipped.matrices()
        np.testing.assert_allclose(
            np.linalg.solve(Lf, P @ voltage - Rf @ (P @ i) - Kf @ (P @ q)),
            P @ idot,
            rtol=2e-14,
            atol=1e-20,
        )
        power_residuals.append(residual)

    poles = np.linalg.eigvals(A)
    # Passive poles, independently derived from the four-dimensional state law.
    max_growth = max(poles.real)
    assert max_growth <= 2e-13 * math.sqrt(max(roots))
    if min(model.R1_ohm, model.R2_ohm) > 0:
        assert max_growth < 0
    return {
        "name": name,
        "parameters": asdict(model),
        "signed_coupling_k": model.coupling,
        "lossless_frequency_hz": (np.sqrt(roots) / (2 * math.pi)).tolist(),
        "lossless_omega_squared_analytic": analytic.tolist(),
        "mode_vectors_columns_L_normalized": v.tolist(),
        "analytic_eigen_max_relative_residual": float(max(abs(roots - analytic) / analytic)),
        "modal_equation_relative_residual": float(modal_relative),
        "global_energy_matrix_relative_residual": float(identity_residual),
        "sampled_power_balance_max_absolute_residual_w": max(power_residuals),
        "state_poles_per_s": [[float(z.real), float(z.imag)] for z in poles],
        "maximum_passive_growth_per_s": float(max_growth),
        "winding_reversal_frequency_and_state_covariance": "passed",
    }


def build_report():
    models = (
        ("symmetric_synthetic", CoupledLC(1e-3, 1e-3, 10e-9, 10e-9, 0.3e-3)),
        ("detuned_synthetic", CoupledLC(1e-3, 4e-3, 10e-9, 4e-9, 0.5e-3)),
        ("detuned_passive_losses", CoupledLC(1e-3, 4e-3, 10e-9, 4e-9, 0.5e-3, 2.0, 5.0)),
        ("detuned_decoupled", CoupledLC(1e-3, 4e-3, 10e-9, 4e-9, 0.0)),
    )
    reports = [audit_case(name, model) for name, model in models]

    # Independent equal-circuit normal-coordinate solution q1=+/-q2.
    symmetric = models[0][1]
    expected = np.array(
        (
            1 / (symmetric.C1_f * (symmetric.L1_h + symmetric.M_h)),
            1 / (symmetric.C1_f * (symmetric.L1_h - symmetric.M_h)),
        )
    )
    roots, vectors = symmetric.numerical_modes()
    np.testing.assert_allclose(roots, expected, rtol=2e-14, atol=0)
    np.testing.assert_allclose(vectors[1] / vectors[0], (1.0, -1.0), rtol=2e-14, atol=0)
    bare = 1 / (2 * math.pi * math.sqrt(symmetric.L1_h * symmetric.C1_f))
    frequencies = np.sqrt(roots) / (2 * math.pi)
    assert frequencies[0] < bare < frequencies[1]

    # M=0 recovers both uncoupled frequencies and no cross-loop acceleration.
    decoupled = models[3][1]
    expected_zero = sorted(
        (1 / (decoupled.L1_h * decoupled.C1_f), 1 / (decoupled.L2_h * decoupled.C2_f))
    )
    np.testing.assert_allclose(decoupled.numerical_modes()[0], expected_zero, rtol=2e-14, atol=0)
    assert decoupled.state_matrix()[2, 1] == decoupled.state_matrix()[3, 0] == 0
    near = replace(decoupled, M_h=1e-6 * math.sqrt(decoupled.L1_h * decoupled.L2_h))
    np.testing.assert_allclose(near.numerical_modes()[0], expected_zero, rtol=3e-12, atol=0)

    invalid = (
        {"L1_h": 0},
        {"L2_h": -1},
        {"C1_f": 0},
        {"C2_f": -1},
        {"L1_h": 1.0, "L2_h": 1.0, "M_h": 1.0},
        {"L1_h": 1.0, "L2_h": 1.0, "M_h": -1.0},
        {"M_h": 3},
        {"R1_ohm": -1},
        {"R2_ohm": -1},
        {"L1_h": math.nan},
        {"M_h": math.inf},
        {"C1_f": True},
        {"parameter_source": " "},
    )
    for changes in invalid:
        assert_rejected(**changes)

    report = {
        "scope": "Declared synthetic two-loop passive LC reference; not measured apparatus or a geometry calibration.",
        "provenance": {
            "preserved_source_sha256": "bf1fa88fe6dad993f15e13aea911fdc10fc918963509c290b06e2d712d5d20af",
            "preserved_report_sha256": "515884f60a7edb70e5da307740c934ff3ca51776737485b75b108a62717c7191",
            "hardening_review_source_sha256": "189e258d948ebe9909791b8757044719e1247415d7206ef93565c5ba722cbb86",
            "scope": "Recovered local synthetic controls; external historical claims are not republished.",
        },
        "all_checks": "passed",
        "case_count": len(reports),
        "invalid_input_cases_rejected": len(invalid),
        "symmetric_bare_frequency_hz": bare,
        "symmetric_split_hz": float(frequencies[1] - frequencies[0]),
        "cases": reports,
        "no_time_integrator": True,
        "needed_to_apply": [
            "L1 and L2 in henries",
            "C1 and C2 in farads",
            "signed M in henries and winding convention",
            "loss/load model, here series R1/R2 in ohms",
            "circuit connection and drive boundary conditions",
            "material/geometry reduction or measurements establishing those parameters",
        ],
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        f"Passed {report['case_count']} synthetic cases and {report['invalid_input_cases_rejected']} original rejection controls"
    )


if __name__ == "__main__":
    main()
