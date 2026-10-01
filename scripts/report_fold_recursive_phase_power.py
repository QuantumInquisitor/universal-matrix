"""Measure recursive modal phase and signed connector power flow without changing the model."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import Q0
    from .report_fold_recursive_drive_load_replay import REPRESENTATIVE, capture_full_tree
    from .report_fold_recursive_impedance import module_matrices
    from .report_fold_scale_extension import connector
except ImportError:
    from report_fold_dynamics import Q0
    from report_fold_recursive_drive_load_replay import REPRESENTATIVE, capture_full_tree
    from report_fold_recursive_impedance import module_matrices
    from report_fold_scale_extension import connector


PHASE_AMPLITUDE_FLOOR = 1e-12
QUARTER_TURN_RAD = math.pi / 2


def base_modes():
    mass, stiffness, _ = module_matrices(1.0)
    values, vectors = np.linalg.eig(np.linalg.solve(mass, stiffness))
    if np.max(np.abs(np.imag(values))) > 1e-10 or np.max(np.abs(np.imag(vectors))) > 1e-10:
        raise ValueError("recursive modal phase requires real linearized modes")
    values, vectors = np.real(values), np.real(vectors)
    order = np.argsort(values)
    values, vectors = values[order], vectors[:, order]
    if np.min(values) <= 0:
        raise ValueError("recursive modal phase requires positive modal stiffness")
    for column in range(vectors.shape[1]):
        vectors[:, column] /= np.linalg.norm(vectors[:, column])
    return vectors


def phase_from_modal(displacement, rate, omega):
    displacement = float(displacement)
    rate = float(rate)
    omega = float(omega)
    if not math.isfinite(displacement) or not math.isfinite(rate) or not math.isfinite(omega):
        raise ValueError("modal phase inputs must be finite")
    if omega <= 0:
        raise ValueError("modal omega must be positive")
    quadrature = -rate / omega
    amplitude = math.hypot(displacement, quadrature)
    if amplitude <= PHASE_AMPLITUDE_FLOOR:
        return {
            "amplitude": amplitude,
            "phase_rad": None,
            "cos_projection": None,
            "sin_projection": None,
            "quarter_cycle_index": None,
        }
    phase = math.atan2(quadrature, displacement)
    wrapped = phase % (2 * math.pi)
    quarter = int(round(wrapped / QUARTER_TURN_RAD)) % 4
    return {
        "amplitude": amplitude,
        "phase_rad": phase,
        "cos_projection": displacement / amplitude,
        "sin_projection": quadrature / amplitude,
        "quarter_cycle_index": quarter,
    }


def wrap_phase(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("phase difference must be finite")
    return (value + math.pi) % (2 * math.pi) - math.pi


def modal_states(q, rates, scale, modes):
    q = np.asarray(q, dtype=float)
    rates = np.asarray(rates, dtype=float)
    mass, stiffness, _ = module_matrices(scale)
    rows = []
    for column in range(modes.shape[1]):
        mode = modes[:, column]
        modal_mass = float(mode @ mass @ mode)
        modal_stiffness = float(mode @ stiffness @ mode)
        omega = math.sqrt(modal_stiffness / modal_mass)
        displacement = float(mode @ (q - Q0))
        rate = float(mode @ rates)
        rows.append(
            {
                "mode": column,
                "omega_rad_per_s": omega,
                "modal_displacement": displacement,
                "modal_rate": rate,
                **phase_from_modal(displacement, rate, omega),
            }
        )
    return rows


def phase_lag(child, parent):
    if child["phase_rad"] is None or parent["phase_rad"] is None:
        return None
    return wrap_phase(child["phase_rad"] - parent["phase_rad"])


def correlation(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def edge_trace(full, child_level, modes):
    rep = REPRESENTATIVE[child_level]
    parent_scale = rep["parent_scale"]
    child_scale = parent_scale / 2
    rows = []

    for sample in full["trace"]:
        parent_q = sample["q"][rep["parent"]]
        parent_v = sample["rates"][rep["parent"]]
        child_q = sample["q"][rep["child"]]
        child_v = sample["rates"][rep["child"]]
        potential, parent_force, child_force = connector(
            parent_q,
            child_q,
            parent_scale,
            child_scale,
        )
        parent_power = float(np.asarray(parent_force) @ np.asarray(parent_v))
        child_power = float(np.asarray(child_force) @ np.asarray(child_v))
        storage_rate = -(parent_power + child_power)

        parent_modes = modal_states(parent_q, parent_v, parent_scale, modes)
        child_modes = modal_states(child_q, child_v, child_scale, modes)
        mode_rows = []
        for parent_mode, child_mode in zip(parent_modes, child_modes, strict=True):
            lag = phase_lag(child_mode, parent_mode)
            mode_rows.append(
                {
                    "mode": parent_mode["mode"],
                    "parent": parent_mode,
                    "child": child_mode,
                    "child_minus_parent_phase_lag_rad": lag,
                    "sin_phase_lag": None if lag is None else math.sin(lag),
                    "cos_phase_lag": None if lag is None else math.cos(lag),
                }
            )

        rows.append(
            {
                "time_s": sample["time_s"],
                "connector_potential_j": float(potential),
                "parent_power_w": parent_power,
                "child_power_w": child_power,
                "mechanical_energy_current_to_child_w": child_power,
                "connector_storage_rate_w": storage_rate,
                "modes": mode_rows,
            }
        )

    summaries = {}
    for mode_index in range(modes.shape[1]):
        defined = [
            row
            for row in rows
            if row["modes"][mode_index]["child_minus_parent_phase_lag_rad"] is not None
        ]
        sin_lag = [row["modes"][mode_index]["sin_phase_lag"] for row in defined]
        cos_lag = [row["modes"][mode_index]["cos_phase_lag"] for row in defined]
        child_power = [row["child_power_w"] for row in defined]
        storage_rate = [row["connector_storage_rate_w"] for row in defined]
        maximum = max(defined, key=lambda row: abs(row["child_power_w"])) if defined else None
        summaries[str(mode_index)] = {
            "defined_sample_count": len(defined),
            "sin_phase_lag_vs_child_power_correlation": correlation(sin_lag, child_power),
            "cos_phase_lag_vs_child_power_correlation": correlation(cos_lag, child_power),
            "sin_phase_lag_vs_storage_rate_correlation": correlation(sin_lag, storage_rate),
            "phase_lag_at_max_abs_child_power_rad": (
                None
                if maximum is None
                else maximum["modes"][mode_index]["child_minus_parent_phase_lag_rad"]
            ),
            "time_at_max_abs_child_power_s": None if maximum is None else maximum["time_s"],
            "max_abs_child_power_w": (
                0.0 if maximum is None else abs(maximum["child_power_w"])
            ),
        }

    return {
        "parent_node": rep["parent"],
        "child_node": rep["child"],
        "parent_scale": parent_scale,
        "child_scale": child_scale,
        "rows": rows,
        "mode_phase_power_summary": summaries,
    }


def report():
    full = capture_full_tree()
    modes = base_modes()
    edges = {str(level): edge_trace(full, level, modes) for level in (1, 2, 3)}

    return {
        "schema": 1,
        "scope": (
            "state-space modal phase, quarter-cycle projection and signed mechanical "
            "connector power flow in the existing passive recursive depth-three model"
        ),
        "phase_definition": {
            "modal_x": "v^T(q-Q0)",
            "modal_y": "-v^T(qdot)/omega",
            "complex_state": "z=x+i*y",
            "phase": "atan2(y,x)",
            "quarter_cycle_indices": {
                "0": "0 degrees / cosine +1",
                "1": "90 degrees / sine +1",
                "2": "180 degrees / cosine -1",
                "3": "270 degrees / sine -1",
            },
        },
        "phase_amplitude_floor": PHASE_AMPLITUDE_FLOOR,
        "edges": edges,
        "full_tree_energy": {
            "max_node_residual_j": full["max_node_residual_j"],
            "max_edge_residual_j": full["max_edge_residual_j"],
            "max_group_residual_j": full["max_group_residual_j"],
        },
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_phase_power.py",
                "report_fold_recursive_drive_load_replay.py",
                "report_fold_recursive_impedance.py",
                "report_fold_scale_extension.py",
                "report_fold_recursive_spatial_connector.py",
            )
        },
        "phase_is_state_space_diagnostic": True,
        "mechanical_energy_current_is_signed_power": True,
        "electrical_current_modeled": False,
        "charged_particles_modeled": False,
        "plasma_modeled": False,
        "electromagnetic_fields_modeled": False,
        "connector_coefficients_changed": False,
        "material_scaling_law_changed": False,
        "new_recursive_coupling_introduced": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
