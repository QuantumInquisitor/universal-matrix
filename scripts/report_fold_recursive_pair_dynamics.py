"""Dynamic self-similarity audit for isolated recursive parent-child pairs."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0
    from .report_fold_material_depth3 import rhs
    from .report_fold_scale_extension import connector, mechanical
except ImportError:
    from report_fold_dynamics import Q0
    from report_fold_material_depth3 import rhs
    from report_fold_scale_extension import connector, mechanical


PARENT_SCALES = (1.0, 0.5, 0.25)
REFERENCE_DURATION_S = 0.1
REFERENCE_DT_S = 0.0005
REFERENCE_SAMPLE_TIMES_S = (0.0, 0.02, 0.05, 0.075, 0.1)
ROOT_DISPLACEMENT = np.array((0.005, -0.008))
ROOT_RATE = np.array((0.002, 0.004))


def initial_state(parent_scale):
    if parent_scale not in PARENT_SCALES:
        raise ValueError("parent scale must be one of the tested interfaces")
    blocks = np.zeros((2, 5))
    blocks[:, :2] = Q0
    blocks[0, :2] = np.asarray(Q0) + ROOT_DISPLACEMENT
    blocks[0, 2:4] = ROOT_RATE / parent_scale
    return np.r_[blocks.ravel(), np.zeros(2)]


def measure(state, parent_scale):
    child_scale = parent_scale / 2
    blocks = np.asarray(state[:10], dtype=float).reshape(2, 5)
    energies = np.asarray(
        [
            mechanical(blocks[0, :2], blocks[0, 2:4], parent_scale)[2],
            mechanical(blocks[1, :2], blocks[1, 2:4], child_scale)[2],
        ]
    )
    potential = connector(
        blocks[0, :2], blocks[1, :2], parent_scale, child_scale
    )[0]
    works = np.asarray(state[10:12], dtype=float)
    total = float(energies.sum() + blocks[:, 4].sum() + potential)
    return energies, float(potential), works, total


def simulate(parent_scale):
    if parent_scale not in PARENT_SCALES:
        raise ValueError("parent scale must be one of the tested interfaces")
    sizes = (parent_scale, parent_scale / 2)
    edges = ((0, 1, 1.0),)
    dt = parent_scale * REFERENCE_DT_S
    duration = parent_scale * REFERENCE_DURATION_S
    steps = round(duration / dt)
    y = initial_state(parent_scale)
    e0, u0, w0, total0 = measure(y, parent_scale)
    node_max = np.zeros(2)
    edge_max = 0.0
    total_max = 0.0
    sample_steps = {
        round(reference_time / REFERENCE_DT_S): reference_time
        for reference_time in REFERENCE_SAMPLE_TIMES_S
    }
    snapshots = []

    def audit(state, step):
        nonlocal edge_max, total_max
        energy, potential, works, total = measure(state, parent_scale)
        blocks = state[:10].reshape(2, 5)
        node_residual = energy - e0 + blocks[:, 4] - (works - w0)
        edge_residual = potential - u0 + float((works - w0).sum())
        total_residual = total - total0
        node_max[:] = np.maximum(node_max, np.abs(node_residual))
        edge_max = max(edge_max, abs(edge_residual))
        total_max = max(total_max, abs(total_residual))
        if step in sample_steps:
            parent_work = float(works[0] - w0[0])
            child_work = float(works[1] - w0[1])
            snapshots.append(
                {
                    "reference_time_s": sample_steps[step],
                    "physical_time_s": step * dt,
                    "q": blocks[:, :2].tolist(),
                    "scale_normalized_rates": (
                        parent_scale * blocks[:, 2:4]
                    ).tolist(),
                    "mechanical_energy_over_parent_s3": (
                        energy / parent_scale**3
                    ).tolist(),
                    "loss_over_parent_s3": (
                        blocks[:, 4] / parent_scale**3
                    ).tolist(),
                    "connector_potential_over_parent_s3": potential
                    / parent_scale**3,
                    "endpoint_work_over_parent_s3": (
                        (works - w0) / parent_scale**3
                    ).tolist(),
                    "child_uptake_fraction_of_parent_magnitude": (
                        None
                        if parent_work == 0
                        else abs(child_work) / abs(parent_work)
                    ),
                }
            )

    audit(y, 0)
    for step in range(steps):
        a = rhs(y, sizes, edges)
        b = rhs(y + dt * a / 2, sizes, edges)
        c = rhs(y + dt * b / 2, sizes, edges)
        d = rhs(y + dt * c, sizes, edges)
        y += dt * (a + 2 * b + 2 * c + d) / 6
        audit(y, step + 1)

    return {
        "parent_scale": parent_scale,
        "child_scale": parent_scale / 2,
        "physical_duration_s": duration,
        "physical_dt_s": dt,
        "reference_duration_s": REFERENCE_DURATION_S,
        "reference_dt_s": REFERENCE_DT_S,
        "snapshots": snapshots,
        "final_state": y.tolist(),
        "max_node_residual_j": node_max.tolist(),
        "max_edge_residual_j": edge_max,
        "max_total_residual_j": total_max,
    }


def _snapshot_arrays(run, key):
    return np.asarray([row[key] for row in run["snapshots"]], dtype=float)


def report():
    runs = {str(scale): simulate(scale) for scale in PARENT_SCALES}
    reference = runs["1.0"]
    comparisons = {}
    for scale in PARENT_SCALES:
        run = runs[str(scale)]
        comparisons[str(scale)] = {
            "coordinate_max_difference": float(
                np.max(np.abs(_snapshot_arrays(run, "q") - _snapshot_arrays(reference, "q")))
            ),
            "scale_normalized_rate_max_difference": float(
                np.max(
                    np.abs(
                        _snapshot_arrays(run, "scale_normalized_rates")
                        - _snapshot_arrays(reference, "scale_normalized_rates")
                    )
                )
            ),
            "normalized_mechanical_energy_max_difference": float(
                np.max(
                    np.abs(
                        _snapshot_arrays(run, "mechanical_energy_over_parent_s3")
                        - _snapshot_arrays(reference, "mechanical_energy_over_parent_s3")
                    )
                )
            ),
            "normalized_loss_max_difference": float(
                np.max(
                    np.abs(
                        _snapshot_arrays(run, "loss_over_parent_s3")
                        - _snapshot_arrays(reference, "loss_over_parent_s3")
                    )
                )
            ),
            "normalized_connector_potential_max_difference": float(
                np.max(
                    np.abs(
                        _snapshot_arrays(run, "connector_potential_over_parent_s3")
                        - _snapshot_arrays(reference, "connector_potential_over_parent_s3")
                    )
                )
            ),
            "normalized_endpoint_work_max_difference": float(
                np.max(
                    np.abs(
                        _snapshot_arrays(run, "endpoint_work_over_parent_s3")
                        - _snapshot_arrays(reference, "endpoint_work_over_parent_s3")
                    )
                )
            ),
        }

    final_uptake = {
        str(scale): runs[str(scale)]["snapshots"][-1][
            "child_uptake_fraction_of_parent_magnitude"
        ]
        for scale in PARENT_SCALES
    }
    return {
        "schema": 1,
        "scope": (
            "isolated two-module recursive interface dynamics at corresponding scaled "
            "initial conditions and physical times; existing laws only"
        ),
        "parent_scales": PARENT_SCALES,
        "reference_duration_s": REFERENCE_DURATION_S,
        "reference_dt_s": REFERENCE_DT_S,
        "reference_sample_times_s": REFERENCE_SAMPLE_TIMES_S,
        "runs": runs,
        "comparisons": comparisons,
        "final_child_uptake_fraction_of_parent_magnitude": final_uptake,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_pair_dynamics.py",
                "report_fold_material_depth3.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "connector_coefficients_changed": False,
        "material_scaling_law_changed": False,
        "damping_law_changed": False,
        "embedded_tree_loading_reproduced": False,
        "new_recursive_coupling_introduced": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
