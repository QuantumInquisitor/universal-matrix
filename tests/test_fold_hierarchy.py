"""Independent hierarchy ownership, boundary-work and regrouping checks."""

import numpy as np
import pytest

from scripts.report_fold_hierarchy import accounts, compile_hierarchy, integrate, rhs
from scripts.report_fold_network import initial_state, measure
from scripts.report_fold_network import rhs as flat_rhs

EDGES = [(0, 1, 1.0), (1, 2, 0.7), (2, 3, 1.2), (3, 0, 0.5)]


def test_lca_ownership_exactly_once():
    layout = compile_hierarchy(4, EDGES, [[0, 1], [2, 3]])
    assert layout["owners"] == {"root/0": [0], "root/1": [2], "root": [1, 3]}
    assert sorted(e for owned in layout["owners"].values() for e in owned) == [0, 1, 2, 3]


@pytest.mark.parametrize(
    "tree", [[0, 1, 2, 3], [[0, 1], [2, 3]], [0, [1, [2, 3]]], [[3, 1], [2, 0]]]
)
def test_recursive_forces_match_flat_and_trajectory(tree):
    layout = compile_hierarchy(4, EDGES, tree)
    y = initial_state(4, EDGES)
    y[11:13] = (0.03, -0.02)
    np.testing.assert_allclose(rhs(y, layout), flat_rhs(y, 4, EDGES), atol=1e-16, rtol=1e-14)
    flat = integrate(layout, hierarchical=False, steps=5)
    nested = integrate(layout, steps=5)
    np.testing.assert_allclose(flat["states"], nested["states"], atol=1e-15, rtol=0)


def test_independent_subgroup_energy_rate_equals_boundary_power():
    layout = compile_hierarchy(4, EDGES, [[0, 1], [2, 3]])
    y = initial_state(4, EDGES)
    y[11:13] = (0.04, -0.03)
    y[20:22] = (-0.03, 0.02)
    y[29:31] = (0.01, 0.05)
    derivative = rhs(y, layout)
    eps = 1e-6
    plus, minus = accounts(y + eps * derivative, layout), accounts(y - eps * derivative, layout)
    for path in layout["groups"]:
        measured = (plus[path]["accounted_energy_j"] - minus[path]["accounted_energy_j"]) / 2 / eps
        crossing = (plus[path]["boundary_work_j"] - minus[path]["boundary_work_j"]) / 2 / eps
        assert abs(measured - crossing) < 1e-12
    assert accounts(y, layout)["root"]["accounted_energy_j"] == pytest.approx(
        measure(y, 4, EDGES)[3], abs=1e-20
    )


def test_group_residuals_and_nonzero_boundary_work():
    layout = compile_hierarchy(4, EDGES, [[0, 1], [2, 3]])
    result = integrate(layout, steps=20)
    assert max(result["group_max_residual_j"].values()) < 1e-12
    assert abs(result["final_accounts"]["root/0"]["boundary_work_j"]) > 1e-9
    assert result["final_accounts"]["root"]["boundary_work_j"] == 0


@pytest.mark.parametrize(
    "tree",
    [[0, 1, 2], [0, 1, 2, 2], [0, 1, 2, 4], [0, 1, 2, True], [0, 1, 2, []], [], 0, [0, 1, 2, 3.0]],
)
def test_invalid_hierarchies(tree):
    with pytest.raises(ValueError):
        compile_hierarchy(4, EDGES, tree)


def test_depth_limit():
    tree = 0
    for _ in range(10):
        tree = [tree]
    with pytest.raises(ValueError, match="depth"):
        compile_hierarchy(1, [], tree)


def test_single_node_disconnected_hierarchy():
    layout = compile_hierarchy(1, [], [[0]])
    y = initial_state(1, [])
    np.testing.assert_allclose(rhs(y, layout), flat_rhs(y, 1, []), atol=0, rtol=0)
    assert layout["owners"] == {"root/0": [], "root": []}


@pytest.mark.parametrize("dt", [True, 10**400, float("nan"), 0, "0.01"])
def test_invalid_timestep(dt):
    layout = compile_hierarchy(1, [], [0])
    with pytest.raises(ValueError):
        integrate(layout, dt=dt)
