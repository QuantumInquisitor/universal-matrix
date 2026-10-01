"""Replay embedded parent histories to separate upstream drive from downstream loading."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, vector
    from .report_fold_material_depth3 import initial_state as full_initial_state
    from .report_fold_material_depth3 import measure as full_measure
    from .report_fold_material_depth3 import rhs as full_rhs
    from .report_fold_material_depth3 import subtree_members, tree_configuration
    from .report_fold_recursive_pair_dynamics import sample_reference_time, simulate_pair
    from .report_fold_scale_extension import connector, mechanical
    from .report_fold_scale_extension import rhs as body_rhs
except ImportError:
    from report_fold_dynamics import Q0, vector
    from report_fold_material_depth3 import initial_state as full_initial_state
    from report_fold_material_depth3 import measure as full_measure
    from report_fold_material_depth3 import rhs as full_rhs
    from report_fold_material_depth3 import subtree_members, tree_configuration
    from report_fold_recursive_pair_dynamics import sample_reference_time, simulate_pair
    from report_fold_scale_extension import connector, mechanical
    from report_fold_scale_extension import rhs as body_rhs


DT_S = 0.0005
DURATION_S = 0.1
SAMPLE_TIMES_S = (0.02, 0.05, 0.075, 0.1)
REPRESENTATIVE = {
    1: {"parent": 0, "child": 1, "parent_scale": 1.0},
    2: {"parent": 1, "child": 3, "parent_scale": 0.5},
    3: {"parent": 3, "child": 7, "parent_scale": 0.25},
}


def capture_full_tree():
    cfg = tree_configuration(3)
    sizes, edges = cfg["sizes"], cfg["edges"]
    groups = subtree_members(len(sizes))
    y = full_initial_state(sizes, edges)
    e0, u0, _, _, groups0 = full_measure(y, sizes, edges, groups)
    node_max = np.zeros(len(sizes))
    edge_max = np.zeros(len(edges))
    group_max = dict.fromkeys(groups0, 0.0)
    trace = []

    def audit(state, time_s):
        energy, potential, incident, works, accounts = full_measure(
            state, sizes, edges, groups
        )
        blocks = state[: 5 * len(sizes)].reshape(len(sizes), 5)
        node_residual = energy - e0 + blocks[:, 4] - incident
        edge_residual = potential - u0 + works.sum(axis=1)
        node_max[:] = np.maximum(node_max, np.abs(node_residual))
        edge_max[:] = np.maximum(edge_max, np.abs(edge_residual))
        for key, account in accounts.items():
            residual = (
                account["accounted_energy_j"]
                - groups0[key]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
            group_max[key] = max(group_max[key], abs(residual))
        trace.append(
            {
                "time_s": float(time_s),
                "q": blocks[:, :2].tolist(),
                "rates": blocks[:, 2:4].tolist(),
                "edge_work_j": works.tolist(),
                "edge_potential_j": potential.tolist(),
            }
        )

    audit(y, 0.0)
    steps = round(DURATION_S / DT_S)
    for step in range(steps):
        a = full_rhs(y, sizes, edges)
        b = full_rhs(y + DT_S * a / 2, sizes, edges)
        c = full_rhs(y + DT_S * b / 2, sizes, edges)
        d = full_rhs(y + DT_S * c, sizes, edges)
        y += DT_S * (a + 2 * b + 2 * c + d) / 6
        audit(y, (step + 1) * DT_S)

    return {
        "settings": {**cfg, "dt_s": DT_S, "duration_s": DURATION_S},
        "trace": trace,
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max.tolist(),
        "max_group_residual_j": group_max,
    }


def hermite_parent(full_run, node, time_s):
    trace = full_run["trace"]
    dt = full_run["settings"]["dt_s"]
    position = time_s / dt
    lower = int(np.floor(position))
    upper = int(np.ceil(position))
    if lower < 0 or upper >= len(trace):
        raise ValueError("parent replay time outside captured trace")
    if lower == upper or np.isclose(position, lower, rtol=0, atol=1e-14):
        return (
            np.asarray(trace[lower]["q"][node]),
            np.asarray(trace[lower]["rates"][node]),
        )
    alpha = position - lower
    h = dt
    q0 = np.asarray(trace[lower]["q"][node])
    q1 = np.asarray(trace[upper]["q"][node])
    v0 = np.asarray(trace[lower]["rates"][node])
    v1 = np.asarray(trace[upper]["rates"][node])
    u = alpha
    h00 = 2 * u**3 - 3 * u**2 + 1
    h10 = u**3 - 2 * u**2 + u
    h01 = -2 * u**3 + 3 * u**2
    h11 = u**3 - u**2
    q = h00 * q0 + h10 * h * v0 + h01 * q1 + h11 * h * v1
    dh00 = 6 * u**2 - 6 * u
    dh10 = 3 * u**2 - 4 * u + 1
    dh01 = -6 * u**2 + 6 * u
    dh11 = 3 * u**2 - 2 * u
    v = (dh00 * q0 + dh10 * h * v0 + dh01 * q1 + dh11 * h * v1) / h
    return q, v


def replay_configuration(child_level, loaded):
    if type(child_level) is not int or child_level not in (1, 2, 3):
        raise ValueError("child level must be 1, 2 or 3")
    if type(loaded) is not bool:
        raise ValueError("loaded must be boolean")
    child_scale = REPRESENTATIVE[child_level]["parent_scale"] / 2
    remaining_depth = 3 - child_level if loaded else 0
    levels = []
    for level in range(remaining_depth + 1):
        levels.extend([level] * (2**level))
    sizes = tuple(child_scale * 0.5**level for level in levels)
    edges = tuple(((child - 1) // 2, child, 1.0) for child in range(1, len(sizes)))
    return {
        "child_level": child_level,
        "loaded": loaded,
        "remaining_depth": remaining_depth,
        "levels": tuple(levels),
        "sizes": sizes,
        "edges": edges,
    }


def replay_initial_state(cfg):
    blocks = np.zeros((len(cfg["sizes"]), 5))
    blocks[:, :2] = Q0
    return np.r_[blocks.ravel(), np.zeros(2 * len(cfg["edges"]) + 2)]


def replay_rhs(time_s, y, cfg, full_run):
    sizes, edges = cfg["sizes"], cfg["edges"]
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges) + 2, "recursive replay state")
    blocks = y[: 5 * n].reshape(n, 5)
    result = np.zeros_like(y)
    forces = np.zeros((n, 2))
    masses = []

    for index, (block, size) in enumerate(zip(blocks, sizes, strict=True)):
        result[5 * index : 5 * index + 5] = body_rhs(block, size)
        masses.append(mechanical(block[:2], block[2:4], size)[0]["mass_matrix"])

    for edge_index, (a, b, weight) in enumerate(edges):
        _, fa, fb = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], weight)
        forces[a] += fa
        forces[b] += fb
        result[5 * n + 2 * edge_index : 5 * n + 2 * edge_index + 2] = [
            fa @ blocks[a, 2:4],
            fb @ blocks[b, 2:4],
        ]

    rep = REPRESENTATIVE[cfg["child_level"]]
    parent_q, parent_v = hermite_parent(full_run, rep["parent"], time_s)
    _, parent_force, child_force = connector(
        parent_q,
        blocks[0, :2],
        rep["parent_scale"],
        sizes[0],
    )
    forces[0] += child_force

    for index in range(n):
        result[5 * index + 2 : 5 * index + 4] += np.linalg.solve(
            masses[index], forces[index]
        )

    result[-2:] = [
        parent_force @ parent_v,
        child_force @ blocks[0, 2:4],
    ]
    return result


def replay_measure(time_s, y, cfg, full_run):
    sizes, edges = cfg["sizes"], cfg["edges"]
    n = len(sizes)
    blocks = y[: 5 * n].reshape(n, 5)
    internal_works = y[5 * n : 5 * n + 2 * len(edges)].reshape(len(edges), 2)
    external_work = y[-2:]
    energies = np.asarray(
        [
            mechanical(block[:2], block[2:4], sizes[index])[2]
            for index, block in enumerate(blocks)
        ]
    )
    internal_potential = np.asarray(
        [
            connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], weight)[0]
            for a, b, weight in edges
        ]
    )
    rep = REPRESENTATIVE[cfg["child_level"]]
    parent_q, _ = hermite_parent(full_run, rep["parent"], time_s)
    external_potential = connector(
        parent_q,
        blocks[0, :2],
        rep["parent_scale"],
        sizes[0],
    )[0]
    return {
        "blocks": blocks,
        "mechanical_j": energies,
        "internal_potential_j": internal_potential,
        "internal_work_j": internal_works,
        "external_potential_j": external_potential,
        "external_work_j": external_work,
    }


def simulate_replay(child_level, loaded, full_run):
    cfg = replay_configuration(child_level, loaded)
    y = replay_initial_state(cfg)
    initial = replay_measure(0.0, y, cfg, full_run)
    initial_total = float(
        initial["mechanical_j"].sum()
        + initial["internal_potential_j"].sum()
        + initial["external_potential_j"]
    )
    max_balance = 0.0
    samples = []
    sample_steps = {round(time / DT_S): time for time in SAMPLE_TIMES_S}

    def audit(state, step):
        nonlocal max_balance
        time_s = step * DT_S
        row = replay_measure(time_s, state, cfg, full_run)
        total = float(
            row["mechanical_j"].sum()
            + row["blocks"][:, 4].sum()
            + row["internal_potential_j"].sum()
            + row["external_potential_j"]
        )
        residual = total - initial_total + row["external_work_j"][0]
        max_balance = max(max_balance, abs(residual))
        if step in sample_steps:
            parent_work, child_work = row["external_work_j"]
            fraction = None if abs(parent_work) == 0 else abs(child_work) / abs(parent_work)
            samples.append(
                {
                    "time_s": sample_steps[step],
                    "root_q": row["blocks"][0, :2].tolist(),
                    "root_rates": row["blocks"][0, 2:4].tolist(),
                    "external_parent_work_j": float(parent_work),
                    "external_child_work_j": float(child_work),
                    "external_child_work_fraction": fraction,
                    "external_potential_j": float(row["external_potential_j"]),
                    "energy_balance_residual_j": float(residual),
                }
            )

    audit(y, 0)
    steps = round(DURATION_S / DT_S)
    for step in range(steps):
        time_s = step * DT_S
        a = replay_rhs(time_s, y, cfg, full_run)
        b = replay_rhs(time_s + DT_S / 2, y + DT_S * a / 2, cfg, full_run)
        c = replay_rhs(time_s + DT_S / 2, y + DT_S * b / 2, cfg, full_run)
        d = replay_rhs(time_s + DT_S, y + DT_S * c, cfg, full_run)
        y += DT_S * (a + 2 * b + 2 * c + d) / 6
        audit(y, step + 1)

    return {
        "settings": cfg,
        "samples": samples,
        "max_energy_balance_residual_j": max_balance,
        "final_state": y.tolist(),
    }


def embedded_sample(full_run, child_level, time_s):
    rep = REPRESENTATIVE[child_level]
    index = round(time_s / full_run["settings"]["dt_s"])
    row = full_run["trace"][index]
    edge_index = rep["child"] - 1
    parent_work, child_work = row["edge_work_j"][edge_index]
    fraction = None if abs(parent_work) == 0 else abs(child_work) / abs(parent_work)
    return {
        "time_s": time_s,
        "child_q": row["q"][rep["child"]],
        "child_rates": row["rates"][rep["child"]],
        "parent_work_j": parent_work,
        "child_work_j": child_work,
        "child_work_fraction": fraction,
        "connector_potential_j": row["edge_potential_j"][edge_index],
    }


def _sample(run, time_s):
    return next(row for row in run["samples"] if row["time_s"] == time_s)


def report():
    full = capture_full_tree()
    isolated_pairs = {str(scale): simulate_pair(scale) for scale in (1.0, 0.5, 0.25)}
    cases = {}
    for child_level in (1, 2, 3):
        free = simulate_replay(child_level, False, full)
        loaded = simulate_replay(child_level, True, full)
        parent_scale = REPRESENTATIVE[child_level]["parent_scale"]
        isolated = isolated_pairs[str(parent_scale)]
        comparisons = {}
        for time_s in SAMPLE_TIMES_S:
            free_row = _sample(free, time_s)
            loaded_row = _sample(loaded, time_s)
            embedded = embedded_sample(full, child_level, time_s)
            isolated_row = sample_reference_time(isolated, time_s / parent_scale)
            isolated_fraction = isolated_row["child_work_fraction_of_parent_magnitude"]
            comparisons[str(time_s)] = {
                "isolated_fraction": isolated_fraction,
                "free_replay_fraction": free_row["external_child_work_fraction"],
                "loaded_replay_fraction": loaded_row["external_child_work_fraction"],
                "embedded_fraction": embedded["child_work_fraction"],
                "upstream_history_factor": (
                    None
                    if isolated_fraction in (None, 0)
                    else free_row["external_child_work_fraction"] / isolated_fraction
                ),
                "downstream_loading_factor": (
                    None
                    if free_row["external_child_work_fraction"] in (None, 0)
                    else loaded_row["external_child_work_fraction"]
                    / free_row["external_child_work_fraction"]
                ),
                "replay_to_embedded_fraction_ratio": (
                    None
                    if embedded["child_work_fraction"] in (None, 0)
                    else loaded_row["external_child_work_fraction"]
                    / embedded["child_work_fraction"]
                ),
                "loaded_root_coordinate_error": float(
                    np.max(
                        np.abs(
                            np.asarray(loaded_row["root_q"])
                            - np.asarray(embedded["child_q"])
                        )
                    )
                ),
                "loaded_root_rate_error": float(
                    np.max(
                        np.abs(
                            np.asarray(loaded_row["root_rates"])
                            - np.asarray(embedded["child_rates"])
                        )
                    )
                ),
            }
        cases[str(child_level)] = {
            "parent_scale": parent_scale,
            "free": {
                "max_energy_balance_residual_j": free["max_energy_balance_residual_j"],
            },
            "loaded": {
                "max_energy_balance_residual_j": loaded["max_energy_balance_residual_j"],
            },
            "comparisons": comparisons,
        }

    return {
        "schema": 1,
        "scope": (
            "causal replay of actual embedded parent trajectories into free-child and "
            "downstream-loaded recursive interfaces under unchanged laws"
        ),
        "sample_times_s": SAMPLE_TIMES_S,
        "full_tree_energy": {
            "max_node_residual_j": full["max_node_residual_j"],
            "max_edge_residual_j": full["max_edge_residual_j"],
            "max_group_residual_j": full["max_group_residual_j"],
        },
        "cases": cases,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_drive_load_replay.py",
                "report_fold_recursive_pair_dynamics.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "parent_trajectory_prescribed_from_full_tree": True,
        "connector_coefficients_changed": False,
        "material_scaling_law_changed": False,
        "new_recursive_coupling_introduced": False,
        "global_spatial_embedding_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
