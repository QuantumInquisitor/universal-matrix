"""Independent energy, reduction and similarity controls for active scaling."""

import numpy as np
import pytest

from scripts.report_fold_active_multiscale import (
    BASE_SIZES,
    EDGES,
    TREE,
    comparison,
    configuration,
    initial_state,
    measure,
    rhs,
    simulate,
)
from scripts.report_fold_hierarchy import compile_hierarchy
from scripts.report_fold_multiscale import rhs as passive_rhs
from scripts.report_fold_reservoir import rhs as reservoir_rhs


def test_unit_body_reduces_to_existing_reservoir():
    y = initial_state((1,), ())
    np.testing.assert_allclose(rhs(y, (1,), ()), reservoir_rhs(y), rtol=1e-14, atol=1e-20)


@pytest.mark.parametrize("control", ["gain_zero", "reserve_zero"])
def test_passive_reduction(control):
    y = initial_state(BASE_SIZES, EDGES)
    b = y[:36].reshape(4, 9)
    if control == "reserve_zero":
        b[:, 4] = 0
    d = rhs(y, BASE_SIZES, EDGES, gain=0 if control == "gain_zero" else 4)
    passive = np.r_[b[:, [0, 1, 2, 3, 6]].ravel(), y[36:]]
    expected = passive_rhs(passive, BASE_SIZES, EDGES)
    np.testing.assert_allclose(
        d[:36].reshape(4, 9)[:, [0, 1, 2, 3, 6]],
        expected[:20].reshape(4, 5),
        rtol=1e-14,
        atol=1e-20,
    )
    np.testing.assert_allclose(d[36:], expected[20:])
    assert np.all(d[:36].reshape(4, 9)[:, [5, 7]] == 0)


def test_all_derivative_scalings_and_fixed_leakage_counterexample():
    y = initial_state(BASE_SIZES, EDGES)
    y[:36].reshape(4, 9)[:, 2:4] = [[0.03, -0.02], [-0.01, 0.04], [0.02, 0.01], [-0.04, -0.03]]
    a = rhs(y, BASE_SIZES, EDGES)
    g = 0.5
    z = y.copy()
    b = z[:36].reshape(4, 9)
    b[:, 2:4] /= g
    b[:, 4:] *= g**3
    z[36:] *= g**3
    expected = a.copy()
    e = expected[:36].reshape(4, 9)
    e[:, :2] /= g
    e[:, 2:4] /= g**2
    e[:, 4:] *= g**2
    expected[36:] *= g**2
    actual = rhs(z, tuple(g * s for s in BASE_SIZES), EDGES)
    np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-20)
    fixed_base = rhs(y, BASE_SIZES, EDGES, fixed_leakage=True)[:36].reshape(4, 9)
    fixed_half = rhs(z, tuple(g * s for s in BASE_SIZES), EDGES, fixed_leakage=True)[:36].reshape(
        4, 9
    )
    np.testing.assert_allclose(fixed_half[:, 8], g**3 * fixed_base[:, 8])
    assert not np.allclose(fixed_half[:, 8], g**2 * fixed_base[:, 8], atol=1e-15)


def test_equilibrium_leakage_closed_form():
    # Independently evaluate the exact reserve trajectory at equal reference times.
    from scripts.report_fold_dynamics import Q0

    for s in (1, 0.5):
        time = 0.7 * s
        reserve = 2e-5 * s**3 * np.exp(-0.15 * time / s)
        y = np.r_[Q0, 0.0, 0.0, reserve, 0.0, 0.0, 0.0, 2e-5 * s**3 - reserve]
        d = rhs(y, (s,), ())
        np.testing.assert_allclose(d[:4], 0, atol=1e-20)
        assert d[4] == pytest.approx(-0.15 / s * reserve)
        assert d[8] == -d[4]
        assert reserve / s**3 == pytest.approx(2e-5 * np.exp(-0.15 * 0.7))
    assert np.exp(-0.15 * 0.7) != pytest.approx(np.exp(-0.15 * 0.7 * 0.5))


def test_independent_group_energy_derivative():
    y = initial_state(BASE_SIZES, EDGES)
    y[:36].reshape(4, 9)[:, 2:4] = [[0.03, -0.02], [-0.01, 0.04], [0.02, 0.01], [-0.04, -0.03]]
    layout = compile_hierarchy(4, EDGES, TREE)
    d = rhs(y, BASE_SIZES, EDGES)
    eps = 1e-6
    plus = measure(y + eps * d, BASE_SIZES, EDGES, layout)[3]
    minus = measure(y - eps * d, BASE_SIZES, EDGES, layout)[3]
    powers = d[36:].reshape(4, 2)
    for path, members in layout["groups"].items():
        boundary = sum(
            powers[e, 0] if a in members else powers[e, 1]
            for e, (a, b, _) in enumerate(EDGES)
            if (a in members) != (b in members)
        )
        difference = (plus[path]["accounted_energy_j"] - minus[path]["accounted_energy_j"]) / (
            2 * eps
        )
        assert difference == pytest.approx(boundary, rel=1e-6, abs=1e-13)


@pytest.mark.parametrize("value", [True, np.bool_(True), "4", complex(4), float("nan"), -1, 11])
def test_invalid_gain(value):
    with pytest.raises(ValueError):
        rhs(initial_state(BASE_SIZES, EDGES), BASE_SIZES, EDGES, gain=value)


@pytest.mark.parametrize(
    "kwargs",
    [{"global_scale": 0.4}, {"refinement": True}, {"omitted_debit": 4}, {"omitted_debit": True}],
)
def test_invalid_run(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)


def test_rejects_negative_reserve_and_duplicate_edges():
    y = initial_state(BASE_SIZES, EDGES)
    y[4] = -1e-20
    with pytest.raises(ValueError, match="negative reservoir"):
        rhs(y, BASE_SIZES, EDGES)
    with pytest.raises(ValueError):
        configuration((1, 0.5), ((0, 1, 1), (1, 0, 1)))


@pytest.fixture(scope="module")
def runs():
    return simulate(), simulate(0.5), simulate(omitted_debit=1)


def test_run_energy_supply_similarity_and_fault_localization(runs):
    base, half, broken = runs
    for run in (base, half):
        for key in (
            "max_node_mechanical_residual_j",
            "max_node_reservoir_residual_j",
            "max_edge_residual_j",
        ):
            assert max(run[key]) < 1e-13
        assert max(run["max_group_residual_j"].values()) < 1e-13
        assert min(run["finite_supply"]["minimum_reserve_j"]) >= 0
        assert max(run["finite_supply"]["maximum_reserve_step_increase_j"]) <= 0
        final = run["trace"][-1]
        assert np.all(
            np.array(final["work_j"])
            <= 0.8 * np.array(run["finite_supply"]["initial_reserve_j"]) + 1e-15
        )
    for key, error in comparison(half, base).items():
        assert np.max(error) < (1e-12 if key in ("q", "rates") else 1e-16)
    assert broken["max_node_reservoir_residual_j"][1] > 1e-12
    assert max(broken["max_node_reservoir_residual_j"][i] for i in (0, 2, 3)) < 1e-13
    assert max(broken["max_node_mechanical_residual_j"]) < 1e-13
    assert broken["max_group_residual_j"]["root"] > 1e-12
    assert broken["max_group_residual_j"]["root/0"] > 1e-12
    assert broken["max_group_residual_j"]["root/1"] < 1e-13
