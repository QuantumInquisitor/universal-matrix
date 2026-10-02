"""Passive unequal-sized modules with a consistently scaled mapped connector."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, vector
    from .report_fold_kinematics import scalar
    from .report_fold_mapped import PORT_STIFFNESS, port
    from .report_fold_scaling import rhs as body_rhs
    from .report_fold_scaling import scale_value, scaled_mechanical
except ImportError:
    from report_fold_dynamics import Q0, vector
    from report_fold_kinematics import scalar
    from report_fold_mapped import PORT_STIFFNESS, port
    from report_fold_scaling import rhs as body_rhs
    from report_fold_scaling import scale_value, scaled_mechanical


def sizes(scale, ratio):
    scale, ratio = scale_value(scale), scalar(ratio, "relative child size")
    if not 0.25 <= ratio <= 1:
        raise ValueError("relative size outside [.25,1]")
    return scale, scale_value(scale * ratio)


def connector(qa, qb, scale=1.0, ratio=0.5, *, fixed_stiffness=False):
    a, b = sizes(scale, ratio)
    pa, ja = port(qa, 0.1 * a)
    pb, jb = port(qb, 0.1 * b)
    delta = pa - pb
    force = (1 if fixed_stiffness else a) * PORT_STIFFNESS @ delta
    return float(delta @ force / 2), -ja.T @ force, jb.T @ force


def initial_state(scale=1.0, ratio=0.5):
    sizes(scale, ratio)
    return np.r_[
        Q0 + (0.005, -0.008), np.array((0.002, 0.004)) / scale, 0.0, Q0, 0.0, 0.0, 0.0, 0.0, 0.0
    ]


def rhs(y, scale=1.0, ratio=0.5, *, fixed_stiffness=False):
    scales = sizes(scale, ratio)
    y = vector(y, 12, "scaled pair state")
    blocks = y[:10].reshape(2, 5)
    _, fa, fb = connector(
        blocks[0, :2], blocks[1, :2], scale, ratio, fixed_stiffness=fixed_stiffness
    )
    result = np.zeros(12)
    for i, force in enumerate((fa, fb)):
        derivative = body_rhs(blocks[i], scales[i])
        mass = scaled_mechanical(blocks[i, :2], blocks[i, 2:4], scales[i])[0]["mass_matrix"]
        derivative[2:4] += np.linalg.solve(mass, force)
        result[5 * i : 5 * i + 5] = derivative
        result[10 + i] = force @ blocks[i, 2:4]
    return result


def measure(y, scale=1.0, ratio=0.5, *, fixed_stiffness=False):
    scales = sizes(scale, ratio)
    blocks = np.asarray(y[:10]).reshape(2, 5)
    energies = np.array(
        [scaled_mechanical(b[:2], b[2:4], scales[i])[2] for i, b in enumerate(blocks)]
    )
    potential = connector(
        blocks[0, :2], blocks[1, :2], scale, ratio, fixed_stiffness=fixed_stiffness
    )[0]
    return energies, potential, float(sum(energies) + sum(blocks[:, 4]) + potential)


def simulate(scale=1.0, ratio=0.5, *, fixed_stiffness=False, refinement=1):
    scale, child = sizes(scale, ratio)
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    dt = 0.01 * scale / refinement
    y = initial_state(scale, ratio)
    snapshot = y.tolist()
    settings = dict(scale=scale, ratio=ratio, fixed_stiffness=fixed_stiffness)
    e0, u0, total0 = measure(y, **settings)
    trace = []
    for step in range(100 * refinement + 1):
        derivative = rhs(y, **settings)
        energies, potential, total = measure(y, **settings)
        blocks = y[:10].reshape(2, 5)
        trace.append(
            dict(
                time_s=step * dt,
                reference_time_s=step * 0.01 / refinement,
                q=blocks[:, :2].tolist(),
                rates=blocks[:, 2:4].tolist(),
                mechanical_j=energies.tolist(),
                damping_loss_j=blocks[:, 4].tolist(),
                connector_j=potential,
                connector_work_j=y[10:].tolist(),
                module_residual_j=(energies - e0 + blocks[:, 4] - y[10:]).tolist(),
                connector_residual_j=float(potential - u0 + sum(y[10:])),
                total_residual_j=total - total0,
            )
        )
        if step == 100 * refinement:
            break
        a = derivative
        b = rhs(y + dt * a / 2, **settings)
        c = rhs(y + dt * b / 2, **settings)
        d = rhs(y + dt * c, **settings)
        y = y + dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        settings=dict(
            parent_scale=scale,
            child_scale=child,
            relative_size=ratio,
            dt_s=dt,
            duration_s=scale,
            fixed_stiffness=fixed_stiffness,
        ),
        initial_state=snapshot,
        final_state=y.tolist(),
        max_total_residual_j=max(abs(r["total_residual_j"]) for r in trace),
        max_module_residual_j=max(max(map(abs, r["module_residual_j"])) for r in trace),
        max_connector_residual_j=max(abs(r["connector_residual_j"]) for r in trace),
        trace=trace,
    )


def comparison(run, reference):
    """Compare internally generated runs on matching reference-time grids."""
    if reference["settings"]["parent_scale"] != 1:
        raise ValueError("reference must have unit parent scale")
    times = [r["reference_time_s"] for r in run["trace"]]
    if times != [r["reference_time_s"] for r in reference["trace"]]:
        raise ValueError("comparison requires matching reference-time grids")
    if run["settings"]["relative_size"] != reference["settings"]["relative_size"]:
        raise ValueError("comparison requires equal relative body sizes")
    scale = run["settings"]["parent_scale"]
    q = np.array([r["q"] for r in run["trace"]])
    qr = np.array([r["q"] for r in reference["trace"]])
    v = np.array([r["rates"] for r in run["trace"]])
    vr = np.array([r["rates"] for r in reference["trace"]])
    e = np.array([r["mechanical_j"] + [r["connector_j"]] for r in run["trace"]])
    er = np.array([r["mechanical_j"] + [r["connector_j"]] for r in reference["trace"]])
    return dict(
        coordinate_max_differences=np.max(abs(q - qr), axis=0).tolist(),
        rescaled_rate_max_differences=np.max(abs(scale * v - vr), axis=0).tolist(),
        rescaled_energy_max_difference_j=float(np.max(abs(e / scale**3 - er))),
    )


def report():
    reference = simulate()
    cases = {}
    for name, scale, fixed in [
        ("reference", 1.0, False),
        ("three_quarters", 0.75, False),
        ("half", 0.5, False),
        ("fixed_stiffness_comparison", 0.5, True),
    ]:
        run = reference if name == "reference" else simulate(scale, fixed_stiffness=fixed)
        compare = comparison(run, reference)
        cases[name] = {k: v for k, v in run.items() if k != "trace"}
        cases[name]["samples"] = run["trace"][::20]
        cases[name]["similarity"] = compare
    fine = simulate(0.5, refinement=2)
    coarse = cases["half"]
    return dict(
        schema=1,
        scope="Conditional uniform scaling of a passive pair with fixed relative child size .5; no active reservoir or recursive assembly",
        sources={
            name: hashlib.sha256(
                Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in (
                "report_fold_scaled_pair.py",
                "report_fold_scaling.py",
                "report_fold_mapped.py",
                "report_fold_coupling.py",
                "report_fold_reservoir.py",
                "report_fold_dynamics.py",
                "report_fold_kinematics.py",
            )
        },
        cases=cases,
        refinement=dict(
            residuals_j=[coarse["max_total_residual_j"], fine["max_total_residual_j"]],
            component_columns=["scale", "angle_rad", "scale_rate_per_s", "angle_rate_rad_per_s"],
            state_component_differences_by_module=[
                np.abs(
                    np.array(coarse["final_state"][i : i + 4]) - fine["final_state"][i : i + 4]
                ).tolist()
                for i in (0, 5)
            ],
        ),
        calibrated_material=False,
        recursive_assembly_validated=False,
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
