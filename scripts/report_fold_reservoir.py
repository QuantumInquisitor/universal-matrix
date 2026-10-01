"""Finite-fuel autonomous feedback in the synthetic reduced fold model."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import DAMPING, Q0, STIFFNESS, mechanical, vector
    from .report_fold_kinematics import scalar
except ImportError:
    from report_fold_dynamics import DAMPING, Q0, STIFFNESS, mechanical, vector
    from report_fold_kinematics import scalar

RESERVE_SCALE = 1e-5  # joules; synthetic activation scale, not calibration


def parameters(gain, efficiency, leakage, damping):
    values = [
        scalar(x, n)
        for x, n in zip(
            (gain, efficiency, leakage, damping),
            ("gain", "efficiency", "leakage", "damping"),
            strict=True,
        )
    ]
    g, eta, leak, d = values
    if not (0 <= g <= 10 and 0 < eta <= 1 and 0 <= leak <= 10 and 0 <= d <= 10):
        raise ValueError("reservoir parameters outside numerical scope")
    return values


def rhs(y, *, gain=4.0, efficiency=0.8, leakage=0.15, damping=1.0, omit_debit=False):
    # State: q(2), velocity(2), reserve, delivered work, damping loss,
    # conversion loss, leakage loss. All ledger entries are joules.
    y = vector(y, 9, "state")
    g, eta, leak, d = parameters(gain, efficiency, leakage, damping)
    if y[4] < 0:
        raise ValueError("negative reservoir: reduce timestep; no clipping allowed")
    state, bias, _ = mechanical(y[:2], y[2:4])
    velocity = y[2:4]
    applied = g * y[4] / (y[4] + RESERVE_SCALE) * (DAMPING @ velocity)
    power = float(applied @ velocity)
    dissipated = float(d * velocity @ DAMPING @ velocity)
    conversion = (1 / eta - 1) * power
    leaked = leak * y[4]
    acceleration = np.linalg.solve(
        state["mass_matrix"], applied - d * DAMPING @ velocity - STIFFNESS @ (y[:2] - Q0) - bias
    )
    derivative = np.r_[
        velocity,
        acceleration,
        -leaked if omit_debit else -power / eta - leaked,
        power,
        dissipated,
        conversion,
        leaked,
    ]
    if not np.all(np.isfinite(derivative)):
        raise ValueError("nonfinite reservoir derivative")
    return derivative


def simulate(
    *,
    duration=10.0,
    dt=0.02,
    reserve=2e-5,
    gain=4.0,
    efficiency=0.8,
    leakage=0.15,
    damping=1.0,
    equilibrium=False,
    omit_debit=False,
):
    duration, dt, reserve = [
        scalar(x, n)
        for x, n in zip((duration, dt, reserve), ("duration", "dt", "reserve"), strict=True)
    ]
    parameters(gain, efficiency, leakage, damping)
    if not (0 < duration <= 10 and 0 < dt <= 0.1 and 0 <= reserve <= 1e-4):
        raise ValueError("integration settings outside numerical scope")
    steps = round(duration / dt)
    if not (1 <= steps <= 10000 and math.isclose(steps * dt, duration, abs_tol=1e-12)):
        raise ValueError("duration must contain 1..10000 complete steps")
    y = np.r_[
        Q0 if equilibrium else Q0 + (0.02, -0.03),
        (0.0, 0.0) if equilibrium else (0.01, 0.02),
        reserve,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    initial_energy = mechanical(y[:2], y[2:4])[2]
    trace = []
    settings = dict(
        gain=gain, efficiency=efficiency, leakage=leakage, damping=damping, omit_debit=omit_debit
    )
    for step in range(steps + 1):
        derivative = rhs(y, **settings)  # also validates every endpoint
        energy = mechanical(y[:2], y[2:4])[2]
        trace.append(
            dict(
                time_s=step * dt,
                q=y[:2].tolist(),
                rates=y[2:4].tolist(),
                mechanical_j=energy,
                reserve_j=float(y[4]),
                work_j=float(y[5]),
                damping_loss_j=float(y[6]),
                conversion_loss_j=float(y[7]),
                leakage_loss_j=float(y[8]),
                total_residual_j=float(energy + y[4] + sum(y[6:]) - initial_energy - reserve),
                mechanical_residual_j=float(energy - initial_energy - y[5] + y[6]),
                reservoir_residual_j=float(y[4] - reserve + y[5] + y[7] + y[8]),
                delivered_power_w=float(derivative[5]),
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
        settings=dict(
            duration_s=duration,
            dt_s=dt,
            initial_reserve_j=reserve,
            equilibrium=equilibrium,
            **settings,
        ),
        initial_mechanical_j=initial_energy,
        final_state=y.tolist(),
        max_total_residual_j=max(abs(r["total_residual_j"]) for r in trace),
        max_mechanical_residual_j=max(abs(r["mechanical_residual_j"]) for r in trace),
        max_reservoir_residual_j=max(abs(r["reservoir_residual_j"]) for r in trace),
        minimum_reserve_j=min(r["reserve_j"] for r in trace),
        trace=trace,
    )


def report():
    cases = {}
    for name, settings in dict(
        fueled={},
        empty=dict(reserve=0),
        disconnected=dict(gain=0),
        equilibrium=dict(equilibrium=True),
        ideal_transfer=dict(efficiency=1, leakage=0, damping=0),
        omitted_debit_control=dict(omit_debit=True),
    ).items():
        run = simulate(**settings)
        run["samples"] = run.pop("trace")[::50]
        cases[name] = run
    fine = simulate(dt=0.01)
    coarse = cases["fueled"]
    return dict(
        schema=1,
        scope="Synthetic finite-fuel feedback; no external time forcing; not material calibration",
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_reservoir.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        reserve_activation_scale_j=RESERVE_SCALE,
        cases=cases,
        refinement=dict(
            dt_s=[0.02, 0.01],
            residuals_j=[coarse["max_total_residual_j"], fine["max_total_residual_j"]],
            final_coordinate_absolute_differences=np.abs(
                np.array(coarse["final_state"][:4]) - fine["final_state"][:4]
            ).tolist(),
        ),
        claims=dict(
            finite_internal_energy_source=True,
            sustained_autonomous_breathing=False,
            physical_material_validation=False,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: dict(residual=v["max_total_residual_j"], reserve=v["minimum_reserve_j"])
                for k, v in result["cases"].items()
            }
        )
    )
