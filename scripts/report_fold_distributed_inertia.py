"""Synthetic panel/bridge distributed inertia with fixed body mass ownership."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from scripts.report_fold_kinematics import PANELS, core_coefficients, inventory, kinematics, rays


def material_points():
    """Exact degree-two quadrature for uniform reference panels and bridge lines."""
    polygon = core_coefficients()
    triangles = [polygon[[0, k, k + 1]] for k in range(1, len(polygon) - 1)]
    areas = []
    for triangle in triangles:
        u, v = triangle[1] - triangle[0], triangle[2] - triangle[0]
        areas.append(abs(u[0] * v[1] - u[1] * v[0]) / 2)
    total = sum(areas)
    barycentric = np.array(((2 / 3, 1 / 6, 1 / 6), (1 / 6, 2 / 3, 1 / 6), (1 / 6, 1 / 6, 2 / 3)))
    mass_by_id = {name: mass for name, _, mass in inventory()}
    ids, coefficients, weights = [], [], []
    for index, pair in enumerate(PANELS):
        name = f"panel-{index}"
        for triangle, area in zip(triangles, areas, strict=True):
            for point in barycentric @ triangle:
                c = np.zeros(4)
                c[list(pair)] = point
                ids.append(name)
                coefficients.append(c)
                weights.append(mass_by_id[name] * area / total / 3)
    for hub in range(4):
        name = f"hub-{hub}"
        ids.append(name)
        coefficients.append(0.5 * np.eye(4)[hub])
        weights.append(mass_by_id[name])
    for index, pair in enumerate(PANELS):
        for hub, other in (pair, pair[::-1]):
            name = f"bridge-{index}-{hub}"
            for t in ((1 - 1 / np.sqrt(3)) / 2, (1 + 1 / np.sqrt(3)) / 2):
                ids.append(name)
                coefficients.append(0.5 * np.eye(4)[hub] + 0.17 * t * np.eye(4)[other])
                weights.append(mass_by_id[name] / 2)
    return ids, np.asarray(coefficients), np.asarray(weights)


def distributed_kinematics(q, length_m=0.1, masses=None):
    """Use old input guards/mass owners; replace each body's point distribution only."""
    old = kinematics(q, length_m, masses)
    owners, coefficients, weights = material_points()
    defaults = {name: mass for name, _, mass in inventory()}
    assigned = dict(zip(old["ids"], old["mass"], strict=True))
    mass = weights * np.array([assigned[name] / defaults[name] for name in owners])
    s, theta = map(float, q)
    r, dr, ddr = rays(theta)
    base, first, second = coefficients @ r, coefficients @ dr, coefficients @ ddr
    position = length_m * s * base
    jacobian = np.stack((length_m * base, length_m * s * first), axis=2)
    hessian = np.zeros((len(mass), 3, 2, 2))
    hessian[:, :, 0, 1] = hessian[:, :, 1, 0] = length_m * first
    hessian[:, :, 1, 1] = length_m * s * second
    matrix = np.einsum("n,nxa,nxb->ab", mass, jacobian, jacobian)
    return dict(
        owners=owners,
        mass=mass,
        position=position,
        jacobian=jacobian,
        hessian=hessian,
        mass_matrix=matrix,
    )


def inertial_bias(state, velocity):
    v = np.asarray(velocity, dtype=float)
    if v.shape != (2,) or not np.all(np.isfinite(v)):
        raise ValueError("velocity must have two finite entries")
    acceleration = np.einsum("nxab,a,b->nx", state["hessian"], v, v)
    return np.einsum("n,nxa,nx->a", state["mass"], state["jacobian"], acceleration)


def centroid_mass_matrix(state):
    """Mass-weighted body centroids, not the historical vertex-mean panel points."""
    matrix = np.zeros((2, 2))
    owners = np.asarray(state["owners"])
    for name in set(owners):
        mask = owners == name
        mass = state["mass"][mask]
        mean = np.einsum("n,nxa->xa", mass, state["jacobian"][mask]) / mass.sum()
        matrix += mass.sum() * mean.T @ mean
    return matrix


def report():
    rows = []
    for s in (0.9, 1.0, 1.1):
        for theta in np.linspace(0, np.pi / 6, 9):
            state = distributed_kinematics((s, theta))
            velocity = np.array((0.21, -0.37))
            cartesian = float(
                np.sum(state["mass"][:, None] * (state["jacobian"] @ velocity) ** 2) / 2
            )
            reduced = float(velocity @ state["mass_matrix"] @ velocity / 2)
            covariance = state["mass_matrix"] - centroid_mass_matrix(state)
            rows.append(
                dict(
                    q=[s, float(theta)],
                    minimum_eigenvalue=float(np.linalg.eigvalsh(state["mass_matrix"])[0]),
                    centroid_covariance_minimum_eigenvalue=float(np.linalg.eigvalsh(covariance)[0]),
                    kinetic_identity_error_j=abs(cartesian - reduced),
                    matrix=state["mass_matrix"].tolist(),
                    old_point_matrix=kinematics((s, theta))["mass_matrix"].tolist(),
                )
            )
    owners, _, mass = material_points()
    totals = {
        name: float(sum(w for owner, w in zip(owners, mass, strict=True) if owner == name))
        for name, _, _ in inventory()
    }
    root = Path(__file__).resolve().parents[1]
    paths = ("scripts/report_fold_distributed_inertia.py", "scripts/report_fold_kinematics.py")
    result = dict(
        schema=1,
        scope="Uniform reference panel surfaces and bridge centerlines; point hubs",
        body_mass_kg=totals,
        total_mass_kg=float(mass.sum()),
        quadrature_points=len(mass),
        samples=rows,
        production_dynamics_changed=False,
        physical_calibration=False,
        hub_rotational_inertia=False,
        solid_volume_partition=False,
        source_hash_encoding="UTF-8/LF",
        sources={
            p: hashlib.sha256((root / p).read_text(encoding="utf-8").encode()).hexdigest()
            for p in paths
        },
    )
    assert len(totals) == 22 and abs(result["total_mass_kg"] - 0.74) < 1e-14
    assert min(r["minimum_eigenvalue"] for r in rows) > 0
    assert min(r["centroid_covariance_minimum_eigenvalue"] for r in rows) > -1e-15
    assert max(r["kinetic_identity_error_j"] for r in rows) < 1e-15
    return result


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
                "mass_kg": result["total_mass_kg"],
                "points": result["quadrature_points"],
                "minimum_eigenvalue": min(r["minimum_eigenvalue"] for r in result["samples"]),
            }
        )
    )
