import math

import numpy as np
import pytest

from src.proposed_pressure_storage import PressureStorageNetwork


def pair():
    return PressureStorageNetwork([2e-10, 3e-10], [5e-13], [[1], [-1]])


@pytest.mark.parametrize("time", (0.0, 100.0, 1000.0, 1e8))
def test_two_reservoir_analytic_decay_and_independent_integrated_loss(time):
    model = pair()
    initial = np.array([100000.0, 20000.0])
    c1, c2 = model.compliance_m3_per_pa
    decay = 5e-13 * (1 / c1 + 1 / c2)
    equilibrium = (c1 * initial[0] + c2 * initial[1]) / (c1 + c2)
    difference = (initial[0] - initial[1]) * math.exp(-decay * time)
    expected = equilibrium + np.array([c2, -c1]) * difference / (c1 + c2)
    result = model.audit(initial, time)
    np.testing.assert_allclose(result["pressure_pa"], expected, rtol=2e-15, atol=2e-11)
    expected_loss = 0.5 * c1 * c2 / (c1 + c2) * (initial[0] - initial[1])**2 * -math.expm1(-2 * decay * time)
    assert result["dissipated_energy_j"] == pytest.approx(expected_loss, rel=2e-14, abs=1e-16)
    assert abs(result["energy_balance_residual_j"]) < 4e-16
    assert abs(result["component_volume_residuals_m3"][0]) < 1e-20
    assert abs(result["power_balance_residual_w"]) < 1e-18
    np.testing.assert_allclose(model.relaxation_rates_per_s, [decay], rtol=2e-15)


def test_three_node_reference_and_independent_time_integration_refine():
    model = PressureStorageNetwork(np.array([2, 3, 5]) * 1e-10,
                                   np.array([0.5, 0.8, 0.3]) * 1e-12,
                                   [[1, 0, -1], [-1, 1, 0], [0, -1, 1]])
    initial = np.array([100000.0, 20000.0, 0.0])
    np.testing.assert_allclose(model.equilibrium_pressure(initial), 26000, rtol=2e-16)
    assert model.energy_j(initial) == pytest.approx(1.06)
    assert model.energy_j(initial) - model.energy_j(model.equilibrium_pressure(initial)) == pytest.approx(0.722)
    exact = model.audit(initial, 1000)

    def rhs(y):
        # Independent physical edge equations and work integral, no modal solver.
        p0, p1, p2 = y[:3]
        q01, q12, q20 = 0.5e-12*(p0-p1), 0.8e-12*(p1-p2), 0.3e-12*(p2-p0)
        loss = q01*(p0-p1) + q12*(p1-p2) + q20*(p2-p0)
        return np.array([(q20-q01)/2e-10, (q01-q12)/3e-10, (q12-q20)/5e-10, loss])

    errors = []
    for steps in (128, 256, 512):
        y = np.r_[initial, 0.0]
        dt = 1000 / steps
        for _ in range(steps):
            a = rhs(y)
            b = rhs(y + dt*a/2)
            c = rhs(y + dt*b/2)
            d = rhs(y + dt*c)
            y += dt*(a + 2*b + 2*c + d)/6
        errors.append(np.max(np.abs(y[:3] - exact["pressure_pa"])))
    assert 15 < errors[0]/errors[1] < 18
    assert 15 < errors[1]/errors[2] < 18
    assert abs(y[3] - exact["dissipated_energy_j"]) < 2e-10
    assert abs(model.energy_j(y[:3]) - model.energy_j(initial) + y[3]) < 2e-10


def test_disconnected_components_and_zero_conductance_bridge_keep_separate_equilibria():
    c = np.arange(1, 6) * 1e-10
    b = [[1, 0, 0], [-1, 0, 1], [0, 1, -1], [0, -1, 0], [0, 0, 0]]
    model = PressureStorageNetwork(c, [1e-12, 2e-12, 0], b)
    initial = np.array([100.0, 10.0, -20.0, 60.0, 999.0])
    expected = [40, 40, 180/7, 180/7, 999]
    assert model.components == ((0, 1), (2, 3), (4,))
    np.testing.assert_allclose(model.pressure_at(initial, 1e7), expected, rtol=2e-15)
    result = model.audit(initial, 300)
    np.testing.assert_allclose(result["component_volume_residuals_m3"], 0, atol=3e-23)
    assert result["flow_m3_per_s"][2] == 0
    assert len(model.relaxation_rates_per_s) == 2


