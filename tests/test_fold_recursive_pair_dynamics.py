"""Controls for isolated recursive pair dynamic self-similarity."""

import numpy as np
import pytest

from scripts.report_fold_recursive_pair_dynamics import (
    PARENT_SCALES,
    REFERENCE_SAMPLE_TIMES_S,
    initial_state,
    report,
    simulate,
)


@pytest.fixture(scope="module")
def result():
    return report()


def test_corresponding_pair_trajectories_collapse(result):
    for scale in PARENT_SCALES:
        row = result["comparisons"][str(scale)]
        assert row["coordinate_max_difference"] < 1e-10
        assert row["scale_normalized_rate_max_difference"] < 1e-9
        assert row["normalized_mechanical_energy_max_difference"] < 1e-12
        assert row["normalized_loss_max_difference"] < 1e-12
        assert row["normalized_connector_potential_max_difference"] < 1e-12
        assert row["normalized_endpoint_work_max_difference"] < 1e-12


def test_pair_energy_accounts_close(result):
    for run in result["runs"].values():
        assert max(run["max_node_residual_j"]) < 1e-10
        assert run["max_edge_residual_j"] < 1e-10
        assert run["max_total_residual_j"] < 1e-10


def test_reference_time_grid_is_shared(result):
    for run in result["runs"].values():
        assert [row["reference_time_s"] for row in run["snapshots"]] == list(
            REFERENCE_SAMPLE_TIMES_S
        )


def test_child_uptake_history_is_scale_invariant_when_defined(result):
    for values_by_scale in result["child_uptake_fraction_by_reference_time"].values():
        fractions = list(values_by_scale.values())
        if fractions[0] is None:
            assert all(value is None for value in fractions)
            continue
        assert all(value is not None for value in fractions)
        assert max(fractions) - min(fractions) < 1e-10
        assert all(np.isfinite(value) and value >= 0 for value in fractions)


def test_initial_conditions_are_dynamically_corresponding():
    states = [initial_state(scale) for scale in PARENT_SCALES]
    q = [state[:10].reshape(2, 5)[:, :2] for state in states]
    for state_q in q[1:]:
        np.testing.assert_allclose(state_q, q[0], rtol=0, atol=0)
    base_rates = states[0][:10].reshape(2, 5)[:, 2:4]
    for scale, state in zip(PARENT_SCALES, states, strict=True):
        rates = state[:10].reshape(2, 5)[:, 2:4]
        np.testing.assert_allclose(scale * rates, base_rates, rtol=0, atol=0)


def test_claim_boundaries_remain_explicit(result):
    assert not result["connector_coefficients_changed"]
    assert not result["material_scaling_law_changed"]
    assert not result["damping_law_changed"]
    assert not result["embedded_tree_loading_reproduced"]
    assert not result["new_recursive_coupling_introduced"]


@pytest.mark.parametrize("scale", [0, 0.125, 0.75, 2, True, None])
def test_invalid_parent_scale_rejected(scale):
    with pytest.raises(ValueError):
        simulate(scale)
