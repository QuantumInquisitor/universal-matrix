"""Independent cubic identity, potential, quadrature and energy controls."""

import numpy as np
import pytest

from scripts import report_wave_harmonics as m


def test_cubic_cosine_identity_generates_third_without_harmonic_drive():
    model = m.Galerkin()
    amplitude = 0.2
    q = np.array((amplitude, 0, 0))
    np.testing.assert_allclose(
        model.cubic(q), [3 * amplitude**3 / 4, amplitude**3 / 4, 0], atol=2e-17
    )
    state = np.r_[q, np.zeros(5)]
    assert model.rhs(0, state)[4] == pytest.approx(-(amplitude**3) / 4)
    assert abs(model.rhs(0, state)[5]) < 2e-17
    assert model.quartic(q) == pytest.approx(3 * amplitude**4 / 16)
    np.testing.assert_array_equal(m.Galerkin(beta=0).cubic(q), 0)


def test_potential_gradient_independent_difference():
    model = m.Galerkin()
    q = np.array((0.2, -0.09, 0.06))
    h = 1e-6
    gradient = np.array(
        [
            (model.quartic(q + h * axis) - model.quartic(q - h * axis)) / (2 * h)
            for axis in np.eye(3)
        ]
    )
    np.testing.assert_allclose(gradient, model.cubic(q), rtol=1e-9, atol=1e-12)


def test_resolved_quadrature_and_basis_normalization():
    model = m.Galerkin()
    np.testing.assert_allclose(
        model.basis @ model.basis.T / model.points, np.eye(3) / 2, atol=3e-16
    )
    fine = m.Galerkin(points=257)
    q = np.array((0.3, 0.14, -0.2))
    np.testing.assert_allclose(model.cubic(q), fine.cubic(q), atol=2e-16)
    assert model.quartic(q) == pytest.approx(fine.quartic(q), abs=2e-17)


def test_energy_directional_derivative_and_missing_work_negative_control():
    model = m.Galerkin()
    t = 0.7
    state = np.array((0.2, -0.1, 0.04, -0.07, 0.03, 0.02, 0, 0))
    d = model.rhs(t, state)
    h = 1e-6
    derivative = (model.energy(t + h, state + h * d) - model.energy(t - h, state - h * d)) / (2 * h)
    assert derivative == pytest.approx(d[-2] - d[-1], abs=3e-11)
    assert abs(derivative + d[-1]) > 1e-3


def test_pump_off_short_integration_and_ledger():
    run = m.simulate(periods=1, modulation=0)
    assert run["completed"]
    np.testing.assert_array_equal(run["drive_work"], 0)
    assert np.min(np.diff(run["damping_loss"])) >= 0
    assert np.max(np.diff(run["total_energy"])) < 0
    assert run["max_abs_balance_residual"] < 1e-10
    assert run["max_abs_q_per_mode"][1] > 1e-6


@pytest.mark.parametrize(
    "kwargs",
    [
        {"modes": (1, 5)},
        {"modes": (True,)},
        {"points": 32},
        {"points": True},
        {"beta": -1},
        {"beta": np.nan},
        {"damping": -1},
        {"modulation": 1},
    ],
)
def test_invalid_model(kwargs):
    with pytest.raises(ValueError):
        m.Galerkin(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"periods": 0},
        {"periods": 21},
        {"periods": True},
        {"steps_per_period": 0},
        {"rtol": np.nan},
        {"rtol": 1},
    ],
)
def test_invalid_run(kwargs):
    with pytest.raises(ValueError):
        m.simulate(**kwargs)


def test_mismatched_time_comparison_rejected():
    with pytest.raises(ValueError, match="identical sample times"):
        m.compare(dict(times=[0, 1]), dict(times=[0, 2]), kind="truncation")


@pytest.mark.parametrize("value", ["1.0", 1 + 0j, True, [1]])
def test_numeric_strings_and_nonreal_values_rejected(value):
    with pytest.raises(ValueError):
        m.finite(value, "value")
