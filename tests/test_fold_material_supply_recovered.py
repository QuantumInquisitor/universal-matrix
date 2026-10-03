"""Recovered instantaneous controls for accepted constitutive material supply.

Ported from preserved scratch tests; no scratch solver or capacity policy is used.
"""

import numpy as np
import pytest

from scripts import fold_material_multiscale as passive
from scripts import report_fold_material_supply as supply
from scripts.report_fold_hierarchy import compile_hierarchy


def nonstationary_state():
    state = supply.initial_state()
    blocks = state[:36].reshape(4, 9)
    blocks[:, :2] += [[0.01, -0.02], [-0.01, 0.015], [0.005, 0.01], [-0.008, -0.01]]
    blocks[:, 2:4] = [[0.02, -0.01], [-0.01, 0.03], [0.015, -0.02], [0.01, 0.01]]
    blocks[:, 4] *= 0.6
    # Nonzero cumulative ledgers require true centered differences, not
    # plus-state divided by epsilon with an assumed zero baseline.
    blocks[:, 5:] = np.arange(1, 17).reshape(4, 4) * 1e-8
    state[36:] = np.arange(1, 13) * 1e-8
    return state


@pytest.mark.parametrize("control", ["gain_zero", "reserve_zero"])
def test_constitutive_passive_reduction_with_external_source_off(control):
    y = nonstationary_state()
    blocks = y[:36].reshape(4, 9)
    if control == "reserve_zero":
        blocks[:, 4] = 0
    powered = supply.rhs(y, power_density=0, gain=0 if control == "gain_zero" else supply.GAIN)
    passive_state = np.r_[blocks[:, [0, 1, 2, 3, 6]].ravel(), y[36:44]]
    expected = passive.rhs(passive_state, supply.BASE_SIZES, supply.EDGES)
    actual = powered[:36].reshape(4, 9)
    np.testing.assert_allclose(
        actual[:, :4], expected[:20].reshape(4, 5)[:, :4], atol=1e-20, rtol=1e-14
    )
    np.testing.assert_allclose(
        actual[:, 6], expected[:20].reshape(4, 5)[:, 4], atol=1e-20, rtol=1e-14
    )
    np.testing.assert_allclose(powered[36:44], expected[20:], atol=1e-20, rtol=1e-14)
    np.testing.assert_array_equal(actual[:, 5], 0)
    np.testing.assert_array_equal(actual[:, 7], 0)
    np.testing.assert_array_equal(powered[44:], 0)


@pytest.mark.parametrize("eps", [1e-5, 5e-6])
def test_independent_owned_energy_directional_derivatives_with_input(eps):
    y = nonstationary_state()
    direction = supply.rhs(y)
    layout = compile_hierarchy(4, supply.EDGES, supply.TREE)
    plus = supply.measure(y + eps * direction, supply.BASE_SIZES, supply.EDGES, layout)
    minus = supply.measure(y - eps * direction, supply.BASE_SIZES, supply.EDGES, layout)
    rates = direction[:36].reshape(4, 9)
    work = direction[36:44].reshape(4, 2)
    incident = np.zeros(4)
    for e, (a, b, _) in enumerate(supply.EDGES):
        incident[a] += work[e, 0]
        incident[b] += work[e, 1]
    # Potential/kinetic values come from measurement, not RHS force contractions.
    np.testing.assert_allclose(
        (plus[0] - minus[0]) / (2 * eps),
        rates[:, 5] - rates[:, 6] + incident,
        atol=2e-13,
        rtol=2e-6,
    )
    np.testing.assert_allclose(
        (plus[1] - minus[1]) / (2 * eps), -work.sum(axis=1), atol=1e-15, rtol=2e-7
    )
    np.testing.assert_allclose(
        rates[:, 4] + rates[:, 5] + rates[:, 7] + rates[:, 8],
        direction[44:],
        atol=1e-21,
        rtol=1e-14,
    )
    for path in layout["groups"]:
        upper, lower = plus[4][path], minus[4][path]
        measured = (upper["accounted_energy_j"] - lower["accounted_energy_j"]) / (2 * eps)
        boundary = (upper["boundary_work_j"] - lower["boundary_work_j"]) / (2 * eps)
        supplied = (upper["input_j"] - lower["input_j"]) / (2 * eps)
        assert measured == pytest.approx(boundary + supplied, abs=3e-13, rel=2e-6)
        if path == "root":
            assert abs(boundary) < 1e-20
            assert supplied > 1e-6
            # Omitting external input leaves a resolvable apparent energy source.
            assert abs(measured - boundary) > 1e-6


def test_full_derivative_homothety_includes_reserve_and_external_input():
    y = nonstationary_state()
    baseline = supply.rhs(y)
    g = 0.5
    scaled = y.copy()
    blocks = scaled[:36].reshape(4, 9)
    blocks[:, 2:4] /= g
    blocks[:, 4:] *= g**3
    scaled[36:] *= g**3
    expected = baseline.copy()
    rates = expected[:36].reshape(4, 9)
    rates[:, :2] /= g
    rates[:, 2:4] /= g**2
    rates[:, 4:] *= g**2
    expected[36:] *= g**2
    actual = supply.rhs(scaled, tuple(g * s for s in supply.BASE_SIZES), supply.EDGES)
    np.testing.assert_allclose(actual, expected, rtol=2e-13, atol=1e-20)
    # This fixture cannot pass through a dormant/zero-input special case.
    assert np.all(baseline[44:] > 0)
    assert np.max(abs(actual[44:] - baseline[44:])) > 1e-6
