"""Bounded sensitivity study; region rejection is not a collision result."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, simulate
except ImportError:
    from report_fold_dynamics import Q0, simulate

DOMAIN_ERROR = "outside declared scope [.9,1.1] x [0,pi/6]"
SEED = 20260930


def run_case(name, **settings):
    """Catch only the known model rectangle rejection; expose other errors."""
    metadata = dict(name=name, settings=settings)
    try:
        run = simulate(**settings)
    except (FloatingPointError, OverflowError, np.linalg.LinAlgError) as error:
        return dict(
            **metadata,
            classification="numerical-error",
            reason=f"{type(error).__name__}: {error}",
            collision_status="not assessed",
            metrics=None,
        )
    except ValueError as error:
        if str(error) != DOMAIN_ERROR:
            raise
        return dict(
            **metadata,
            classification="domain-rejected",
            reason=str(error),
            collision_status="not assessed",
            metrics=None,
        )

    trace = run["trace"]
    states = np.array([row["q"] + row["rates"] for row in trace])
    energies = np.array([row["energy_j"] for row in trace])
    ledger = np.array(
        [[row[key] for key in ("energy_j", "work_j", "loss_j", "residual_j")] for row in trace]
    )
    if not np.all(np.isfinite(states)) or not np.all(np.isfinite(ledger)):
        return dict(
            **metadata,
            classification="numerical-error",
            collision_status="not assessed",
            reason="nonfinite trace",
            metrics=None,
        )
    # Reference is a stated ledger magnitude, not final energy (which may decay).
    reference = max(
        run["initial_energy_j"],
        float(np.max(np.abs(energies))),
        max(abs(row["work_j"]) for row in trace),
        max(abs(row["loss_j"]) for row in trace),
    )
    residual = run["maximum_balance_residual_j"]
    metrics = dict(
        final_state=run["final_state"],
        state_min=states.min(axis=0).tolist(),
        state_max=states.max(axis=0).tolist(),
        initial_energy_j=run["initial_energy_j"],
        final_energy_j=run["final_energy_j"],
        max_balance_residual_j=residual,
        balance_reference_j=reference,
        relative_balance_residual=residual / reference if reference else 0.0,
        extrema_scope=run["extrema_scope"],
    )
    return dict(
        **metadata, classification="success", collision_status="not assessed", metrics=metrics
    )


def configurations():
    cases = []
    for duration in (2.0, 10.0):
        for damping in (0.0, 0.25, 1.0):
            for drive in (0.0, 1.0, 3.0):
                cases.append(
                    (
                        f"t{duration:g}-d{damping:g}-f{drive:g}",
                        dict(duration=duration, dt=0.02, damping=damping, drive=drive),
                    )
                )
    rng = np.random.default_rng(SEED)
    amplitudes = np.array((0.01, 0.015, 0.01, 0.015))
    base = np.r_[Q0 + (0.02, -0.03), 0.01, 0.02]
    for index in range(2):
        initial = np.r_[base + rng.uniform(-1, 1, 4) * amplitudes, 0.0, 0.0].tolist()
        cases.append(
            (
                f"perturb-{index}",
                dict(duration=10.0, dt=0.02, damping=0.25, drive=1.0, initial=initial),
            )
        )
    cases.append(("accepted-refined", dict(duration=10.0, dt=0.01, damping=0.25, drive=1.0)))
    for dt in (0.02, 0.01, 0.005):
        cases.append(
            (
                f"high-rate-dt{dt:g}",
                dict(
                    duration=2.0,
                    dt=dt,
                    damping=0.0,
                    drive=0.0,
                    initial=np.r_[Q0, 2.0, 0.0, 0.0, 0.0].tolist(),
                ),
            )
        )
    return cases


def report():
    cases = [run_case(name, **settings) for name, settings in configurations()]
    by_name = {case["name"]: case for case in cases}
    coarse, fine = [by_name[name] for name in ("t10-d0.25-f1", "accepted-refined")]
    refinement = dict(classifications=[coarse["classification"], fine["classification"]])
    if all(case["classification"] == "success" for case in (coarse, fine)):
        refinement["final_coordinate_absolute_difference"] = np.abs(
            np.array(coarse["metrics"]["final_state"][:4]) - fine["metrics"]["final_state"][:4]
        ).tolist()
        refinement["residual_j_coarse_fine"] = [
            case["metrics"]["max_balance_residual_j"] for case in (coarse, fine)
        ]
    root = Path(__file__).resolve().parent
    return dict(
        schema_version=1,
        scope="Synthetic 22-lump two-coordinate model; prescribed external drive; no collision or calibrated-material claim",
        source_sha256_normalized_text={
            name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest()
            for name in (
                "report_fold_kinematics.py",
                "report_fold_dynamics.py",
                "report_fold_robustness.py",
            )
        },
        perturbation=dict(
            seed=SEED,
            generator="numpy default_rng PCG64",
            distribution="independent uniform [-amplitude,+amplitude]",
            amplitudes=[0.01, 0.015, 0.01, 0.015],
        ),
        coordinate_columns=["scale", "angle_rad", "scale_rate_per_s", "angle_rate_rad_per_s"],
        relative_residual_definition="max abs(E-E0-W+loss) / max(E0, max abs(E), max abs(W), max abs(loss)); zero if all zero",
        classification_definition="success means integration stayed in declared numerical rectangle; domain-rejected includes RK stages and does not establish physical escape or collision; other ValueErrors propagate",
        counts={
            key: sum(case["classification"] == key for case in cases)
            for key in ("success", "domain-rejected", "numerical-error")
        },
        accepted_refinement=refinement,
        rejected_refinement=[
            by_name[f"high-rate-dt{dt:g}"]["classification"] for dt in (0.02, 0.01, 0.005)
        ],
        cases=cases,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
