"""Optional instantaneous distributed-inertia graph contract; no time evolution."""

import numpy as np

from scripts.fold_material_multiscale import scaled_material
from scripts.report_fold_distributed_inertia import distributed_kinematics, inertial_bias
from scripts.report_fold_dynamics import DAMPING, vector
from scripts.report_fold_kinematics import inventory
from scripts.report_fold_multiscale import configuration, connector
from scripts.report_fold_scaling import scale_value


def mechanical(q, velocity, scale=1.0):
    """Return distributed state, bias and Cartesian-plus-constitutive energy."""
    scale = scale_value(scale)
    v = vector(velocity, 2, "velocity")
    if np.max(np.abs(v)) > 1e6:
        raise ValueError("velocity outside numerical scope")
    masses = {name: mass * scale**3 for name, _, mass in inventory()}
    state = distributed_kinematics(q, length_m=0.1 * scale, masses=masses)
    kinetic = float(np.sum(state["mass"][:, None] * (state["jacobian"] @ v) ** 2) / 2)
    energy = kinetic + scaled_material(q, scale)["total_energy_j"]
    return state, inertial_bias(state, v), float(energy)


def body_rhs(y, scale=1.0):
    """Five-state node: q(2), velocity(2), cumulative damping loss."""
    scale = scale_value(scale)
    y = vector(y, 5, "material body state")
    q, v = y[:2], y[2:4]
    state, bias, _ = mechanical(q, v, scale)
    gradient = np.asarray(scaled_material(q, scale)["gradient"])
    resistance = scale**4 * DAMPING @ v
    acceleration = np.linalg.solve(state["mass_matrix"], -gradient - resistance - bias)
    return np.r_[v, acceleration, v @ resistance]


def rhs(y, sizes, edges):
    """Preserve reciprocal mapped connectors and both signed endpoint works."""
    sizes, edges = configuration(sizes, edges)
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "mixed-size graph state")
    blocks = y[: 5 * n].reshape(n, 5)
    result = np.zeros_like(y)
    forces = np.zeros((n, 2))
    for i, block in enumerate(blocks):
        result[5 * i : 5 * i + 5] = body_rhs(block, sizes[i])
    for e, (a, b, w) in enumerate(edges):
        _, fa, fb = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)
        forces[a] += fa
        forces[b] += fb
        result[5 * n + 2 * e : 5 * n + 2 * e + 2] = [fa @ blocks[a, 2:4], fb @ blocks[b, 2:4]]
    for i, block in enumerate(blocks):
        state = mechanical(block[:2], block[2:4], sizes[i])[0]
        result[5 * i + 2 : 5 * i + 4] += np.linalg.solve(state["mass_matrix"], forces[i])
    return result


def measure(y, sizes, edges, layout):
    """Keep node, edge and group ownership separate; energy uses quadrature."""
    sizes, edges = configuration(sizes, edges)
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "mixed-size graph state")
    blocks = y[: 5 * n].reshape(n, 5)
    energies = np.array([mechanical(b[:2], b[2:4], sizes[i])[2] for i, b in enumerate(blocks)])
    potentials = np.array(
        [connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)[0] for a, b, w in edges]
    )
    works = y[5 * n :].reshape(len(edges), 2)
    incident = np.zeros(n)
    for e, (a, b, _) in enumerate(edges):
        incident[a] += works[e, 0]
        incident[b] += works[e, 1]
    groups = {}
    for path, members in layout["groups"].items():
        internal, boundary = [], 0.0
        for e, (a, b, _) in enumerate(edges):
            if a in members and b in members:
                internal.append(e)
            elif a in members:
                boundary += works[e, 0]
            elif b in members:
                boundary += works[e, 1]
        groups[path] = dict(
            accounted_energy_j=float(
                sum(energies[members]) + sum(blocks[members, 4]) + sum(potentials[internal])
            ),
            boundary_work_j=float(boundary),
            internal_edges=internal,
        )
    return energies, potentials, incident, groups
