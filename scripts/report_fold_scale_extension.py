"""Independent audit of the fold material laws below the declared 0.25 scale floor."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_constitutive import constitutive
    from .report_fold_dynamics import DAMPING, Q0, vector
    from .report_fold_kinematics import inventory, kinematics, scalar
    from .report_fold_mapped import PORT_STIFFNESS, port
except ImportError:
    from report_fold_constitutive import constitutive
    from report_fold_dynamics import DAMPING, Q0, vector
    from report_fold_kinematics import inventory, kinematics, scalar
    from report_fold_mapped import PORT_STIFFNESS, port


AUDIT_MIN_SCALE = 0.125


def audit_scale(value):
    """Experimental scale validator; does not replace the repository-wide guard."""
    value = scalar(value, "audit length scale")
    if not AUDIT_MIN_SCALE <= value <= 1:
        raise ValueError("audit length scale outside [0.125,1]")
    return value


def material_response(q, scale):
    scale = audit_scale(scale)
    return constitutive(
        q,
        length_m=0.1 * scale,
        thickness_m=1e-4 * scale,
        bridge_ea_n=0.1 * scale**2,
    )


def mechanical(q, velocity, scale):
    """Reconstruct inertia and constitutive energy without calling scale_value()."""
    scale = audit_scale(scale)
    masses = {name: mass * scale**3 for name, _, mass in inventory()}
    state = kinematics(q, length_m=0.1 * scale, masses=masses)
    velocity = vector(velocity, 2, "velocity")
    hvv = np.einsum("nxab,a,b->nx", state["hessian"], velocity, velocity)
    bias = np.einsum("n,nxa,nx->a", state["mass"], state["jacobian"], hvv)
    response = material_response(q, scale)
    energy = float(
        velocity @ state["mass_matrix"] @ velocity / 2 + response["total_energy_j"]
    )
    return state, bias, energy, np.asarray(response["gradient"])


def rhs(y, scale):
    scale = audit_scale(scale)
    y = vector(y, 5, "extended-scale material state")
    state, bias, _, gradient = mechanical(y[:2], y[2:4], scale)
    resistance = scale**4 * DAMPING @ y[2:4]
    acceleration = np.linalg.solve(
        state["mass_matrix"], -gradient - resistance - bias
    )
    return np.r_[y[2:4], acceleration, y[2:4] @ resistance]


def connector(qa, qb, size_a, size_b, weight=1.0):
    """Mapped connector formula evaluated with audit-scoped endpoint sizes."""
    size_a, size_b = audit_scale(size_a), audit_scale(size_b)
    weight = scalar(weight, "edge weight")
    if not 0 < weight <= 10:
        raise ValueError("edge weight outside (0,10]")
    pa, ja = port(qa, 0.1 * size_a)
    pb, jb = port(qb, 0.1 * size_b)
    delta = pa - pb
    force = weight * max(size_a, size_b) * PORT_STIFFNESS @ delta
    return float(delta @ force / 2), -ja.T @ force, jb.T @ force


def simulate(scale, *, reference_duration=0.2, refinement=1):
    """Compare corresponding trajectories with time proportional to scale."""
    scale = audit_scale(scale)
    reference_duration = scalar(reference_duration, "reference duration")
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    if not 0 < reference_duration <= 0.2:
        raise ValueError("reference duration outside (0,0.2]")

    reference_dt = 0.002 / refinement
    steps = round(reference_duration / reference_dt)
    if not np.isclose(steps * reference_dt, reference_duration, rtol=0, atol=1e-14):
        raise ValueError("reference duration must contain complete steps")
    dt = scale * reference_dt
    y = np.r_[Q0 + (0.02, -0.03), np.array((0.01, 0.02)) / scale, 0.0]
    initial = y.copy()
    _, _, e0, _ = mechanical(y[:2], y[2:4], scale)
    trace = []

    for step in range(steps + 1):
        derivative = rhs(y, scale)
        _, _, energy, _ = mechanical(y[:2], y[2:4], scale)
        trace.append(
            {
                "time_s": step * dt,
                "reference_time_s": step * reference_dt,
                "q": y[:2].tolist(),
                "rates": y[2:4].tolist(),
                "mechanical_j": energy,
                "loss_j": float(y[4]),
                "residual_j": float(energy - e0 + y[4]),
            }
        )
        if step == steps:
            break
        a = derivative
        b = rhs(y + dt * a / 2, scale)
        c = rhs(y + dt * b / 2, scale)
        d = rhs(y + dt * c, scale)
        y += dt * (a + 2 * b + 2 * c + d) / 6

    return {
        "scale": scale,
        "dt_s": dt,
        "reference_duration_s": reference_duration,
        "duration_s": reference_duration * scale,
        "initial_state": initial.tolist(),
        "final_state": y.tolist(),
        "max_balance_residual_j": max(abs(row["residual_j"]) for row in trace),
        "trace": trace,
    }


def comparison(run, reference):
    if reference["scale"] != 1:
        raise ValueError("reference run must use unit scale")
    if [row["reference_time_s"] for row in run["trace"]] != [
        row["reference_time_s"] for row in reference["trace"]
    ]:
        raise ValueError("matching reference-time grids required")
    scale = run["scale"]
    q = np.asarray([row["q"] for row in run["trace"]])
    q0 = np.asarray([row["q"] for row in reference["trace"]])
    rates = np.asarray([row["rates"] for row in run["trace"]])
    rates0 = np.asarray([row["rates"] for row in reference["trace"]])
    energy = np.asarray([row["mechanical_j"] for row in run["trace"]])
    energy0 = np.asarray([row["mechanical_j"] for row in reference["trace"]])
    loss = np.asarray([row["loss_j"] for row in run["trace"]])
    loss0 = np.asarray([row["loss_j"] for row in reference["trace"]])
    return {
        "coordinate_max_difference": float(np.max(abs(q - q0))),
        "rescaled_rate_max_difference": float(np.max(abs(scale * rates - rates0))),
        "rescaled_energy_max_difference_j": float(
            np.max(abs(energy / scale**3 - energy0))
        ),
        "rescaled_loss_max_difference_j": float(
            np.max(abs(loss / scale**3 - loss0))
        ),
    }


def static_checks(scale):
    scale = audit_scale(scale)
    q = Q0 + (0.03, -0.04)
    v = np.array((0.11, -0.12))
    base, bias0, _, gradient0 = mechanical(q, v, 1)
    state, bias, _, gradient = mechanical(q, v, scale)
    point_velocity = state["jacobian"] @ v
    cartesian = float(
        sum(
            mass * np.dot(velocity, velocity)
            for mass, velocity in zip(state["mass"], point_velocity, strict=True)
        )
        / 2
    )
    generalized = float(v @ state["mass_matrix"] @ v / 2)
    response = material_response(q, scale)
    base_response = material_response(q, 1)
    return {
        "scale": scale,
        "minimum_mass_kg": float(np.min(state["mass"])),
        "length_m": 0.1 * scale,
        "thickness_m": 1e-4 * scale,
        "bridge_ea_n": 0.1 * scale**2,
        "position_scaling_error_m": float(
            np.max(abs(state["position"] - scale * base["position"]))
        ),
        "mass_matrix_scaling_error": float(
            np.max(abs(state["mass_matrix"] - scale**5 * base["mass_matrix"]))
        ),
        "bias_scaling_error": float(np.max(abs(bias - scale**5 * bias0))),
        "material_energy_scaling_error_j": abs(
            response["total_energy_j"] - scale**3 * base_response["total_energy_j"]
        ),
        "material_gradient_scaling_error": np.max(
            abs(np.asarray(response["gradient"]) - scale**3 * gradient0)
        ).item(),
        "cartesian_generalized_kinetic_error_j": abs(cartesian - generalized),
    }


def connector_checks():
    qa = Q0 + (0.02, -0.03)
    qb = Q0 + (-0.01, 0.04)
    direction_a = np.array((0.3, -0.2))
    direction_b = np.array((-0.1, 0.4))
    cases = {}
    for name, sizes in (
        ("quarter_to_eighth", (0.25, 0.125)),
        ("eighth_pair", (0.125, 0.125)),
    ):
        energy, force_a, force_b = connector(qa, qb, *sizes)
        eps = 1e-6
        slope = (
            connector(qa + eps * direction_a, qb + eps * direction_b, *sizes)[0]
            - connector(qa - eps * direction_a, qb - eps * direction_b, *sizes)[0]
        ) / (2 * eps)
        cases[name] = {
            "sizes": sizes,
            "energy_j": energy,
            "force_power_gradient_error": abs(
                slope + force_a @ direction_a + force_b @ direction_b
            ),
        }

    base = connector(qa, qb, 1, 1)[0]
    eighth = connector(qa, qb, 0.125, 0.125)[0]
    return {
        "cases": cases,
        "uniform_eighth_energy_scaling_error_j": abs(
            eighth - 0.125**3 * base
        ),
    }


def report():
    reference = simulate(1)
    quarter = simulate(0.25)
    eighth = simulate(0.125)
    eighth_fine = simulate(0.125, refinement=2)
    static = {str(scale): static_checks(scale) for scale in (1, 0.25, 0.125)}
    return {
        "schema": 1,
        "scope": (
            "independent numerical audit at scale 0.125 below the repository-wide "
            "0.25 guard; existing production validators remain unchanged"
        ),
        "declared_repository_scale_floor": 0.25,
        "audit_scale_floor": AUDIT_MIN_SCALE,
        "static": static,
        "trajectories": {
            "reference": {k: v for k, v in reference.items() if k != "trace"},
            "quarter": {k: v for k, v in quarter.items() if k != "trace"},
            "eighth": {k: v for k, v in eighth.items() if k != "trace"},
            "eighth_fine": {k: v for k, v in eighth_fine.items() if k != "trace"},
        },
        "similarity": {
            "quarter": comparison(quarter, reference),
            "eighth": comparison(eighth, reference),
        },
        "eighth_refinement_max_state_difference": float(
            np.max(abs(np.asarray(eighth["final_state"]) - np.asarray(eighth_fine["final_state"])))
        ),
        "connector": connector_checks(),
        "sources": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "report_fold_scale_extension.py",
                "report_fold_kinematics.py",
                "report_fold_constitutive.py",
                "report_fold_mapped.py",
            )
        },
        "global_scale_guard_changed": False,
        "depth_three_recursive_tree_executed": False,
        "physical_scale_extension_validated": False,
        "numerical_scale_extension_audited": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
