"""Finite-window power onset audit with equilibrium-initial reserves."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from . import report_fold_supply as supply
except ImportError:
    import report_fold_supply as supply

POWERS = (0.0, 3e-7, 6e-7, 9e-7, 1.2e-6)
PERTURBATION = np.array(((1, 1), (-1, 0.5), (0.5, -1), (-0.5, -0.5))) * 1e-4
SOURCE_NAMES = (
    "threshold",
    "supply",
    "active_multiscale",
    "multiscale",
    "scaled_pair",
    "scaling",
    "mapped",
    "hierarchy",
    "network",
    "coupling",
    "reservoir",
    "dynamics",
    "kinematics",
)


def equilibrium(power_density):
    p = supply.power_setting(power_density)
    return 2e-5 * np.array(supply.BASE_SIZES) ** 3 * p / (p + 3e-6)


def feedback_ratio(power_density):
    p = supply.power_setting(power_density)
    return 8 * p / (3 * p + 3e-6)


def initial_state(power_density, *, perturbed=True):
    if type(perturbed) is not bool:
        raise ValueError("perturbed must be boolean")
    y = np.zeros(48)
    blocks = y[:36].reshape(4, 9)
    blocks[:, :2] = supply.Q0 + (PERTURBATION if perturbed else 0)
    blocks[:, 4] = equilibrium(power_density)
    return y


def simulate(duration=20.0, *, power_density=0.0, max_step=0.05, rtol=1e-8):
    run = supply.simulate(
        duration,
        power_density=power_density,
        max_step=max_step,
        rtol=rtol,
        initial=initial_state(power_density),
    )
    samples = run["samples"]
    initial_energy = samples[0]["total_mechanical_j"]
    late = [row for row in samples if row["time_s"] >= 0.75 * duration]
    covered = [late[0]["time_s"], late[-1]["time_s"]] if late else None
    slope = (
        (late[-1]["total_mechanical_j"] - late[0]["total_mechanical_j"])
        / (late[-1]["time_s"] - late[0]["time_s"])
        if len(late) > 1
        else None
    )
    run["onset"] = dict(
        equilibrium_reserve_j=equilibrium(power_density).tolist(),
        equilibrium_feedback_to_damping_ratio=feedback_ratio(power_density),
        initial_total_mechanical_j=initial_energy,
        final_to_initial_energy_ratio=run["final_total_mechanical_j"] / initial_energy,
        late_sampled_window=dict(
            requested_interval_s=[0.75 * duration, duration],
            covered_interval_s=covered,
            sample_count=len(late),
            endpoint_energy_slope_w=slope,
            note="Saved accepted endpoints; coverage begins at the first saved late endpoint.",
        ),
    )
    return run


def source_hashes():
    return {
        f"report_fold_{name}.py": hashlib.sha256(
            Path(__file__).with_name(f"report_fold_{name}.py").read_text(encoding="utf-8").encode()
        ).hexdigest()
        for name in SOURCE_NAMES
    }


def report():
    sources = source_hashes()
    cases = {}
    settings = [(f"power_{i}", p, 0.05, 1e-8) for i, p in enumerate(POWERS)]
    settings.append(("fine_power_3", POWERS[3], 0.025, 1e-9))
    for name, power, step, tolerance in settings:
        options = dict(power_density=power, max_step=step, rtol=tolerance)
        print(f"Running {name}: p={power} W, 20 seconds", flush=True)
        cases[name] = simulate(20.0, **options)
        key = hashlib.sha256(
            json.dumps(
                dict(
                    sources=sources,
                    name=name,
                    duration=20.0,
                    options=options,
                ),
                sort_keys=True,
            ).encode()
        ).hexdigest()[:20]
        checkpoint = (
            Path(__file__).resolve().parents[1]
            / "artifacts"
            / "fold-threshold"
            / f"{name}-{key}.json"
        )
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        checkpoint.write_text(
            json.dumps(dict(sources=sources, result=cases[name]), indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        print(f"Completed {name}: {cases[name]['termination']}", flush=True)
    a, b = cases["power_3"], cases["fine_power_3"]
    matched = (
        a["termination"]["status"] == b["termination"]["status"] == "completed"
        and a["termination"]["last_accepted_time_s"] == b["termination"]["last_accepted_time_s"]
    )
    return dict(
        schema=1,
        sources=sources,
        scope="20-second near-rest onset sweep in the existing synthetic supplied graph",
        protocol=dict(
            powers_w=list(POWERS),
            coordinate_perturbation=PERTURBATION.tolist(),
            initial_rates="zero",
            initial_ledgers="zero",
            reserve_initialization="rest equilibrium for each power",
            same_initial_mechanical_energy=True,
            same_initial_total_energy=False,
            damping_threshold_w=6e-7,
            equilibrium_reserve_fraction="p/(p+3e-6)",
            equilibrium_feedback_ratio="8*p/(3*p+3e-6)",
            conditional_energy_result="Within scope, equilibrium-initial reserves stay in [0,Req]; for p<=6e-7 W mechanical plus connector energy is nonincreasing.",
        ),
        cases=cases,
        refinement=dict(
            baseline="power_3",
            fine="fine_power_3",
            matched_final_time_s=a["termination"]["last_accepted_time_s"] if matched else None,
            absolute_state_differences=abs(np.array(a["final_state"]) - b["final_state"]).tolist()
            if matched
            else None,
            absolute_mechanical_difference_j=abs(
                a["final_total_mechanical_j"] - b["final_total_mechanical_j"]
            )
            if matched
            else None,
        ),
        stable_breathing=False,
        calibrated_material=False,
        ideal_external_source=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
