"""Independent controls for mixed-size mapped networks."""

import numpy as np
import pytest

from scripts.fold_material_multiscale import (
    BASE_SIZES,
    EDGES,
    comparison,
    configuration,
    connector,
    initial_state,
    rhs,
    simulate,
)
from scripts.report_fold_dynamics import Q0


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


def test_unit_node_equivalence_to_material_dynamics():
    from scripts.report_fold_dynamics import rhs as original_rhs

    y = initial_state((1.0,), ())
    expected = original_rhs(0.0, np.r_[y[:4], 0.0, y[4]], potential="constitutive")
    np.testing.assert_allclose(
        rhs(y, (1.0,), ()), expected[[0, 1, 2, 3, 5]], rtol=1e-14, atol=1e-20
    )


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
    assert broken["max_edge_residual_j"][1] > 1e-13
    assert broken["max_edge_residual_j"][1] > 100 * max(base["max_edge_residual_j"])
    assert max(broken["max_edge_residual_j"][i] for i in (0, 2, 3)) < 1e-13
    assert max(broken["max_node_residual_j"]) < 1e-13
    assert broken["max_group_residual_j"]["root"] > 1e-13
    assert broken["max_group_residual_j"]["root"] > 100 * base["max_group_residual_j"]["root"]
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
    from scripts.fold_material_multiscale import TREE, measure
    from scripts.report_fold_hierarchy import compile_hierarchy

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


@pytest.mark.parametrize("scale", [0.25, 0.5, 0.75])
def test_direct_element_scaling_and_fixed_dimension_negative_controls(scale):
    from scripts.fold_material_multiscale import scaled_material
    from scripts.report_fold_constitutive import constitutive

    q = Q0 + (0.04, -0.03)
    base = scaled_material(q)
    scaled = scaled_material(q, scale)
    fixed = constitutive(q, length_m=0.1 * scale)
    for kind, wrong_exponent in (("panels", 2), ("bridges", 1)):
        for b, s, f in zip(base[kind], scaled[kind], fixed[kind], strict=True):
            assert s["energy_j"] == pytest.approx(b["energy_j"] * scale**3, rel=2e-13)
            np.testing.assert_allclose(
                s["gradient"], np.array(b["gradient"]) * scale**3, rtol=2e-13, atol=1e-20
            )
            assert f["energy_j"] == pytest.approx(b["energy_j"] * scale**wrong_exponent, rel=2e-13)
            assert abs(f["energy_j"] / s["energy_j"] - 1) > 0.1


@pytest.mark.parametrize("scale", [1.0, 0.5, 0.25])
def test_material_gradient_independent_energy_difference(scale):
    from scripts.fold_material_multiscale import scaled_material

    q, direction = Q0 + (0.02, -0.04), np.array((0.3, -0.2))
    eps = 1e-6
    slope = (
        scaled_material(q + eps * direction, scale)["total_energy_j"]
        - scaled_material(q - eps * direction, scale)["total_energy_j"]
    ) / (2 * eps)
    assert slope == pytest.approx(
        np.array(scaled_material(q, scale)["gradient"]) @ direction, rel=1e-8, abs=1e-14
    )


def test_refinement_reduces_balance_error(runs):
    coarse = runs[0]
    fine = simulate(refinement=2)
    assert max(fine["max_node_residual_j"]) < max(coarse["max_node_residual_j"])
    assert max(fine["max_group_residual_j"].values()) < max(coarse["max_group_residual_j"].values())
    np.testing.assert_allclose(fine["final_state"], coarse["final_state"], rtol=1e-6, atol=1e-10)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration_reference": 0.3},
        {"duration_reference": 0},
        {"duration_reference": True},
        {"duration_reference": float("nan")},
        {"duration_reference": 0.015},
        {"refinement": 3},
        {"broken_edge": True},
    ],
)
def test_rejects_extra_invalid_run(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)
