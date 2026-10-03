"""Instantaneous independent controls; no trajectory integration."""

import numpy as np
import pytest

from scripts.fold_distributed_graph import body_rhs, measure, mechanical, rhs
from scripts.fold_material_multiscale import scaled_material
from scripts.report_fold_distributed_inertia import distributed_kinematics, inertial_bias
from scripts.report_fold_dynamics import DAMPING
from scripts.report_fold_hierarchy import compile_hierarchy
from scripts.report_fold_kinematics import inventory
from scripts.report_fold_multiscale import connector
from scripts.report_fold_scaling import scaled_mechanical


def fixture_state():
    sizes = (1.0, 0.5, 0.5)
    edges = ((0, 1, 1.0), (0, 2, 1.0))
    blocks = np.array(
        [[1.02, 0.2, 0.3, -0.4, 0], [0.98, 0.27, -0.2, 0.25, 0], [1.01, 0.15, 0.1, 0.2, 0]]
    )
    return np.r_[blocks.ravel(), np.zeros(4)], sizes, edges


def independent_energy(y, sizes, edges):
    blocks = y[: 5 * len(sizes)].reshape(-1, 5)
    energy = 0.0
    for b, scale in zip(blocks, sizes, strict=True):
        masses = {name: mass * scale**3 for name, _, mass in inventory()}
        state = distributed_kinematics(b[:2], length_m=0.1 * scale, masses=masses)
        energy += np.sum(state["mass"][:, None] * (state["jacobian"] @ b[2:4]) ** 2) / 2
        energy += scaled_material(b[:2], scale)["total_energy_j"]
    energy += sum(
        connector(blocks[a, :2], blocks[b, :2], sizes[a], sizes[b], w)[0] for a, b, w in edges
    )
    return energy


def energy_rate(y, derivative, sizes, edges, eps):
    return (
        independent_energy(y + eps * derivative, sizes, edges)
        - independent_energy(y - eps * derivative, sizes, edges)
    ) / (2 * eps)


def test_one_node_matches_single_specimen_equations_and_cartesian_energy():
    y = np.array([1.02, 0.2, 0.3, -0.4, 0.0])
    state = distributed_kinematics(y[:2])
    expected = np.linalg.solve(
        state["mass_matrix"],
        -np.asarray(scaled_material(y[:2])["gradient"])
        - DAMPING @ y[2:4]
        - inertial_bias(state, y[2:4]),
    )
    np.testing.assert_allclose(body_rhs(y)[2:4], expected, rtol=1e-14)
    np.testing.assert_allclose(rhs(y, (1,), ()), body_rhs(y), rtol=0, atol=0)
    assert mechanical(y[:2], y[2:4])[2] == pytest.approx(independent_energy(y, (1,), ()))


@pytest.mark.parametrize("scale", [0.25, 0.5, 1.0])
def test_homothetic_contract(scale):
    q, v = (1.02, 0.2), np.array([0.3, -0.4])
    base, bias, energy = mechanical(q, v)
    state, fixed_bias, _ = mechanical(q, v, scale)
    assert set(state["owners"]) == {name for name, _, _ in inventory()}
    assert len(state["mass"]) == 82
    for name, _, mass in inventory():
        assert state["mass"][np.array(state["owners"]) == name].sum() == pytest.approx(
            mass * scale**3
        )
    np.testing.assert_allclose(state["mass_matrix"], scale**5 * base["mass_matrix"], rtol=1e-13)
    np.testing.assert_allclose(fixed_bias, scale**5 * bias, rtol=1e-13)
    assert np.linalg.eigvalsh(state["mass_matrix"])[0] > 0
    _, dynamic_bias, dynamic_energy = mechanical(q, v / scale, scale)
    np.testing.assert_allclose(dynamic_bias, scale**3 * bias, rtol=1e-13)
    assert dynamic_energy == pytest.approx(scale**3 * energy, rel=1e-13)
    derivative = body_rhs(np.r_[q, v / scale, 0], scale)
    np.testing.assert_allclose(
        derivative[2:4], body_rhs(np.r_[q, v, 0])[2:4] / scale**2, rtol=1e-12
    )


def test_disconnected_nodes_and_zero_edge_accounts():
    y, sizes, _ = fixture_state()
    y = y[:15]
    actual = rhs(y, sizes, ())
    for i, scale in enumerate(sizes):
        np.testing.assert_array_equal(
            actual[5 * i : 5 * i + 5], body_rhs(y[5 * i : 5 * i + 5], scale)
        )
    changed = y.copy()
    changed[5] += 0.01
    np.testing.assert_array_equal(rhs(changed, sizes, ())[:5], actual[:5])
    layout = compile_hierarchy(3, (), [0, 1, 2])
    energies, potentials, incident, groups = measure(y, sizes, (), layout)
    assert potentials.shape == (0,)
    np.testing.assert_array_equal(incident, np.zeros(3))
    assert all(g["internal_edges"] == [] and g["boundary_work_j"] == 0 for g in groups.values())
    assert np.all(np.isfinite(energies))


