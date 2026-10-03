"""Optional bounded distributed-inertia graph evolution; synthetic material only."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_trapezoid

from scripts.fold_distributed_graph import measure, mechanical
from scripts.fold_material_multiscale import scaled_material
from scripts.report_fold_distributed_trajectories import simulate as reference
from scripts.report_fold_dynamics import DAMPING, vector
from scripts.report_fold_hierarchy import compile_hierarchy
from scripts.report_fold_kinematics import scalar
from scripts.report_fold_material_recursive_tree import recursive_configuration
from scripts.report_fold_multiscale import configuration, connector, initial_state


def rhs(y, sizes, edges, *, damping=1):
    """Same graph equations, evaluating each distributed matrix once per stage."""
    if type(damping) is not int or damping not in (0, 1):
        raise ValueError("damping must be 0 or 1")
    sizes, edges = configuration(sizes, edges)
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "graph state")
    blocks = y[: 5 * n].reshape(n, 5)
    result = np.zeros_like(y)
    forces = np.zeros((n, 2))
    for e, (a, b, w) in enumerate(edges):
        _, fa, fb = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)
        forces[a] += fa
        forces[b] += fb
        result[5 * n + 2 * e : 5 * n + 2 * e + 2] = [fa @ blocks[a, 2:4], fb @ blocks[b, 2:4]]
    for i, block in enumerate(blocks):
        q, v = block[:2], block[2:4]
        state, bias, _ = mechanical(q, v, sizes[i])
        resistance = damping * sizes[i] ** 4 * DAMPING @ v
        gradient = np.asarray(scaled_material(q, sizes[i])["gradient"])
        acceleration = np.linalg.solve(
            state["mass_matrix"], forces[i] - gradient - bias - resistance
        )
        result[5 * i : 5 * i + 5] = np.r_[v, acceleration, v @ resistance]
    return result


def simulate(depth, *, refinement=1, connected=True, damping=1, duration=0.1):
    """Integrate a short passive replicated-material tree with owned energies."""
    if type(depth) is not int or depth not in (0, 1):
        raise ValueError("depth must be 0 or 1")
    if type(damping) is not int or damping not in (0, 1):
        raise ValueError("damping must be 0 or 1")
    cfg = recursive_configuration(depth, connected=connected)
    sizes, edges = cfg["sizes"], cfg["edges"]
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    duration = scalar(duration, "duration")
    dt = 0.001 / refinement
    steps = round(duration / dt)
    if (
        steps < 1
        or not 0 < duration <= 0.1
        or not np.isclose(steps * dt, duration, rtol=0, atol=1e-14)
    ):
        raise ValueError("duration must be complete .001/refinement steps in (0,.1]")

    layout = compile_hierarchy(len(sizes), edges, cfg["tree"])
    y = initial_state(sizes, edges)
    initial = y.copy()
    e0, u0, _, groups0 = measure(y, sizes, edges, layout)
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = dict.fromkeys(groups0, 0.0)
    root_trace = []
    state_trace = []
    total_energy_trace = []
    power_trace = []
    loss_power_trace = []

    def audit(state, time):
        nonlocal node_max, edge_max
        energy, potential, incident, groups = measure(state, sizes, edges, layout)
        blocks = state[: 5 * len(sizes)].reshape(len(sizes), 5)
        work = state[5 * len(sizes) :].reshape(len(edges), 2)
        node_residual = energy - e0 + blocks[:, 4] - incident
        edge_residual = potential - u0 + work.sum(axis=1)
        node_max = np.maximum(node_max, np.abs(node_residual))
        edge_max = np.maximum(edge_max, np.abs(edge_residual))
        for path, account in groups.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            account["residual_j"] = residual
            group_max[path] = max(group_max[path], abs(residual))
        power_trace.append(
            [
                [fa @ blocks[a, 2:4], fb @ blocks[b, 2:4]]
                for a, b, w in edges
                for _, fa, fb in [connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)]
            ]
        )
        loss_power_trace.append(
            [
                float(b[2:4] @ (damping * sizes[i] ** 4 * DAMPING) @ b[2:4])
                for i, b in enumerate(blocks)
            ]
        )
        state_trace.append(state.tolist())
        total_energy_trace.append(float(sum(energy) + sum(potential)))
        root_trace.append(
            {
                "time_s": time,
                "q": blocks[0, :2].tolist(),
                "rates": blocks[0, 2:4].tolist(),
                "mechanical_j": float(energy[0]),
            }
        )

    audit(y, 0.0)
    for step in range(steps):
        a = rhs(y, sizes, edges, damping=damping)
        b = rhs(y + dt * a / 2, sizes, edges, damping=damping)
        c = rhs(y + dt * b / 2, sizes, edges, damping=damping)
        d = rhs(y + dt * c, sizes, edges, damping=damping)
        y += dt * (a + 2 * b + 2 * c + d) / 6
        audit(y, (step + 1) * dt)

    times = np.arange(steps + 1) * dt
    states = np.asarray(state_trace)
    sampled_loss = cumulative_trapezoid(loss_power_trace, times, axis=0, initial=0)
    loss_error = float(
        np.max(abs(sampled_loss - states[:, : 5 * len(sizes)].reshape(-1, len(sizes), 5)[:, :, 4]))
    )
    work_error = 0.0
    if edges:
        sampled_work = cumulative_trapezoid(power_trace, times, axis=0, initial=0)
        work_error = float(
            np.max(abs(sampled_work - states[:, 5 * len(sizes) :].reshape(-1, len(edges), 2)))
        )
    return {
        "sampled_loss_error_j": loss_error,
        "sampled_work_error_j": work_error,
        "settings": {
            **cfg,
            "dt_s": dt,
            "duration_s": duration,
            "steps": steps,
            "refinement": refinement,
            "damping": damping,
        },
        "initial_state": initial.tolist(),
        "final_state": y.tolist(),
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max.tolist(),
        "max_group_residual_j": group_max,
        "root_trace": root_trace,
        "state_trace": state_trace,
        "total_energy_trace_j": total_energy_trace,
    }


def report():
    cases = {}
    for depth in (0, 1):
        for refinement in (1, 2):
            cases[f"passive_depth_{depth}_r{refinement}"] = simulate(depth, refinement=refinement)
    cases["conservative_depth_1"] = simulate(1, refinement=2, damping=0)
    cases["disconnected_depth_1"] = simulate(1, connected=False)
    fine0 = cases["passive_depth_0_r2"]
    initial = np.asarray(fine0["initial_state"])
    ref = reference(initial=np.r_[initial[:4], 0.0, initial[4]], duration=0.1, samples=201)
    reference_rows = np.asarray([r["q"] + r["rates"] + [r["loss_j"]] for r in ref["trace"]])
    match = float(np.max(abs(np.asarray(fine0["state_trace"]) - reference_rows)))
    refinements = {}
    for depth in (0, 1):
        coarse = cases[f"passive_depth_{depth}_r1"]
        fine = cases[f"passive_depth_{depth}_r2"]
        refinements[str(depth)] = float(
            np.max(abs(np.asarray(coarse["state_trace"]) - np.asarray(fine["state_trace"])[::2]))
        )
    fine1 = cases["passive_depth_1_r2"]
    root_response = float(
        np.max(
            abs(np.asarray(fine1["state_trace"])[:, :4] - np.asarray(fine0["state_trace"])[:, :4])
        )
    )
    work = np.asarray(fine1["state_trace"])[:, 15:].reshape(-1, 2, 2)
    # Deliberately reverse one saved endpoint-work sign: edge ΔU+Wa+Wb then
    # acquires -2*Wb. This tests ledger sign sensitivity, not faulty dynamics.
    wrong_sign_signal = float(np.max(abs(2 * work[:, 0, 1])))
    root = Path(__file__).resolve().parent
    names = [
        "report_fold_distributed_graph_trajectories.py",
        "fold_distributed_graph.py",
        "fold_material_multiscale.py",
        "report_fold_distributed_trajectories.py",
        "report_fold_distributed_inertia.py",
        "report_fold_constitutive.py",
        "report_fold_dynamics.py",
        "report_fold_kinematics.py",
        "report_fold_material_recursive_tree.py",
        "report_fold_multiscale.py",
        "report_fold_hierarchy.py",
        "report_fold_scaling.py",
        "report_fold_mapped.py",
    ]
    result = dict(
        schema="fold-distributed-graph-trajectories-v1",
        cases=cases,
        common_time_refinement_max_abs=refinements,
        dop853_common_time_max_abs=match,
        connected_root_common_time_response=root_response,
        dop853_max_balance_residual_j=ref["maximum_balance_residual_j"],
        wrong_endpoint_work_sign_signal_j=wrong_sign_signal,
        source_hash_encoding="UTF-8/LF",
        sources={
            n: hashlib.sha256((root / n).read_text(encoding="utf-8").encode()).hexdigest()
            for n in names
        },
        depths_tested=[0, 1],
        duration_s=0.1,
        physical_attachments_validated=False,
        depth_convergence_validated=False,
        powered_persistence_validated=False,
        stable_breathing_established=False,
        physical_calibration=False,
        production_dynamics_changed=False,
    )
    validate(result)
    return result


def validate(result):
    for case in result["cases"].values():
        assert max(case["max_node_residual_j"]) < 1e-12
        assert max(case["max_edge_residual_j"], default=0) < 1e-12
        assert max(case["max_group_residual_j"].values()) < 1e-12
        assert np.max(np.diff(case["total_energy_trace_j"])) < 1e-12
    assert max(result["common_time_refinement_max_abs"].values()) < 1e-7
    assert result["dop853_common_time_max_abs"] < 1e-8
    assert result["connected_root_common_time_response"] > 1e-12
    assert result["dop853_max_balance_residual_j"] < 1e-10
    cases = result["cases"]
    for depth in (0, 1):
        coarse, fine = [cases[f"passive_depth_{depth}_r{r}"] for r in (1, 2)]
        assert fine["sampled_loss_error_j"] < coarse["sampled_loss_error_j"]
        if depth:
            assert fine["sampled_work_error_j"] < coarse["sampled_work_error_j"]
    zero = np.asarray(cases["passive_depth_0_r1"]["state_trace"])
    disconnected = np.asarray(cases["disconnected_depth_1"]["state_trace"])[:, :5]
    assert np.max(abs(zero - disconnected)) < 1e-14
    signal = result["wrong_endpoint_work_sign_signal_j"]
    assert signal > 1e-13
    assert signal > 100 * max(cases["passive_depth_1_r2"]["max_edge_residual_j"])


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
                k: result[k]
                for k in (
                    "common_time_refinement_max_abs",
                    "dop853_common_time_max_abs",
                    "wrong_endpoint_work_sign_signal_j",
                )
            }
        )
    )
