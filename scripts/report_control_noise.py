"""Frozen thirty-run synthetic finite-band measurement-noise comparison."""

# ruff: noqa: E402
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.proposed_noisy_control import noisy_control_trace

FIXTURE = ROOT / "tests/fixtures/control_noise_coefficients.json"
FIXTURE_SHA256 = "2d90cb5b0144409990a2341735a27b2cc44ac17d18a707eb4e5b309d22198e9c"


def sampled_summary(run):
    t = np.array(run["times_s"])
    qv = np.array(run["states"])
    q, v = qv[:, :2], qv[:, 2:]
    force = np.array(run["applied_force_per_mass"])
    command = np.array(run["limited_command_per_mass"])
    power = (
        np.sum(force * v, axis=1)
        - 0.2 * np.sin(2 * t) * np.sum(q * q, axis=1)
        - 0.04 * np.sum(v * v, axis=1)
    )
    delta = run["mechanical_energy_per_mass"][-1] - run["mechanical_energy_per_mass"][0]
    fields = (
        "parameters",
        "late_position_rms_m",
        "diagnostic_limit_m",
        "meets_declared_tracking_target",
        "maximum_sampled_force_per_mass",
        "sampled_command_clipping_fraction",
        "sampled_applied_force_saturation_fraction",
        "sampled_noise_mean",
        "sampled_noise_rms",
        "noise_statistics_convention",
        "clipping_statistics_convention",
        "max_energy_balance_residual_per_mass",
    )
    result = {key: run[key] for key in fields}
    result.update(
        sampled_power_quadrature_residual_per_mass=abs(float(delta - np.trapezoid(power, t))),
        sampled_actual_force_rms_per_mass=float(np.sqrt(np.mean(np.sum(force * force, axis=1)))),
        minimum_sampled_damping_increment=float(np.min(np.diff(run["damping_loss_per_mass"]))),
        command_work_substitution_error_per_mass=abs(
            float(np.trapezoid(np.sum(command * v, axis=1), t) - run["actuator_work_per_mass"][-1])
        ),
    )
    for field in ("actuator_work_per_mass", "pump_work_per_mass", "damping_loss_per_mass"):
        result["final_" + field] = run[field][-1]
    return result


def compare(runs):
    summaries = [sampled_summary(run) for run in runs]
    errors = []
    for a, b in zip(runs, runs[1:], strict=False):
        delta = np.abs(np.array(a["states"]) - np.array(b["states"])[::2])
        errors.append(
            {
                "maximum_position_difference_m": float(np.max(delta[:, :2])),
                "maximum_velocity_difference_m_s": float(np.max(delta[:, 2:])),
                "late_rms_difference_m": abs(a["late_position_rms_m"] - b["late_position_rms_m"]),
            }
        )
    failures = []
    for index, error in enumerate(errors):
        for key, limit in (
            ("maximum_position_difference_m", 5e-4),
            ("maximum_velocity_difference_m_s", 5e-4),
            ("late_rms_difference_m", 1e-4),
        ):
            if error[key] >= limit:
                failures.append(f"refinement_{index}:{key}")
    if len(errors) == 2:
        for key in errors[0]:
            if errors[1][key] >= errors[0][key] and errors[1][key] >= 1e-10:
                failures.append("preselected_finer_difference_not_decreasing:" + key)
    for index, s in enumerate(summaries):
        if s["max_energy_balance_residual_per_mass"] >= 1e-5:
            failures.append(f"integrated_balance_{index}")
        if s["minimum_sampled_damping_increment"] < 0:
            failures.append(f"negative_damping_{index}")
    for index, (a, b) in enumerate(zip(summaries, summaries[1:], strict=False)):
        if (
            b["sampled_power_quadrature_residual_per_mass"]
            >= a["sampled_power_quadrature_residual_per_mass"]
        ):
            failures.append(f"quadrature_not_decreasing_{index}")
    tracking = [s["meets_declared_tracking_target"] for s in summaries]
    borderline = len(set(tracking)) != 1 or any(
        abs(s["late_position_rms_m"] - 0.05) <= 1e-4 for s in summaries
    )
    status = (
        "numerically_unresolved"
        if failures
        else "borderline_unresolved"
        if borderline
        else "meets_finite_run_target"
        if tracking[-1]
        else "fails_finite_run_target"
    )
    return {
        "runs": summaries,
        "refinement_errors": errors,
        "numerical_gate_failures": failures,
        "tracking_borderline": borderline,
        "classification": status,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    fixture_text = FIXTURE.read_text(encoding="utf-8")
    if hashlib.sha256(fixture_text.encode()).hexdigest() != FIXTURE_SHA256:
        raise ValueError("saved coefficient fixture changed; reviewed protocol pin required")
    fixture = json.loads(fixture_text)
    cases = {}
    traces = {}
    start = time.perf_counter()
    count = 0
    for label, tau, delay in (("ideal", 0.0, 0.0), ("lag_delay", 0.1, 0.2)):
        baseline = None
        for amplitude, seed in [(0.0, 7)] + [(a, s) for a in (0.01, 0.1) for s in (7, 19, 41)]:
            name = f"{label}:sigma={amplitude}:seed={seed}"
            resolutions = [256, 512] + ([1024] if amplitude == 0.1 and seed == 7 else [])
            runs = []
            for steps in resolutions:
                run = noisy_control_trace(
                    coefficients=fixture["seeds"][str(seed)],
                    position_sigma_m=amplitude,
                    velocity_sigma_m_s=amplitude,
                    actuator_time_constant_s=tau,
                    delay_s=delay,
                    steps_per_period=steps,
                )
                runs.append(run)
                count += 1
                print(
                    f"{count}/30 {name} steps={steps} RMS={run['late_position_rms_m']:.9g}",
                    flush=True,
                )
            case = compare(runs)
            case.update(
                configuration=label,
                seed=seed,
                position_sigma_m=amplitude,
                velocity_sigma_m_s=amplitude,
            )
            if amplitude == 0:
                baseline = {
                    n: r["late_position_rms_m"] for n, r in zip(resolutions, runs, strict=True)
                }
            case["paired_late_rms_differences_from_zero_m"] = {
                str(n): r["late_position_rms_m"] - baseline[n]
                for n, r in zip(resolutions, runs, strict=True)
                if n in baseline
            }
            cases[name] = case
            traces[name] = runs
    paths = [FIXTURE, Path(__file__)] + [
        ROOT / "src" / name
        for name in (
            "proposed_noisy_control.py",
            "proposed_measurement_noise.py",
            "proposed_combined_control_limits.py",
            "proposed_mode_pair_control.py",
            "proposed_scalar_wave_control.py",
        )
    ]
    metadata = {
        "schema": 1,
        "run_count": count,
        "elapsed_seconds": time.perf_counter() - start,
        "noise_fixture": fixture,
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode()
            ).hexdigest()
            for p in paths
        },
        "hash_convention": "UTF-8 normalized LF text",
        "numpy_version": np.__version__,
        "scope": "Finite synthetic known-reference tracking; all30 preregistered integrations retained. No hardware, stability-boundary, population-reliability or quantum-noise claim.",
        "gate_thresholds": {
            "position_difference_m": 5e-4,
            "velocity_difference_m_s": 5e-4,
            "late_rms_difference_m": 1e-4,
            "integrated_balance_per_mass": 1e-5,
            "tracking_m": 0.05,
            "tracking_borderline_band_m": 1e-4,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({**metadata, "cases": cases, "traces": traces}, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps({**metadata, "cases": cases}, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: case["classification"] for key, case in cases.items()}, indent=2))


if __name__ == "__main__":
    main()
