"""Compare isolated recursive pairs with the same interfaces embedded in the depth-three tree."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0, vector
    from .report_fold_material_depth_backreaction import simulate as simulate_embedded_tree
    from .report_fold_scale_extension import (
        audit_scale,
        connector,
        mechanical,
        rhs as body_rhs,
    )
except ImportError:
    from report_fold_dynamics import Q0, vector
    from report_fold_material_depth_backreaction import simulate as simulate_embedded_tree
    from report_fold_scale_extension import audit_scale, connector, mechanical
    from report_fold_scale_extension import rhs as body_rhs


PARENT_SCALES = (1.0, 0.5, 0.25)
REFERENCE_DT_S = 0.002
REFERENCE_DURATION_S = 0.4
REFERENCE_SAMPLE_TIMES_S = (0.02, 0.05, 0.1, 0.2, 0.3, 0.4)
EMBEDDED_PHYSICAL_TIMES_S = (0.02, 0.05, 0.075, 0.1)


def pair_sizes(parent_scale):
    parent = audit_scale(parent_scale)
    if parent not in PARENT_SCALES:
        raise ValueError("parent scale must be one of the tested recursive interfaces")
    child = audit_scale(parent / 2)
    return parent, child


def initial_state(parent_scale):
    parent, _ = pair_sizes(parent_scale)
    return np.r_[
        Q0 + (0.005, -0.008),
        np.array((0.002, 0.004)) / parent,
        0.0,
        Q0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]


def rhs(y, parent_scale):
    parent, child = pair_sizes(parent_scale)
    y = vector(y, 12, "recursive isolated pair state")
    blocks = y[:10].reshape(2, 5)
    _, parent_force, child_force = connector(blocks[0, :2], blocks[1, :2], parent, child)
    result = np.zeros(12)
    for index, (scale, force) in enumerate(((parent, parent_force), (child, child_force))):
        derivative = body_rhs(blocks[index], scale)
        mass = mechanical(blocks[index, :2], blocks[index, 2:4], scale)[0]["mass_matrix"]
        derivative[2:4] += np.linalg.solve(mass, force)
        result[5 * index : 5 * index + 5] = derivative
        result[10 + index] = force @ blocks[index, 2:4]
    return result


def measure(y, parent_scale):
    parent, child = pair_sizes(parent_scale)
    y = vector(y, 12, "recursive isolated pair state")
    blocks = y[:10].reshape(2, 5)
    energies = np.asarray(
        [
            mechanical(blocks[0, :2], blocks[0, 2:4], parent)[2],
            mechanical(blocks[1, :2], blocks[1, 2:4], child)[2],
        ]
    )
    potential = connector(blocks[0, :2], blocks[1, :2], parent, child)[0]
    return energies, potential


def simulate_pair(parent_scale, *, refinement=1):
    parent, child = pair_sizes(parent_scale)
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    reference_dt = REFERENCE_DT_S / refinement
    steps = round(REFERENCE_DURATION_S / reference_dt)
    dt = parent * reference_dt
    y = initial_state(parent)
    e0, u0 = measure(y, parent)
    total0 = float(e0.sum() + u0)
    trace = []

    for step in range(steps + 1):
        energies, potential = measure(y, parent)
        blocks = y[:10].reshape(2, 5)
        works = y[10:].copy()
        parent_work = float(works[0])
        child_work = float(works[1])
        fraction = None if abs(parent_work) == 0 else abs(child_work) / abs(parent_work)
        trace.append(
            {
                "time_s": step * dt,
                "reference_time_s": step * reference_dt,
                "q": blocks[:, :2].tolist(),
                "rates": blocks[:, 2:4].tolist(),
                "mechanical_j": energies.tolist(),
                "damping_loss_j": blocks[:, 4].tolist(),
                "connector_j": float(potential),
                "endpoint_work_j": works.tolist(),
                "child_work_fraction_of_parent_magnitude": fraction,
                "module_residual_j": (
                    energies - e0 + blocks[:, 4] - works
                ).tolist(),
                "connector_residual_j": float(potential - u0 + works.sum()),
                "total_residual_j": float(
                    energies.sum() + blocks[:, 4].sum() + potential - total0
                ),
            }
        )
        if step == steps:
            break
        a = rhs(y, parent)
        b = rhs(y + dt * a / 2, parent)
        c = rhs(y + dt * b / 2, parent)
        d = rhs(y + dt * c, parent)
        y += dt * (a + 2 * b + 2 * c + d) / 6

    return {
        "settings": {
            "parent_scale": parent,
            "child_scale": child,
            "reference_dt_s": reference_dt,
            "physical_dt_s": dt,
            "reference_duration_s": REFERENCE_DURATION_S,
            "physical_duration_s": parent * REFERENCE_DURATION_S,
            "refinement": refinement,
        },
        "trace": trace,
        "max_module_residual_j": max(
            max(abs(value) for value in row["module_residual_j"]) for row in trace
        ),
        "max_connector_residual_j": max(abs(row["connector_residual_j"]) for row in trace),
        "max_total_residual_j": max(abs(row["total_residual_j"]) for row in trace),
    }


def sample_reference_time(run, reference_time):
    index = round(reference_time / run["settings"]["reference_dt_s"])
    row = run["trace"][index]
    if not np.isclose(row["reference_time_s"], reference_time, rtol=0, atol=1e-14):
        raise ValueError("requested reference time is off-grid")
    return row


def similarity(run, reference):
    parent = run["settings"]["parent_scale"]
    if reference["settings"]["parent_scale"] != 1.0:
        raise ValueError("reference pair must have unit parent scale")
    times = [row["reference_time_s"] for row in run["trace"]]
    if times != [row["reference_time_s"] for row in reference["trace"]]:
        raise ValueError("pair comparison requires matching reference-time grids")
    q = np.asarray([row["q"] for row in run["trace"]])
    q0 = np.asarray([row["q"] for row in reference["trace"]])
    rate = np.asarray([row["rates"] for row in run["trace"]])
    rate0 = np.asarray([row["rates"] for row in reference["trace"]])
    energy = np.asarray(
        [
            row["mechanical_j"] + [row["connector_j"]]
            for row in run["trace"]
        ]
    )
    energy0 = np.asarray(
        [
            row["mechanical_j"] + [row["connector_j"]]
            for row in reference["trace"]
        ]
    )
    works = np.asarray([row["endpoint_work_j"] for row in run["trace"]])
    works0 = np.asarray([row["endpoint_work_j"] for row in reference["trace"]])
    return {
        "coordinate_max_difference": float(np.max(np.abs(q - q0))),
        "rescaled_rate_max_difference": float(np.max(np.abs(parent * rate - rate0))),
        "rescaled_energy_max_difference_j": float(
            np.max(np.abs(energy / parent**3 - energy0))
        ),
        "rescaled_work_max_difference_j": float(
            np.max(np.abs(works / parent**3 - works0))
        ),
    }


def report():
    pairs = {str(scale): simulate_pair(scale) for scale in PARENT_SCALES}
    reference = pairs["1.0"]
    pair_similarity = {
        str(scale): similarity(pairs[str(scale)], reference)
        for scale in PARENT_SCALES
    }

    isolated_samples = {}
    for scale in PARENT_SCALES:
        run = pairs[str(scale)]
        isolated_samples[str(scale)] = {
            str(time): {
                key: sample_reference_time(run, time)[key]
                for key in (
                    "q",
                    "rates",
                    "mechanical_j",
                    "connector_j",
                    "endpoint_work_j",
                    "child_work_fraction_of_parent_magnitude",
                )
            }
            for time in REFERENCE_SAMPLE_TIMES_S
        }

    embedded = simulate_embedded_tree(3)
    embedded_comparison = {}
    for child_level, parent_scale in ((1, 1.0), (2, 0.5), (3, 0.25)):
        rows = {}
        isolated = pairs[str(parent_scale)]
        for snapshot in embedded["snapshots"]:
            physical_time = snapshot["time_s"]
            if physical_time not in EMBEDDED_PHYSICAL_TIMES_S:
                continue
            reference_time = physical_time / parent_scale
            isolated_row = sample_reference_time(isolated, reference_time)
            embedded_row = snapshot["edge_levels"][str(child_level)]
            isolated_fraction = isolated_row["child_work_fraction_of_parent_magnitude"]
            embedded_fraction = embedded_row["child_uptake_fraction_of_parent_magnitude"]
            rows[str(physical_time)] = {
                "parent_scale": parent_scale,
                "reference_time_s": reference_time,
                "isolated_child_work_fraction": isolated_fraction,
                "embedded_child_work_fraction": embedded_fraction,
                "embedded_to_isolated_fraction_ratio": (
                    None
                    if isolated_fraction in (None, 0) or embedded_fraction is None
                    else embedded_fraction / isolated_fraction
                ),
                "isolated_endpoint_work_j": isolated_row["endpoint_work_j"],
                "embedded_parent_endpoint_work_j": embedded_row["parent_endpoint_work_j"],
                "embedded_child_endpoint_work_j": embedded_row["child_endpoint_work_j"],
                "embedded_potential_change_j": embedded_row["potential_change_j"],
            }
        embedded_comparison[str(child_level)] = rows

    fine = simulate_pair(0.25, refinement=2)
    coarse_final = np.asarray(pairs["0.25"]["trace"][-1]["q"] + pairs["0.25"]["trace"][-1]["rates"])
    fine_final = np.asarray(fine["trace"][-1]["q"] + fine["trace"][-1]["rates"])

    return {
        "schema": 1,
        "scope": (
            "isolated 1:2 recursive pair dynamics at parent scales 1, 1/2 and 1/4 "
            "compared at corresponding reference times and against embedded full-tree interfaces"
        ),
        "reference_sample_times_s": REFERENCE_SAMPLE_TIMES_S,
        "embedded_physical_times_s": EMBEDDED_PHYSICAL_TIMES_S,
        "pairs": {
            scale: {
                "settings": run["settings"],
                "max_module_residual_j": run["max_module_residual_j"],
                "max_connector_residual_j": run["max_connector_residual_j"],
                "max_total_residual_j": run["max_total_residual_j"],
            }
            for scale, run in pairs.items()
        },
        "pair_similarity": pair_similarity,
        "isolated_samples": isolated_samples,
        "embedded_comparison": embedded_comparison,
        "quarter_to_eighth_refinement_max_state_difference": float(
            np.max(np.abs(coarse_final - fine_final))
        ),
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_pair_dynamics.py",
                "report_fold_scale_extension.py",
                "report_fold_material_depth_backreaction.py",
                "report_fold_material_depth3.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "connector_coefficients_changed": False,
        "material_scaling_law_changed": False,
        "production_scale_guard_changed": False,
        "isolated_pair_similarity_expected": True,
        "embedded_loading_equated_with_isolated_pair": False,
        "new_recursive_coupling_introduced": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
