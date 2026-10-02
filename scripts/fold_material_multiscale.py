"""Conditional homothetic material dynamics on a synthetic passive graph.

Reference thickness and bridge cross-section scale with length. These are explicit
model assumptions, not an experimentally calibrated material similarity law.
"""

import numpy as np

try:
    from .report_fold_constitutive import constitutive
    from .report_fold_dynamics import DAMPING, vector
    from .report_fold_hierarchy import compile_hierarchy
    from .report_fold_kinematics import scalar
    from .report_fold_multiscale import (
        BASE_SIZES,
        EDGES,
        TREE,
        configuration,
        connector,
        initial_state,
    )
    from .report_fold_scaling import scale_value, scaled_mechanical
except ImportError:
    from report_fold_constitutive import constitutive
    from report_fold_dynamics import DAMPING, vector
    from report_fold_hierarchy import compile_hierarchy
    from report_fold_kinematics import scalar
    from report_fold_multiscale import (
        BASE_SIZES,
        EDGES,
        TREE,
        configuration,
        connector,
        initial_state,
    )
    from report_fold_scaling import scale_value, scaled_mechanical


def scaled_material(q, scale=1.0):
    """Scale all lengths by a and bridge EA by a squared, retaining E and nu."""
    scale = scale_value(scale)
    return constitutive(
        q, length_m=0.1 * scale, thickness_m=1e-4 * scale, bridge_ea_n=0.1 * scale**2
    )


def mechanical(q, velocity, scale=1.0):
    """Retain point inertia and geometric bias; discard the old quadratic energy."""
    state, bias, _ = scaled_mechanical(q, velocity, scale)
    v = vector(velocity, 2, "velocity")
    energy = float(v @ state["mass_matrix"] @ v / 2 + scaled_material(q, scale)["total_energy_j"])
    return state, bias, energy


def body_rhs(y, scale=1.0):
    scale = scale_value(scale)
    y = vector(y, 5, "material body state")
    state, bias, _ = scaled_mechanical(y[:2], y[2:4], scale)
    gradient = np.array(scaled_material(y[:2], scale)["gradient"])
    v = y[2:4]
    resistance = scale**4 * DAMPING @ v
    acceleration = np.linalg.solve(state["mass_matrix"], -gradient - resistance - bias)
    return np.r_[v, acceleration, v @ resistance]


def rhs(y, sizes, edges, *, broken_edge=None):
    sizes, edges = configuration(sizes, edges)
    if broken_edge is not None and (
        type(broken_edge) is not int or not 0 <= broken_edge < len(edges)
    ):
        raise ValueError("broken edge must identify an existing edge")
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "mixed-size graph state")
    blocks = y[: 5 * n].reshape(n, 5)
    result = np.zeros_like(y)
    forces = np.zeros((n, 2))
    for i, block in enumerate(blocks):
        result[5 * i : 5 * i + 5] = body_rhs(block, sizes[i])
    for e, (a, b, w) in enumerate(edges):
        _, fa, fb = connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)
        if e == broken_edge:
            fb = -fb
        forces[a] += fa
        forces[b] += fb
        result[5 * n + 2 * e : 5 * n + 2 * e + 2] = [fa @ blocks[a, 2:4], fb @ blocks[b, 2:4]]
    for i, block in enumerate(blocks):
        mass = scaled_mechanical(block[:2], block[2:4], sizes[i])[0]["mass_matrix"]
        result[5 * i + 2 : 5 * i + 4] += np.linalg.solve(mass, forces[i])
    return result


def measure(y, sizes, edges, layout):
    sizes, edges = configuration(sizes, edges)
    n = len(sizes)
    y = vector(y, 5 * n + 2 * len(edges), "mixed-size graph state")
    blocks = y[: 5 * n].reshape(n, 5)
    energies = np.array([mechanical(b[:2], b[2:4], sizes[i])[2] for i, b in enumerate(blocks)])
    potentials = np.array(
        [connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)[0] for a, b, w in edges]
    )
    works = np.asarray(y[5 * n :]).reshape(len(edges), 2)
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
        accounted = float(
            sum(energies[members]) + sum(blocks[members, 4]) + sum(potentials[internal])
        )
        groups[path] = dict(
            accounted_energy_j=accounted, boundary_work_j=float(boundary), internal_edges=internal
        )
    return energies, potentials, incident, groups


