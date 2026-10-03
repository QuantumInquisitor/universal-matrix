"""Bounded evolution and independent reference controls for the optional report."""

import numpy as np
import pytest

from scripts.fold_distributed_graph import rhs as established_rhs
from scripts.report_fold_distributed_graph_trajectories import rhs, simulate
from scripts.report_fold_distributed_trajectories import simulate as reference
from scripts.report_fold_multiscale import initial_state


@pytest.mark.parametrize("connected", [False, True])
def test_passive_stage_matches_established_graph_on_nonstationary_children(connected):
    sizes = (1.0, 0.5, 0.5)
    edges = ((0, 1, 1.0), (0, 2, 1.0)) if connected else ()
    y = initial_state(sizes, edges)
    y[5:9] = [1.02, 0.2, 0.3, -0.4]
    y[10:14] = [0.98, 0.27, -0.2, 0.25]
    np.testing.assert_allclose(
        rhs(y, sizes, edges), established_rhs(y, sizes, edges), rtol=1e-14, atol=1e-15
    )


def test_one_node_common_times_and_loss_index_match_independent_dop853():
    graph = simulate(0, refinement=2, duration=0.002)
    initial = np.asarray(graph["initial_state"])
    ref = reference(initial=np.r_[initial[:4], 0.0, initial[4]], duration=0.002, samples=5)
    rows = [r["q"] + r["rates"] + [r["loss_j"]] for r in ref["trace"]]
    np.testing.assert_allclose(graph["state_trace"], rows, rtol=0, atol=1e-10)
    assert graph["final_state"][4] > 0
    assert ref["final_state"][4] == 0  # work, not the graph loss


@pytest.mark.parametrize("damping", [0, 1])
def test_connected_energy_ownership(damping):
    case = simulate(1, duration=0.002, damping=damping)
    assert max(case["max_node_residual_j"]) < 1e-12
    assert max(case["max_edge_residual_j"]) < 1e-12
    assert max(case["max_group_residual_j"].values()) < 1e-12
    state = np.asarray(case["final_state"])
    losses = state[:15].reshape(3, 5)[:, 4]
    if damping:
        assert np.sum(losses) > 0
        assert case["total_energy_trace_j"][-1] < case["total_energy_trace_j"][0]
    else:
        np.testing.assert_array_equal(losses, 0)
        assert np.ptp(case["total_energy_trace_j"]) < 1e-12
    assert np.max(abs(state[15:])) > 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"depth": 2},
        {"depth": True},
        {"depth": 1.5},
        {"refinement": 3},
        {"refinement": True},
        {"duration": 0},
        {"duration": 1e-16},
        {"duration": 0.101},
        {"duration": 0.0015},
        {"damping": -1},
        {"damping": True},
        {"connected": 1},
    ],
)
def test_invalid_controls_rejected(kwargs):
    with pytest.raises(ValueError):
        simulate(**({"depth": 0} | kwargs))
