"""Independent controls for mixed-size mapped networks."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0
from scripts.report_fold_multiscale import (
    BASE_SIZES,
    EDGES,
    comparison,
    configuration,
    connector,
    initial_state,
    rhs,
    simulate,
)
from scripts.report_fold_scaled_pair import initial_state as pair_initial
from scripts.report_fold_scaled_pair import rhs as pair_rhs


def test_connector_potential_gradient_and_endpoint_reversal():
    qa, qb = Q0 + (0.02, -0.03), Q0 + (-0.01, 0.04)
    u, fa, fb = connector(qa, qb, 0.75, 0.5, 0.7)
    va, vb = np.array((0.3, -0.2)), np.array((-0.1, 0.4))
    eps = 1e-6
    gradient = (
        connector(qa + eps * va, qb + eps * vb, 0.75, 0.5, 0.7)[0]
        - connector(qa - eps * va, qb - eps * vb, 0.75, 0.5, 0.7)[0]
    ) / (2 * eps)
    assert gradient == pytest.approx(-fa @ va - fb @ vb, rel=1e-8, abs=1e-14)
    reverse = connector(qb, qa, 0.5, 0.75, 0.7)
    assert reverse[0] == u
    np.testing.assert_allclose(reverse[1], fb)
    np.testing.assert_allclose(reverse[2], fa)


def test_reduces_to_previously_validated_scaled_pair():
    for g in (1.0, 0.5):
        sizes, edges = (g, 0.5 * g), ((0, 1, 1.0),)
        y = initial_state(sizes, edges, g)
        np.testing.assert_array_equal(y, pair_initial(g))
        np.testing.assert_allclose(rhs(y, sizes, edges), pair_rhs(y, g), rtol=1e-14, atol=1e-20)


def test_derivative_similarity():
    y = initial_state(BASE_SIZES, EDGES)
    a = rhs(y, BASE_SIZES, EDGES)
    g = 0.5
    z = y.copy()
    z[:20].reshape(4, 5)[:, 2:4] /= g
    b = rhs(z, tuple(g * s for s in BASE_SIZES), EDGES)
    expected = a.copy()
    blocks = expected[:20].reshape(4, 5)
    blocks[:, :2] /= g
    blocks[:, 2:4] /= g**2
    blocks[:, 4] *= g**2
    expected[20:] *= g**2
    np.testing.assert_allclose(b, expected, rtol=1e-13, atol=1e-20)


def test_node_permutation_preserves_derivative():
    y = initial_state(BASE_SIZES, EDGES)
    permutation = [2, 0, 3, 1]
    inverse = np.argsort(permutation)
    sizes = tuple(BASE_SIZES[i] for i in permutation)
    edges = tuple((int(inverse[a]), int(inverse[b]), w) for a, b, w in EDGES)
    z = np.r_[y[:20].reshape(4, 5)[permutation].ravel(), y[20:]]
    expected = rhs(y, BASE_SIZES, EDGES)
    actual = rhs(z, sizes, edges)
    np.testing.assert_allclose(
        actual[:20].reshape(4, 5), expected[:20].reshape(4, 5)[permutation], rtol=1e-14, atol=1e-20
    )
    np.testing.assert_allclose(actual[20:], expected[20:])


@pytest.mark.parametrize(
    "sizes,edges",
    [
        ((1, 0.2), ((0, 1, 1),)),
        ((True, 0.5), ((0, 1, 1),)),
        ((1, 0.5), ((0, 1, 1), (1, 0, 1))),
        ((1, 0.5), ((0, 0, 1),)),
        ((1, 0.5), ((0, 1, float("nan")),)),
        ((), ()),
    ],
)
def test_rejects_invalid_configuration(sizes, edges):
    with pytest.raises(ValueError):
        configuration(sizes, edges)


@pytest.fixture(scope="module")
def runs():
    return simulate(), simulate(0.5), simulate(broken_edge=1)


def test_conservation_similarity_and_broken_edge_localization(runs):
    base, half, broken = runs
    for run in (base, half):
        assert max(run["max_node_residual_j"]) < 1e-13
        assert max(run["max_edge_residual_j"]) < 1e-13
        assert max(run["max_group_residual_j"].values()) < 1e-13
    comparisons = comparison(half, base)
    assert np.max(comparisons["coordinate_max_differences"]) < 1e-12
    assert np.max(comparisons["rescaled_rate_max_differences"]) < 1e-12
    assert max(comparisons["rescaled_node_energy_differences_j"]) < 1e-16
    assert broken["max_edge_residual_j"][1] > 1e-12
    assert max(broken["max_edge_residual_j"][i] for i in (0, 2, 3)) < 1e-13
    assert max(broken["max_node_residual_j"]) < 1e-13
    assert broken["max_group_residual_j"]["root"] > 1e-12
    # Bad edge crosses groups; measured boundary work still balances each subgroup.
    assert broken["max_group_residual_j"]["root/0"] < 1e-13
    assert broken["max_group_residual_j"]["root/1"] < 1e-13


@pytest.mark.parametrize(
    "kwargs", [{"global_scale": 0.4}, {"refinement": True}, {"broken_edge": 4}]
)
def test_rejects_invalid_run(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)


def test_independent_group_energy_derivative_equals_boundary_power():
    from scripts.report_fold_hierarchy import compile_hierarchy
    from scripts.report_fold_multiscale import TREE, measure

    y = initial_state(BASE_SIZES, EDGES)
    y[:20].reshape(4, 5)[:, 2:4] = [[0.03, -0.02], [-0.01, 0.04], [0.02, 0.01], [-0.04, -0.03]]
    layout = compile_hierarchy(4, EDGES, TREE)
    derivative = rhs(y, BASE_SIZES, EDGES)
    eps = 1e-6
    plus = measure(y + eps * derivative, BASE_SIZES, EDGES, layout)[3]
    minus = measure(y - eps * derivative, BASE_SIZES, EDGES, layout)[3]
    powers = derivative[20:].reshape(4, 2)
    for path, members in layout["groups"].items():
        boundary = 0.0
        for e, (a, b, _) in enumerate(EDGES):
            if a in members and b not in members:
                boundary += powers[e, 0]
            elif b in members and a not in members:
                boundary += powers[e, 1]
        energy_derivative = (
            plus[path]["accounted_energy_j"] - minus[path]["accounted_energy_j"]
        ) / (2 * eps)
        assert energy_derivative == pytest.approx(boundary, rel=1e-6, abs=1e-13)