def simulate(global_scale=1.0, *, refinement=1, broken_edge=None, duration_reference=0.2):
    global_scale = scale_value(global_scale)
    sizes, edges = configuration(tuple(global_scale * s for s in BASE_SIZES), EDGES)
    if type(refinement) is not int or refinement not in (1, 2):
        raise ValueError("refinement must be 1 or 2")
    layout = compile_hierarchy(len(sizes), edges, TREE)
    y = initial_state(sizes, edges, global_scale)
    initial = y.tolist()
    e0, u0, _, groups0 = measure(y, sizes, edges, layout)
    duration_reference = scalar(duration_reference, "reference duration")
    steps = round(duration_reference * 100 * refinement)
    if (
        not 0 < duration_reference <= 0.2
        or steps < 1
        or not np.isclose(steps / (100 * refinement), duration_reference, rtol=0, atol=1e-12)
    ):
        raise ValueError("reference duration must be complete .01/refinement steps in (0,.2]")
    dt = 0.01 * global_scale / refinement
    trace = []
    for step in range(steps + 1):
        derivative = rhs(y, sizes, edges, broken_edge=broken_edge)
        energy, potential, incident, groups = measure(y, sizes, edges, layout)
        for path, account in groups.items():
            account["residual_j"] = (
                account["accounted_energy_j"]
                - groups0[path]["accounted_energy_j"]
                - account["boundary_work_j"]
            )
        blocks = y[:20].reshape(4, 5)
        work = y[20:].reshape(4, 2)
        trace.append(
            dict(
                time_s=step * dt,
                reference_time_s=step * 0.01 / refinement,
                q=blocks[:, :2].tolist(),
                rates=blocks[:, 2:4].tolist(),
                mechanical_j=energy.tolist(),
                damping_loss_j=blocks[:, 4].tolist(),
                edge_potential_j=potential.tolist(),
                edge_work_j=work.tolist(),
                node_residual_j=(energy - e0 + blocks[:, 4] - incident).tolist(),
                edge_residual_j=(potential - u0 + work.sum(axis=1)).tolist(),
                groups=groups,
            )
        )
        if step == steps:
            break
        a = derivative
        b = rhs(y + dt * a / 2, sizes, edges, broken_edge=broken_edge)
        c = rhs(y + dt * b / 2, sizes, edges, broken_edge=broken_edge)
        d = rhs(y + dt * c, sizes, edges, broken_edge=broken_edge)
        y += dt * (a + 2 * b + 2 * c + d) / 6
    return dict(
        settings=dict(
            global_scale=global_scale,
            sizes=list(sizes),
            edges=edges,
            hierarchy=TREE,
            dt_s=dt,
            duration_s=duration_reference * global_scale,
            duration_reference_s=duration_reference,
            steps=steps,
            broken_edge=broken_edge,
        ),
        initial_state=initial,
        final_state=y.tolist(),
        initial_accounts=groups0,
        final_accounts=trace[-1]["groups"],
        owners=layout["owners"],
        max_node_residual_j=np.max(np.abs([r["node_residual_j"] for r in trace]), axis=0).tolist(),
        max_edge_residual_j=np.max(np.abs([r["edge_residual_j"] for r in trace]), axis=0).tolist(),
        max_group_residual_j={
            p: max(abs(r["groups"][p]["residual_j"]) for r in trace) for p in groups0
        },
        trace=trace,
    )


def comparison(run, reference):
    if [r["reference_time_s"] for r in run["trace"]] != [
        r["reference_time_s"] for r in reference["trace"]
    ]:
        raise ValueError("comparison requires matching reference-time grids")
    if reference["settings"]["global_scale"] != 1:
        raise ValueError("reference must have unit global scale")
    g = run["settings"]["global_scale"]

    def values(key, source):
        return np.array([r[key] for r in source["trace"]])

    return dict(
        coordinate_max_differences=np.max(
            abs(values("q", run) - values("q", reference)), axis=0
        ).tolist(),
        rescaled_rate_max_differences=np.max(
            abs(g * values("rates", run) - values("rates", reference)), axis=0
        ).tolist(),
        rescaled_node_energy_differences_j=np.max(
            abs(values("mechanical_j", run) / g**3 - values("mechanical_j", reference)), axis=0
        ).tolist(),
        rescaled_edge_energy_differences_j=np.max(
            abs(values("edge_potential_j", run) / g**3 - values("edge_potential_j", reference)),
            axis=0,
        ).tolist(),
    )
