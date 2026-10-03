"""Bounded distributed-inertia trajectories under the existing synthetic laws."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_ivp

from scripts.report_fold_constitutive import constitutive
from scripts.report_fold_distributed_inertia import distributed_kinematics, inertial_bias
from scripts.report_fold_dynamics import DAMPING, Q0, force, parameters, vector
from scripts.report_fold_kinematics import scalar


def simulate(
    *,
    damping=1.0,
    drive=0.0,
    drive_until=None,
    initial=None,
    duration=0.4,
    max_step=0.02,
    samples=81,
    omit_bias=False,
):
    damping, drive, drive_until = parameters(damping, drive, drive_until)
    duration, max_step = scalar(duration, "duration"), scalar(max_step, "max_step")
    if not 0 < duration <= 0.4 or not 0 < max_step <= 0.02:
        raise ValueError("duration in (0,.4], max_step in (0,.02] required")
    if isinstance(samples, bool) or not isinstance(samples, int) or not 3 <= samples <= 1001:
        raise ValueError("samples must be an integer in [3,1001]")
    y0 = (
        np.r_[Q0 + (0.02, -0.03), 0.01, 0.02, 0.0, 0.0]
        if initial is None
        else vector(initial, 6, "initial")
    )
    if np.any(y0[4:] != 0):
        raise ValueError("initial work and loss must be zero")

    def rhs(t, y):
        q, v = y[:2], y[2:4]
        state = distributed_kinematics(q)
        gradient = np.asarray(constitutive(q)["gradient"])
        applied, resistance = force(t, drive, drive_until), damping * DAMPING @ v
        bias = 0 if omit_bias else inertial_bias(state, v)
        a = np.linalg.solve(state["mass_matrix"], applied - resistance - gradient - bias)
        return np.r_[v, a, applied @ v, v @ resistance]

    times = np.linspace(0, duration, samples)
    solution = solve_ivp(
        rhs,
        (0, duration),
        y0,
        method="DOP853",
        t_eval=times,
        rtol=1e-10,
        atol=1e-13,
        max_step=max_step,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    rows, powers, losses = [], [], []
    for t, y in zip(times, solution.y.T, strict=True):
        q, v = y[:2], y[2:4]
        state = distributed_kinematics(q)
        # Cartesian quadrature energy is evaluated independently of M in rhs.
        kinetic = float(np.sum(state["mass"][:, None] * (state["jacobian"] @ v) ** 2) / 2)
        potential = float(constitutive(q)["total_energy_j"])
        powers.append(float(force(t, drive, drive_until) @ v))
        losses.append(float(v @ (damping * DAMPING) @ v))
        rows.append(
            dict(
                time_s=float(t),
                q=q.tolist(),
                rates=v.tolist(),
                kinetic_j=kinetic,
                potential_j=potential,
                energy_j=kinetic + potential,
                work_j=float(y[4]),
                loss_j=float(y[5]),
            )
        )
    energy = np.array([r["energy_j"] for r in rows])
    independent_work = cumulative_trapezoid(powers, times, initial=0)
    independent_loss = cumulative_trapezoid(losses, times, initial=0)
    residual = energy - energy[0] - solution.y[4] + solution.y[5]
    return dict(
        final_state=solution.y[:, -1].tolist(),
        trace=rows,
        maximum_balance_residual_j=float(np.max(abs(residual))),
        independent_work_error_j=float(np.max(abs(independent_work - solution.y[4]))),
        independent_loss_error_j=float(np.max(abs(independent_loss - solution.y[5]))),
        maximum_energy_step_increase_j=float(np.max(np.diff(energy))),
        max_step_s=max_step,
        samples=samples,
        omitted_inertial_bias=omit_bias,
    )


def report():
    cases = {}
    for name, kwargs in {
        "equilibrium": dict(initial=np.r_[Q0, 0.0, 0.0, 0.0, 0.0]),
        "conservative": dict(damping=0),
        "passive": dict(),
        "driven": dict(drive=1),
        "drive_off": dict(drive=1, drive_until=0.2),
    }.items():
        coarse = simulate(**kwargs)
        fine = simulate(max_step=0.01, samples=161, **kwargs)
        fine["refinement"] = dict(
            final_state_max_difference=float(
                np.max(abs(np.array(coarse["final_state"]) - fine["final_state"]))
            ),
            coarse_work_quadrature_error_j=coarse["independent_work_error_j"],
            coarse_loss_quadrature_error_j=coarse["independent_loss_error_j"],
        )
        cases[name] = fine
    initial = np.r_[Q0 + (0.02, -0.03), 0.12, -0.2, 0.0, 0.0]
    healthy = simulate(initial=initial, damping=0)
    faulty = simulate(initial=initial, damping=0, omit_bias=True)
    end = np.asarray(cases["conservative"]["final_state"])
    reverse = simulate(initial=np.r_[end[:2], -end[2:4], 0.0, 0.0], damping=0)
    target = np.r_[Q0 + (0.02, -0.03), -0.01, -0.02]
    reversal_error = float(np.max(abs(np.array(reverse["final_state"][:4]) - target)))
    root = Path(__file__).resolve().parent
    names = [
        "report_fold_distributed_trajectories.py",
        "report_fold_distributed_inertia.py",
        "report_fold_constitutive.py",
        "report_fold_dynamics.py",
        "report_fold_kinematics.py",
    ]
    result = dict(
        schema="fold-distributed-trajectories-v1",
        duration_s=0.4,
        solver=dict(method="DOP853", rtol=1e-10, atol=1e-13),
        cases=cases,
        reversal_error=reversal_error,
        bias_control=dict(
            healthy_residual_j=healthy["maximum_balance_residual_j"],
            omitted_bias_residual_j=faulty["maximum_balance_residual_j"],
        ),
        sources={
            n: hashlib.sha256((root / n).read_text(encoding="utf-8").encode()).hexdigest()
            for n in names
        },
        source_hash_encoding="UTF-8/LF",
        production_dynamics_changed=False,
        physical_calibration=False,
        stable_breathing_established=False,
    )
    validate(result)
    return result


def validate(result):
    for case in result["cases"].values():
        assert case["maximum_balance_residual_j"] < 1e-10
        assert case["refinement"]["final_state_max_difference"] < 1e-8
        assert case["independent_work_error_j"] < 1e-9
        assert case["independent_loss_error_j"] < 1e-9
    for name in ("passive", "conservative"):
        assert result["cases"][name]["maximum_energy_step_increase_j"] < 1e-12
    equilibrium = result["cases"]["equilibrium"]["final_state"]
    assert np.max(abs(np.asarray(equilibrium[:4]) - np.r_[Q0, 0.0, 0.0])) < 1e-10
    off = [r for r in result["cases"]["drive_off"]["trace"] if r["time_s"] >= 0.2]
    assert max(r["work_j"] for r in off) - min(r["work_j"] for r in off) < 1e-12
    assert result["reversal_error"] < 1e-8
    assert result["bias_control"]["healthy_residual_j"] < 1e-10
    assert result["bias_control"]["omitted_bias_residual_j"] > 1e-9


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"reversal_error": result["reversal_error"], "bias_control": result["bias_control"]}
        )
    )
