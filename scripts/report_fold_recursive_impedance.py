"""Linearized scale-impedance audit for the existing recursive material laws."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from .report_fold_dynamics import DAMPING, Q0
    from .report_fold_scale_extension import connector, material_response, mechanical
except ImportError:
    from report_fold_dynamics import DAMPING, Q0
    from report_fold_scale_extension import connector, material_response, mechanical


EPS = 1e-6
MODULE_SCALES = (1.0, 0.5, 0.25, 0.125)
INTERFACE_PARENT_SCALES = (1.0, 0.5, 0.25)
REFERENCE_PERTURBATION = np.array((0.005, -0.008))


def material_stiffness(scale):
    """Centered-difference Hessian of the existing constitutive potential."""
    columns = []
    q0 = np.asarray(Q0, dtype=float)
    for axis in range(2):
        step = np.zeros(2)
        step[axis] = EPS
        plus = np.asarray(material_response(q0 + step, scale)["gradient"], dtype=float)
        minus = np.asarray(material_response(q0 - step, scale)["gradient"], dtype=float)
        columns.append((plus - minus) / (2 * EPS))
    matrix = np.column_stack(columns)
    return (matrix + matrix.T) / 2


def module_matrices(scale):
    state, _, _, _ = mechanical(Q0, np.zeros(2), scale)
    return (
        np.asarray(state["mass_matrix"], dtype=float),
        material_stiffness(scale),
        scale**4 * np.asarray(DAMPING, dtype=float),
    )


def _base_modes():
    mass, stiffness, _ = module_matrices(1.0)
    values, vectors = np.linalg.eig(np.linalg.solve(mass, stiffness))
    if np.max(np.abs(np.imag(values))) > 1e-10 or np.max(np.abs(np.imag(vectors))) > 1e-10:
        raise ValueError("linearized module modes must be real")
    values, vectors = np.real(values), np.real(vectors)
    order = np.argsort(values)
    values, vectors = values[order], vectors[:, order]
    if np.min(values) <= 0:
        raise ValueError("reference material tangent must have positive modal stiffness")
    for column in range(vectors.shape[1]):
        vectors[:, column] /= np.linalg.norm(vectors[:, column])
    return values, vectors


def module_linearization(scale, modes):
    mass, stiffness, damping = module_matrices(scale)
    rows = []
    for column in range(modes.shape[1]):
        mode = modes[:, column]
        modal_mass = float(mode @ mass @ mode)
        modal_stiffness = float(mode @ stiffness @ mode)
        modal_damping = float(mode @ damping @ mode)
        if modal_mass <= 0 or modal_stiffness <= 0:
            raise ValueError("modal mass and stiffness must be positive")
        omega = math.sqrt(modal_stiffness / modal_mass)
        impedance = math.sqrt(modal_mass * modal_stiffness)
        rows.append(
            {
                "modal_mass": modal_mass,
                "modal_stiffness": modal_stiffness,
                "modal_damping": modal_damping,
                "omega_rad_per_s": omega,
                "modal_impedance": impedance,
                "damping_ratio": modal_damping / (2 * impedance),
            }
        )
    return {
        "scale": scale,
        "mass_matrix": mass.tolist(),
        "material_stiffness": stiffness.tolist(),
        "damping_matrix": damping.tolist(),
        "modes": rows,
    }


def connector_stiffness(parent_scale):
    if parent_scale not in INTERFACE_PARENT_SCALES:
        raise ValueError("parent scale must be one of the tested recursive interfaces")
    child_scale = parent_scale / 2
    z0 = np.r_[Q0, Q0].astype(float)

    def force(z):
        _, parent_force, child_force = connector(
            z[:2], z[2:], parent_scale, child_scale
        )
        return np.r_[parent_force, child_force]

    columns = []
    for axis in range(4):
        step = np.zeros(4)
        step[axis] = EPS
        columns.append(-(force(z0 + step) - force(z0 - step)) / (2 * EPS))
    matrix = np.column_stack(columns)
    return (matrix + matrix.T) / 2


def interface_linearization(parent_scale):
    child_scale = parent_scale / 2
    connector_k = connector_stiffness(parent_scale)
    parent_k = material_stiffness(parent_scale)
    child_k = material_stiffness(child_scale)
    kpp = connector_k[:2, :2]
    kpc = connector_k[:2, 2:]
    kcp = connector_k[2:, :2]
    kcc = connector_k[2:, 2:]
    child_total = child_k + kcc
    transfer = -np.linalg.solve(child_total, kcp)
    child_delta = transfer @ REFERENCE_PERTURBATION
    combined_delta = np.r_[REFERENCE_PERTURBATION, child_delta]
    child_energy = float(child_delta @ child_k @ child_delta / 2)
    connector_energy = float(combined_delta @ connector_k @ combined_delta / 2)
    total_interface_energy = child_energy + connector_energy
    if total_interface_energy <= 0:
        raise ValueError("linearized interface energy must be positive")
    return {
        "parent_scale": parent_scale,
        "child_scale": child_scale,
        "connector_stiffness": connector_k.tolist(),
        "parent_material_stiffness": parent_k.tolist(),
        "child_material_stiffness": child_k.tolist(),
        "quasistatic_child_transfer_matrix": transfer.tolist(),
        "quasistatic_transfer_spectral_norm": float(np.linalg.svd(transfer)[1][0]),
        "reference_parent_perturbation": REFERENCE_PERTURBATION.tolist(),
        "relaxed_child_perturbation": child_delta.tolist(),
        "linearized_child_material_energy": child_energy,
        "linearized_connector_energy": connector_energy,
        "linearized_child_energy_fraction": child_energy / total_interface_energy,
        "connector_parent_block_to_parent_material_norm_ratio": float(
            np.linalg.norm(kpp, 2) / np.linalg.norm(parent_k, 2)
        ),
        "connector_child_block_to_child_material_norm_ratio": float(
            np.linalg.norm(kcc, 2) / np.linalg.norm(child_k, 2)
        ),
        "connector_cross_block_norm": float(np.linalg.norm(kpc, 2)),
    }


def report():
    _, modes = _base_modes()
    modules = {str(scale): module_linearization(scale, modes) for scale in MODULE_SCALES}
    interfaces = {
        str(scale): interface_linearization(scale) for scale in INTERFACE_PARENT_SCALES
    }

    base = modules["1.0"]
    base_mass = np.asarray(base["mass_matrix"])
    base_stiffness = np.asarray(base["material_stiffness"])
    base_damping = np.asarray(base["damping_matrix"])
    base_omega = np.asarray([row["omega_rad_per_s"] for row in base["modes"]])
    base_impedance = np.asarray([row["modal_impedance"] for row in base["modes"]])
    base_zeta = np.asarray([row["damping_ratio"] for row in base["modes"]])

    module_scaling = {}
    for scale in MODULE_SCALES:
        row = modules[str(scale)]
        mass = np.asarray(row["mass_matrix"])
        stiffness = np.asarray(row["material_stiffness"])
        damping = np.asarray(row["damping_matrix"])
        omega = np.asarray([mode["omega_rad_per_s"] for mode in row["modes"]])
        impedance = np.asarray([mode["modal_impedance"] for mode in row["modes"]])
        zeta = np.asarray([mode["damping_ratio"] for mode in row["modes"]])
        module_scaling[str(scale)] = {
            "mass_s5_max_error": float(np.max(np.abs(mass / scale**5 - base_mass))),
            "stiffness_s3_max_error": float(
                np.max(np.abs(stiffness / scale**3 - base_stiffness))
            ),
            "damping_s4_max_error": float(
                np.max(np.abs(damping / scale**4 - base_damping))
            ),
            "frequency_inverse_scale_max_error": float(
                np.max(np.abs(scale * omega - base_omega))
            ),
            "impedance_s4_max_error": float(
                np.max(np.abs(impedance / scale**4 - base_impedance))
            ),
            "damping_ratio_max_error": float(np.max(np.abs(zeta - base_zeta))),
        }

    base_connector = np.asarray(interfaces["1.0"]["connector_stiffness"])
    base_transfer = np.asarray(interfaces["1.0"]["quasistatic_child_transfer_matrix"])
    base_fraction = interfaces["1.0"]["linearized_child_energy_fraction"]
    interface_scaling = {}
    for parent_scale in INTERFACE_PARENT_SCALES:
        row = interfaces[str(parent_scale)]
        connector_k = np.asarray(row["connector_stiffness"])
        transfer = np.asarray(row["quasistatic_child_transfer_matrix"])
        interface_scaling[str(parent_scale)] = {
            "connector_parent_s3_max_error": float(
                np.max(np.abs(connector_k / parent_scale**3 - base_connector))
            ),
            "transfer_matrix_max_difference": float(
                np.max(np.abs(transfer - base_transfer))
            ),
            "child_energy_fraction_difference": abs(
                row["linearized_child_energy_fraction"] - base_fraction
            ),
        }

    return {
        "schema": 1,
        "scope": (
            "local linearized scale-impedance audit at the unloaded recursive reference; "
            "existing material, damping and mapped-connector laws only"
        ),
        "finite_difference_step": EPS,
        "module_scales": MODULE_SCALES,
        "interface_parent_scales": INTERFACE_PARENT_SCALES,
        "modules": modules,
        "interfaces": interfaces,
        "module_scaling": module_scaling,
        "interface_scaling": interface_scaling,
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_recursive_impedance.py",
                "report_fold_scale_extension.py",
                "report_fold_constitutive.py",
                "report_fold_kinematics.py",
                "report_fold_mapped.py",
                "report_fold_dynamics.py",
            )
        },
        "connector_coefficients_changed": False,
        "material_coefficients_changed": False,
        "damping_coefficients_changed": False,
        "dynamic_child_work_fraction_predicted": False,
        "spatial_recursive_embedding_validated": False,
        "arbitrary_depth_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
