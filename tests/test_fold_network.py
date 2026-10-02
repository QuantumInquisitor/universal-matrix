"""Graph topology, accounting and independent pair reduction controls."""

import numpy as np
import pytest

from scripts.report_fold_coupling import rhs as pair_rhs
from scripts.report_fold_network import initial_state, measure, rhs, simulate, topology

CHAIN = [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0)]


def test_two_node_reduces_to_verified_pair():
    edges = [(0, 1, 1.0)]
    y = initial_state(2, edges)
    np.testing.assert_allclose(rhs(y, 2, edges), pair_rhs(y), rtol=0, atol=0)


def test_independent_global_energy_derivative_and_broken_edge():
    y = initial_state(4, CHAIN)
    y[9:13] += (0.01, -0.02, 0.03, -0.04)
    y[18:22] += (-0.01, 0.015, -0.02, 0.03)
    eps = 1e-6
    d = rhs(y, 4, CHAIN)
    slope = (measure(y + eps * d, 4, CHAIN)[3] - measure(y - eps * d, 4, CHAIN)[3]) / 2 / eps
    assert abs(slope) < 1e-12
    bad = rhs(y, 4, CHAIN, broken_edge=1)
    error = (measure(y + eps * bad, 4, CHAIN)[3] - measure(y - eps * bad, 4, CHAIN)[3]) / 2 / eps
    assert abs(error) > 1e-7


def test_edge_orientation_changes_only_endpoint_ledger_order():
    y = initial_state(4, CHAIN)
    y[11:13] = (0.03, -0.02)
    normal = rhs(y, 4, CHAIN)
    reversed_edges = [(b, a, w) for a, b, w in CHAIN]
    reverse = rhs(y, 4, reversed_edges)
    np.testing.assert_allclose(normal[:36], reverse[:36], atol=0, rtol=0)
    np.testing.assert_allclose(
        normal[36:].reshape(-1, 2), reverse[36:].reshape(-1, 2)[:, ::-1], atol=0, rtol=0
    )


def test_node_relabeling_preserves_derivatives():
    y = initial_state(4, CHAIN)
    order = [2, 0, 3, 1]
    inverse = np.argsort(order)
    relabeled = [(int(inverse[a]), int(inverse[b]), w) for a, b, w in CHAIN]
    moved = np.r_[y[:36].reshape(4, 9)[order].ravel(), y[36:]]
    expected = rhs(y, 4, CHAIN)
    actual = rhs(moved, 4, relabeled)
    np.testing.assert_allclose(
        actual[:36].reshape(4, 9), expected[:36].reshape(4, 9)[order], atol=1e-16, rtol=0
    )
    np.testing.assert_allclose(actual[36:], expected[36:], atol=0, rtol=0)


def test_disconnected_nodes_remain_still():
    run = simulate(4, [], duration=0.2)
    assert run["trace"][-1]["mechanical_j"][1:] == [0.0, 0.0, 0.0]
    assert run["max_edge_residuals_j"] == []


def test_graph_conservation_and_error_localization():
    good = simulate(4, CHAIN, duration=0.6, gain=0, damping=0, leakage=0, fueled=False)
    bad = simulate(
        4, CHAIN, duration=0.6, gain=0, damping=0, leakage=0, fueled=False, broken_edge=0
    )
    assert good["max_total_residual_j"] < 1e-12
    assert good["max_node_residual_j"] < 1e-12
    assert max(good["max_edge_residuals_j"]) < 1e-12
    assert good["trace"][-1]["mechanical_j"][2] > 0
    assert bad["max_node_residual_j"] < 1e-12
    assert bad["max_edge_residuals_j"][0] > 1e-8
    assert max(bad["max_edge_residuals_j"][1:]) < 1e-12


@pytest.mark.parametrize(
    "nodes,edges",
    [
        (0, []),
        (9, []),
        (True, []),
        (2, [(0, 0, 1)]),
        (2, [(0, 2, 1)]),
        (2, [(False, 1, 1)]),
        (2, [(0, 1, 1), (1, 0, 2)]),
        (2, [(0, 1, 0)]),
        (2, [(0, 1, -1)]),
        (2, [(0, 1, True)]),
        (2, [(0, 1, float("nan"))]),
        (2, [(0, 1)]),
        (2, None),
    ],
)
def test_invalid_topology(nodes, edges):
    with pytest.raises(ValueError):
        topology(nodes, edges)


def test_invalid_broken_edge_and_initial_ledger():
    y = initial_state(4, CHAIN)
    with pytest.raises(ValueError):
        rhs(y, 4, CHAIN, broken_edge=True)
    y[-1] = 1
    with pytest.raises(ValueError, match="ledgers"):
        simulate(4, CHAIN, initial=y)
