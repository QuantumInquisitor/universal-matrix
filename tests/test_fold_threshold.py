"""Independent equilibrium, damping sign, preparation and short budget checks."""

import numpy as np
import pytest

from scripts import report_fold_threshold as m
from scripts.report_fold_dynamics import DAMPING
from scripts.report_fold_scaling import scaled_mechanical


@pytest.mark.parametrize("power", m.POWERS)
def test_physical_rest_and_nonzero_balanced_ledger_flow(power):
    y = m.initial_state(power, perturbed=False)
    d = m.supply.rhs(y, power_density=power)
    blocks = d[:36].reshape(4, 9)
    np.testing.assert_allclose(blocks[:, :5], 0, atol=2e-21)
    np.testing.assert_allclose(blocks[:, 8], d[44:], atol=2e-21)
    if power:
        assert np.all(d[44:] > 0)
    else:
        np.testing.assert_array_equal(d, 0)


@pytest.mark.parametrize("power", m.POWERS)
def test_independent_small_velocity_damping_sign_and_invariant_reserve(power):
    y = m.initial_state(power, perturbed=False)
    velocity = np.array((1e-5, -2e-5))
    y[:36].reshape(4, 9)[:, 2:4] = velocity
    plus = m.supply.rhs(y, power_density=power)
    y[:36].reshape(4, 9)[:, 2:4] = -velocity
    minus = m.supply.rhs(y, power_density=power)
    odd_acc = (plus[:36].reshape(4, 9)[:, 2:4] - minus[:36].reshape(4, 9)[:, 2:4]) / 2
    powers = []
    for i, size in enumerate(m.supply.BASE_SIZES):
        mass = scaled_mechanical(m.supply.Q0, velocity, size)[0]["mass_matrix"]
        powers.append(float(velocity @ mass @ odd_acc[i]))
    dissipation = sum(size**4 * velocity @ DAMPING @ velocity for size in m.supply.BASE_SIZES)
    expected = (m.feedback_ratio(power) - 1) * dissipation
    assert sum(powers) == pytest.approx(expected, abs=1e-26)
    if power < 6e-7:
        assert sum(powers) < 0
    if power > 6e-7:
        assert sum(powers) > 0
    # At the equilibrium upper boundary feedback can only drain reserves.
    assert np.max(plus[:36].reshape(4, 9)[:, 4]) <= 2e-21
    y[:36].reshape(4, 9)[:, 4] = 0
    assert np.min(m.supply.rhs(y, power_density=power)[:36].reshape(4, 9)[:, 4]) >= 0


def test_same_declared_small_preparation_every_power():
    energies = []
    layout = m.supply.compile_hierarchy(4, m.supply.EDGES, m.supply.TREE)
    for power in m.POWERS:
        y = m.initial_state(power)
        blocks = y[:36].reshape(4, 9)
        np.testing.assert_allclose(blocks[:, :2] - m.supply.Q0, m.PERTURBATION, atol=1e-16)
        assert np.max(abs(m.PERTURBATION)) == 1e-4
        np.testing.assert_array_equal(blocks[:, 2:4], 0)
        np.testing.assert_array_equal(blocks[:, 5:], 0)
        np.testing.assert_array_equal(y[36:], 0)
        e, u, _, _ = m.supply.measure(y[:44], m.supply.BASE_SIZES, m.supply.EDGES, layout)
        energies.append(sum(e) + sum(u))
    assert energies[0] > 0
    np.testing.assert_array_equal(energies, np.full(5, energies[0]))


@pytest.mark.parametrize(
    "options",
    [
        {"duration": 0},
        {"duration": 21},
        {"max_step": 0},
        {"rtol": 0},
        {"power_density": -1},
        {"power_density": float("nan")},
        {"power_density": True},
    ],
)
def test_invalid_settings(options):
    with pytest.raises(ValueError):
        m.simulate(**options)


def test_short_budget_and_finite_scope():
    run = m.simulate(0.08, power_density=9e-7)
    assert run["termination"]["status"] == "completed"
    assert max(run["max_group_residual_j"].values()) < 1e-14
    assert min(run["minimum_reserve_j"]) >= 0
    assert max(run["maximum_reserve_upper_violation_j"]) == 0
    assert max(run["maximum_input_budget_violation_j"]) == 0
    assert max(run["maximum_power_budget_violation_w"]) == 0
    assert run["onset"]["final_to_initial_energy_ratio"] > 0
    assert run["total_received_j"] <= 9e-7 * sum(np.array(m.supply.BASE_SIZES) ** 2) * 0.08
    assert run["onset"]["late_sampled_window"]["endpoint_energy_slope_w"] is None