def test_independent_energy_rate_and_negative_controls():
    y, sizes, edges = fixture_state()
    derivative = rhs(y, sizes, edges)
    loss_rate = derivative[:15].reshape(3, 5)[:, 4].sum()
    residuals = [
        abs(energy_rate(y, derivative, sizes, edges, eps) + loss_rate) for eps in (2e-6, 1e-6)
    ]
    assert max(residuals) < 1e-10
    faults = {}
    missing_bias = derivative.copy()
    for i, scale in enumerate(sizes):
        b = y[5 * i : 5 * i + 5]
        state, bias, _ = mechanical(b[:2], b[2:4], scale)
        missing_bias[5 * i + 2 : 5 * i + 4] += np.linalg.solve(state["mass_matrix"], bias)
    faults["missing_bias"] = missing_bias
    wrong_reaction = derivative.copy()
    _, fa, fb = connector(y[:2], y[5:7], sizes[0], sizes[1])
    child_matrix = mechanical(y[5:7], y[7:9], sizes[1])[0]["mass_matrix"]
    wrong_reaction[7:9] -= 2 * np.linalg.solve(child_matrix, fb)
    faults["wrong_reaction"] = wrong_reaction
    wrong_matrix = derivative.copy()
    distributed = mechanical(y[:2], y[2:4])[0]["mass_matrix"]
    point = scaled_mechanical(y[:2], y[2:4])[0]["mass_matrix"]
    wrong_matrix[2:4] += np.linalg.solve(point, fa) - np.linalg.solve(distributed, fa)
    faults["point_connector_matrix"] = wrong_matrix
    for name, fault in faults.items():
        assert abs(energy_rate(y, fault, sizes, edges, 1e-6) + loss_rate) > 1e-8, name


def test_endpoint_power_and_group_ownership():
    y, sizes, edges = fixture_state()
    derivative = rhs(y, sizes, edges)
    for e, (a, b, w) in enumerate(edges):
        qa, qb = y[5 * a : 5 * a + 2], y[5 * b : 5 * b + 2]
        va, vb = y[5 * a + 2 : 5 * a + 4], y[5 * b + 2 : 5 * b + 4]
        eps = 1e-6
        slope = (
            connector(qa + eps * va, qb + eps * vb, sizes[a], sizes[b], w)[0]
            - connector(qa - eps * va, qb - eps * vb, sizes[a], sizes[b], w)[0]
        ) / (2 * eps)
        assert abs(slope + derivative[15 + 2 * e : 17 + 2 * e].sum()) < 1e-10
    y[4], y[9], y[14] = 0.1, 0.2, 0.3
    y[15:] = [0.01, -0.02, 0.03, -0.04]
    layout = compile_hierarchy(3, edges, [0, [1, 2]])
    energy, potential, incident, groups = measure(y, sizes, edges, layout)
    np.testing.assert_allclose(incident, [0.04, -0.02, -0.04])
    for path, members in layout["groups"].items():
        internal = [e for e, (a, b, _) in enumerate(edges) if a in members and b in members]
        expected = (
            energy[members].sum()
            + y[:15].reshape(3, 5)[members, 4].sum()
            + potential[internal].sum()
        )
        assert groups[path]["accounted_energy_j"] == pytest.approx(expected)
        boundary = sum(incident[members]) - sum(y[15 + 2 * e : 17 + 2 * e].sum() for e in internal)
        assert groups[path]["boundary_work_j"] == pytest.approx(boundary)


@pytest.mark.parametrize("scale", [0.249, 1.01, True, np.nan])
def test_invalid_scale(scale):
    with pytest.raises(ValueError):
        mechanical((1, 0.2), (0, 0), scale)


@pytest.mark.parametrize(
    "q,v",
    [
        ((0.8, 0.2), (0, 0)),
        ((1, -0.1), (0, 0)),
        ((True, 0.2), (0, 0)),
        ((1, 0.2), (np.inf, 0)),
        ((1, 0.2), (1e6 + 1, 0)),
        ((1, 0.2), (0,)),
    ],
)
def test_invalid_mechanics(q, v):
    with pytest.raises(ValueError):
        mechanical(q, v)


def test_invalid_graph_shape_and_topology():
    with pytest.raises(ValueError):
        rhs(np.zeros(4), (1,), ())
    with pytest.raises(ValueError):
        rhs(np.zeros(12), (1, 0.5), ((0, 2, 1),))
