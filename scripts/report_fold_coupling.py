"""Two synthetic fold modules linked by a conservative generalized spring."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, mechanical, vector
    from .report_fold_kinematics import scalar
    from .report_fold_reservoir import rhs as reservoir_rhs
except ImportError:
    from report_fold_dynamics import Q0, mechanical, vector
    from report_fold_kinematics import scalar
    from report_fold_reservoir import rhs as reservoir_rhs

COUPLING = np.diag((0.003, 0.001))


def spring(qa, qb, coupling=1.0):
    coupling = scalar(coupling, "coupling")
    if not 0 <= coupling <= 10:
        raise ValueError("coupling outside [0,10]")
    delta = vector(qa, 2, "qa") - vector(qb, 2, "qb")
    gradient = coupling * COUPLING @ delta
    return float(delta @ gradient / 2), -gradient, gradient


def rhs(
    y,
    *,
    coupling=1.0,
    gain=4.0,
    damping=1.0,
    leakage=0.15,
    efficiency=0.8,
    wrong_reaction=False,
    potential="quadratic",
):
    # Two 9-state modules followed by work delivered by the connection to each.
    y = vector(y, 20, "coupled state")
    modules = y[:18].reshape(2, 9)
    _, force_a, force_b = spring(modules[0, :2], modules[1, :2], coupling)
    if wrong_reaction:
        force_b = -force_b  # deliberate nonconservative negative control
    result = np.zeros(20)
    for i, force in enumerate((force_a, force_b)):
        block = modules[i]
        derivative = reservoir_rhs(
            block,
            gain=gain,
            damping=damping,
            leakage=leakage,
            efficiency=efficiency,
            potential=potential,
        )
        mass = mechanical(block[:2], block[2:4], potential=potential)[0]["mass_matrix"]
        derivative[2:4] += np.linalg.solve(mass, force)
        result[9 * i : 9 * i + 9] = derivative
        result[18 + i] = force @ block[2:4]
    return result


def initial_state(fueled=True):
    a = np.r_[Q0 + (0.02, -0.03), 0.01, 0.02, 2e-5 if fueled else 0.0, 0.0, 0.0, 0.0, 0.0]
    b = np.r_[Q0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    return np.r_[a, b, 0.0, 0.0]


def measure(y, coupling=1.0, *, potential="quadratic"):
    modules = np.asarray(y[:18]).reshape(2, 9)
    energies = [mechanical(m[:2], m[2:4], potential=potential)[2] for m in modules]
    spring_energy = spring(modules[0, :2], modules[1, :2], coupling)[0]
    total = sum(energies) + float(np.sum(modules[:, 4]) + np.sum(modules[:, 6:])) + spring_energy
    return np.array(energies), spring_energy, total


def simulate(
    *,
    duration=10.0,
    dt=0.02,
    coupling=1.0,
    gain=4.0,
    damping=1.0,
    leakage=0.15,
    efficiency=0.8,
    fueled=True,
    wrong_reaction=False,
    initial=None,
    potential="quadratic",
):
    duration, dt = scalar(duration, "duration"), scalar(dt, "dt")
    if not 0 < duration <= 10 or not 0 < dt <= 0.1:
        raise ValueError("duration or timestep outside numerical scope")
    steps = round(duration / dt)
    if not 1 <= steps <= 10000 or not math.isclose(steps * dt, duration, abs_tol=1e-12):
        raise ValueError("duration must contain 1..10000 complete steps")
    y = initial_state(fueled) if initial is None else vector(initial, 20, "initial")
    initial_snapshot = y.tolist()
    blocks = y[:18].reshape(2, 9)
    if np.any(blocks[:, 5:] != 0) or np.any(y[18:] != 0):
        raise ValueError("initial work and loss ledgers must be zero")
    if np.any(blocks[:, 4] > 1e-4):
        raise ValueError("initial reserves outside numerical scope")
    settings = dict(
        coupling=coupling,
        gain=gain,
        damping=damping,
        leakage=leakage,
        efficiency=efficiency,
        wrong_reaction=wrong_reaction,
        potential=potential,
    )
    rhs(y, **settings)
    e0, u0, total0 = measure(y, coupling, potential=potential)
    trace = []
    for step in range(steps + 1):
        derivative = rhs(y, **settings)
        energies, spring_energy, total = measure(y, coupling, potential=potential)
        blocks = y[:18].reshape(2, 9)
        local = energies - e0 - blocks[:, 5] + blocks[:, 6] - y[18:]
        trace.append(
            dict(
                time_s=step * dt,
                q=blocks[:, :2].tolist(),
                mechanical_j=energies.tolist(),
                reserve_j=blocks[:, 4].tolist(),
                spring_j=spring_energy,
                coupling_work_j=y[18:].tolist(),
                reservoir_work_j=blocks[:, 5].tolist(),
                losses_j=blocks[:, 6:].tolist(),
                module_residual_j=local.tolist(),
                total_residual_j=total - total0,
                connection_residual_j=float(spring_energy - u0 + sum(y[18:])),
            )
        )
        if step == steps:
            break
        a = derivative
        b = rhs(y + dt * a / 2, **settings)
        c = rhs(y + dt * b / 2, **settings)
        d = rhs(y + dt * c, **settings)
        y = y + dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        settings=dict(duration_s=duration, dt_s=dt, **settings),
        initial_state=initial_snapshot,
        initialization="explicit"
        if initial is not None
        else ("fueled A" if fueled else "empty reserves"),
        initial_total_j=total0,
        final_state=y.tolist(),
        max_total_residual_j=max(abs(r["total_residual_j"]) for r in trace),
        max_module_residual_j=max(max(map(abs, r["module_residual_j"])) for r in trace),
        max_connection_residual_j=max(abs(r["connection_residual_j"]) for r in trace),
        trace=trace,
    )


def report():
    cases = {}
    for name, settings in dict(
        fueled_pair={},
        disconnected=dict(coupling=0),
        conservative=dict(fueled=False, gain=0, damping=0, leakage=0),
        wrong_reaction_control=dict(
            fueled=False, gain=0, damping=0, leakage=0, wrong_reaction=True
        ),
    ).items():
        run = simulate(**settings)
        run["samples"] = run.pop("trace")[::50]
        cases[name] = run
    fine = simulate(dt=0.01)
    coarse = cases["fueled_pair"]
    return dict(
        schema=1,
        scope="Two synthetic generalized-coordinate modules; no spatial joint or intermodule collision validation",
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_coupling.py",
                "report_fold_reservoir.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        coupling_matrix=COUPLING.tolist(),
        cases=cases,
        refinement=dict(
            dt_s=[0.02, 0.01],
            residuals_j=[coarse["max_total_residual_j"], fine["max_total_residual_j"]],
            final_coordinate_absolute_differences=[
                np.abs(
                    np.array(coarse["final_state"][i : i + 4]) - fine["final_state"][i : i + 4]
                ).tolist()
                for i in (0, 9)
            ],
        ),
        full_structure_recursive_validation=False,
        sustained_breathing=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v["max_total_residual_j"] for k, v in result["cases"].items()}))