def test_link_orientation_and_common_pressure_offset():
    model = pair()
    reversed_model = PressureStorageNetwork(model.compliance_m3_per_pa, [5e-13], -model.incidence)
    initial = np.array([12345.0, -6789.0])
    np.testing.assert_allclose(model.pressure_at(initial, 400), reversed_model.pressure_at(initial, 400), atol=0, rtol=0)
    np.testing.assert_allclose(model.flow_m3_per_s(initial), -reversed_model.flow_m3_per_s(initial), atol=0, rtol=0)
    np.testing.assert_allclose(model.pressure_at(initial+1000, 400), model.pressure_at(initial, 400)+1000, rtol=2e-15)
    np.testing.assert_allclose(model.flow_m3_per_s(initial+1000), model.flow_m3_per_s(initial), atol=0, rtol=0)


def test_unlinked_nodes_and_constant_pressure_do_not_exchange():
    model = PressureStorageNetwork([1, 2, 3], [], np.zeros((3, 0)))
    initial = [10, -20, 3]
    np.testing.assert_array_equal(model.pressure_at(initial, 1e308), initial)
    assert model.audit(initial, 1e308)["dissipated_energy_j"] == 0
    assert model.relaxation_rates_per_s.size == 0
    np.testing.assert_array_equal(pair().flow_m3_per_s([12, 12]), [0])
    np.testing.assert_allclose(pair().pressure_at([12, 12], 1e8), [12, 12], atol=2e-15)


def test_passive_energy_decay_and_initial_pressure_extrema_bound():
    model = pair()
    states = [model.pressure_at([12, -5], time) for time in np.linspace(0, 1000, 20)]
    assert np.max(np.diff([model.energy_j(p) for p in states])) < 0
    assert min(np.min(p) for p in states) >= -5
    assert max(np.max(p) for p in states) <= 12


@pytest.mark.parametrize("c,g,b", [
    ([0, 1], [1], [[1], [-1]]), ([1, -1], [1], [[1], [-1]]),
    ([1, np.nan], [1], [[1], [-1]]), ([1, 1], [np.inf], [[1], [-1]]),
    ([True, False], [1], [[1], [-1]]), ([1+1j, 2], [1], [[1], [-1]]),
    ([1, 1], [-1], [[1], [-1]]), ([1, 1], [1], [[0], [0]]),
    ([1, 1], [1], [[1], [-1+1e-15]]), ([1, 1], [1], [[1], [1]]),
    ([1, 1], [1], [[1], [np.nan]]), ([1, 1], [1], [[1, -1]]),
    ([[1, 1]], [1], [[1], [-1]]), ([1, 1], [[1]], [[1], [-1]]),
    ([], [], np.zeros((0, 0))), (np.ones(129), [], np.zeros((129, 0))),
    ([1, 1], np.ones(4097), np.zeros((2, 4097))),
    ([1e308, 1e308], [1e-308], [[1], [-1]]),
])
def test_invalid_or_unresolved_networks_reject(c, g, b):
    with pytest.raises(ValueError):
        PressureStorageNetwork(c, g, b)


@pytest.mark.parametrize("pressure,time", [([1], 1), ([1, np.nan], 1), ([True, False], 1),
    ([1, 2], np.complex128(1+2j)), ([1, 2], np.complex128(1+0j)),
    ([1, 2], True), ([1, 2], -1), ([1, 2], np.inf), ([1, 2], [1]), ([1e308, -1e308], 1)])
def test_invalid_or_overflowing_states_reject(pressure, time):
    with pytest.raises(ValueError):
        pair().audit(pressure, time)


def test_constructor_copies_inputs():
    c, g, b = np.array([2e-10, 3e-10]), np.array([5e-13]), np.array([[1.0], [-1.0]])
    model = PressureStorageNetwork(c, g, b)
    expected = model.pressure_at([10, 0], 100)
    c[:] = 0
    g[:] = 0
    b[:] = 0
    np.testing.assert_array_equal(model.pressure_at([10, 0], 100), expected)
    with pytest.raises(ValueError):
        model.compliance_m3_per_pa.setflags(write=True)
