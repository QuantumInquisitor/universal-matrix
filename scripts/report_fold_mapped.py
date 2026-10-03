"""Energy-derived connector between nonlinear ports with different lever lengths."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_coupling import initial_state
    from .report_fold_dynamics import Q0, mechanical, vector
    from .report_fold_kinematics import scalar
    from .report_fold_reservoir import rhs as reservoir_rhs
except ImportError:
    from report_fold_coupling import initial_state
    from report_fold_dynamics import Q0, mechanical, vector
    from report_fold_kinematics import scalar
    from report_fold_reservoir import rhs as reservoir_rhs

PORT_STIFFNESS = np.diag((0.3, 0.1))  # N/m in the synthetic two-component port
PARENT_LENGTH = 0.1  # m


def port(q, length):
    q = vector(q, 2, "coordinates")
    length = scalar(length, "port length")
    if not 0 < length <= 1:
        raise ValueError("port length outside (0,1] metres")
    if not 0.9 <= q[0] <= 1.1 or not 0 <= q[1] <= math.pi / 6:
        raise ValueError("port coordinates outside validated domain")
    s, angle = q[0], q[1] - Q0[1]
    displacement = length * np.array((s - 1, s * math.sin(angle)))
    jacobian = length * np.array(((1, 0), (math.sin(angle), s * math.cos(angle))))
    return displacement, jacobian


def connector(qa, qb, ratio=0.5, *, wrong_child_jacobian=False):
    ratio = scalar(ratio, "length ratio")
    if not 0.1 <= ratio <= 1:
        raise ValueError("length ratio outside [.1,1]")
    pa, ja = port(qa, PARENT_LENGTH)
    pb, jb = port(qb, PARENT_LENGTH * ratio)
    delta = pa - pb
    stress = PORT_STIFFNESS @ delta
    energy = float(delta @ stress / 2)
    return energy, -ja.T @ stress, (ja if wrong_child_jacobian else jb).T @ stress


def rhs(
    y, *, ratio=0.5, gain=4.0, damping=1.0, leakage=0.15, efficiency=0.8, wrong_child_jacobian=False
):
    y = vector(y, 20, "mapped state")
    blocks = y[:18].reshape(2, 9)
    _, fa, fb = connector(
        blocks[0, :2], blocks[1, :2], ratio, wrong_child_jacobian=wrong_child_jacobian
    )
    result = np.zeros(20)
    for i, force in enumerate((fa, fb)):
        block = blocks[i]
        derivative = reservoir_rhs(
            block, gain=gain, damping=damping, leakage=leakage, efficiency=efficiency
        )
        mass = mechanical(block[:2], block[2:4])[0]["mass_matrix"]
        derivative[2:4] += np.linalg.solve(mass, force)
        result[9 * i : 9 * i + 9] = derivative
        result[18 + i] = force @ block[2:4]
    return result


def measure(y, ratio=0.5):
    blocks = np.asarray(y[:18]).reshape(2, 9)
    energies = np.array([mechanical(b[:2], b[2:4])[2] for b in blocks])
    potential = connector(blocks[0, :2], blocks[1, :2], ratio)[0]
    return (
        energies,
        potential,
        float(sum(energies) + potential + sum(blocks[:, 4]) + np.sum(blocks[:, 6:])),
    )


def simulate(
    *,
    ratio=0.5,
    dt=0.02,
    duration=4.0,
    fueled=True,
    gain=4.0,
    damping=1.0,
    leakage=0.15,
    efficiency=0.8,
    wrong_child_jacobian=False,
):
    duration, dt = scalar(duration, "duration"), scalar(dt, "dt")
    if not 0 < duration <= 10 or not 0 < dt <= 0.1:
        raise ValueError("integration settings outside scope")
    steps = round(duration / dt)
    if not 1 <= steps <= 10000 or not math.isclose(steps * dt, duration, abs_tol=1e-12):
        raise ValueError("duration must contain complete steps")
    settings = dict(
        ratio=ratio,
        gain=gain,
        damping=damping,
        leakage=leakage,
        efficiency=efficiency,
        wrong_child_jacobian=wrong_child_jacobian,
    )
    y = initial_state(fueled)
    snapshot = y.tolist()
    rhs(y, **settings)
    e0, u0, total0 = measure(y, ratio)
    trace = []
    for step in range(steps + 1):
        derivative = rhs(y, **settings)
        energies, potential, total = measure(y, ratio)
        blocks = y[:18].reshape(2, 9)
        trace.append(
            dict(
                time_s=step * dt,
                q=blocks[:, :2].tolist(),
                rates=blocks[:, 2:4].tolist(),
                mechanical_j=energies.tolist(),
                reserve_j=blocks[:, 4].tolist(),
                connector_j=potential,
                connector_work_j=y[18:].tolist(),
                reservoir_work_j=blocks[:, 5].tolist(),
                losses_j=blocks[:, 6:].tolist(),
                node_residual_j=(energies - e0 - blocks[:, 5] + blocks[:, 6] - y[18:]).tolist(),
                connector_residual_j=float(potential - u0 + sum(y[18:])),
                total_residual_j=total - total0,
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
        initial_state=snapshot,
        final_state=y.tolist(),
        max_total_residual_j=max(abs(r["total_residual_j"]) for r in trace),
        max_node_residual_j=max(max(map(abs, r["node_residual_j"])) for r in trace),
        max_connector_residual_j=max(abs(r["connector_residual_j"]) for r in trace),
        trace=trace,
    )


def report():
    cases = {}
    for name, settings in dict(
        equal_ports=dict(ratio=1),
        half_port=dict(ratio=0.5),
        quarter_port=dict(ratio=0.25),
        conservative=dict(fueled=False, gain=0, damping=0, leakage=0),
        wrong_jacobian_control=dict(wrong_child_jacobian=True),
    ).items():
        run = simulate(**settings)
        run["samples"] = run.pop("trace")[::25]
        cases[name] = run
    fine = simulate(dt=0.01)
    return dict(
        schema=1,
        scope="Synthetic nonlinear port-length mapping; unchanged module inertia and material parameters",
        parent_length_m=PARENT_LENGTH,
        port_stiffness_n_per_m=PORT_STIFFNESS.tolist(),
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_mapped.py",
                "report_fold_coupling.py",
                "report_fold_reservoir.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        cases=cases,
        refinement=dict(
            dt_s=[0.02, 0.01],
            residuals_j=[cases["half_port"]["max_total_residual_j"], fine["max_total_residual_j"]],
            coordinate_differences_by_module=[
                np.abs(
                    np.array(cases["half_port"]["final_state"][i : i + 4])
                    - fine["final_state"][i : i + 4]
                ).tolist()
                for i in (0, 9)
            ],
        ),
        geometric_mass_scaling_validated=False,
        physical_recursive_assembly_validated=False,
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
