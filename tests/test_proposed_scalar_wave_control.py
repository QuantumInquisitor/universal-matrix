from dataclasses import replace
import math

import numpy as np
import pytest

from src.proposed_scalar_wave_control import RingMode, energy_audit, floquet_audit


def mode(**changes):
    return replace(RingMode(2 * math.pi, 1.0, 1, 0.0, 0.02, 0.2, 2.0), **changes)


def constant_oscillator_matrix(omega, damping, period):
    # Closed-form matrix exponential, including the critical Jordan case.
    b = np.array(((damping, 1.0), (-omega * omega, -damping)))
    discriminant = damping * damping - omega * omega
    if discriminant == 0:
        c, s = 1.0, period
    elif discriminant > 0:
        root = math.sqrt(discriminant)
        c, s = math.cosh(root * period), math.sinh(root * period) / root
    else:
        root = math.sqrt(-discriminant)
        c, s = math.cos(root * period), math.sin(root * period) / root
    return math.exp(-damping * period) * (c * np.eye(2) + s * b)


@pytest.mark.parametrize("damping", (0.0, 0.02, 1.0, 1.4))
def test_unmodulated_matrix_matches_all_analytic_damping_regimes(damping):
    reference = mode(modulation=0, damping_per_s=damping, drive_rad_s=1.6)
    computed = floquet_audit(reference, steps=1024)
    expected = constant_oscillator_matrix(1, damping, reference.period_s)
    np.testing.assert_allclose(computed["monodromy"], expected, atol=2e-11, rtol=2e-10)


def test_unmodulated_fourth_order_refinement_checks_phase_not_just_determinant():
    reference = mode(modulation=0, drive_rad_s=1.6)
    exact = constant_oscillator_matrix(1, 0.02, reference.period_s)
    errors = [np.linalg.norm(floquet_audit(reference, steps=n)["monodromy"] - exact)
              for n in (64, 128, 256)]
    assert 15 < errors[0] / errors[1] < 17
    assert 15 < errors[1] / errors[2] < 17


@pytest.mark.parametrize("ratio,growing", ((1.5, False), (2.0, True), (2.5, False)))
def test_refined_parametric_onset_and_liouville_determinant(ratio, growing):
    reference = mode(drive_rad_s=ratio)
    audits = [floquet_audit(reference, steps=n) for n in (256, 512, 1024)]
    expected = math.exp(-2 * reference.damping_per_s * reference.period_s)
    for result in audits:
        assert (result["spectral_radius"] > 1.01) == growing
        assert abs(np.linalg.det(result["monodromy"]) - expected) < 5e-10
        if not growing:
            assert result["spectral_radius"] < 0.96
    np.testing.assert_allclose(audits[1]["monodromy"], audits[2]["monodromy"], atol=2e-10, rtol=0)
    assert abs(audits[1]["growth_rate_per_s"] - audits[2]["growth_rate_per_s"]) < 1e-10


def test_pump_and_loss_controls_change_the_onset():
    assert floquet_audit(mode())["growth_rate_per_s"] > 0.02
    assert floquet_audit(mode(modulation=0))["growth_rate_per_s"] == pytest.approx(-0.02, abs=1e-11)
    assert floquet_audit(mode(damping_per_s=0.08))["growth_rate_per_s"] < -0.02


def test_independent_drive_and_dissipation_quadratures_balance_and_refine():
    audits = [energy_audit(mode(), steps=n, periods=8) for n in (128, 256, 512)]
    residuals = [abs(audit["balance_residual"]) for audit in audits]
    # A full-period balance can cancel leading errors; demand convergence,
    # while the analytic matrix comparison separately checks RK4's order.
    assert residuals[0] / residuals[1] > 8
    assert residuals[1] / residuals[2] > 8
    result = audits[-1]
    assert result["drive_work"] > result["damping_loss"] > 0
    assert result["energy_after"] > result["energy_before"]
    assert residuals[-1] < 1e-8


def test_unforced_energy_loss_and_undamped_conservation():
    for damping in (0.0, 0.02):
        result = energy_audit(mode(modulation=0, damping_per_s=damping), periods=4)
        assert result["drive_work"] == 0
        assert abs(result["balance_residual"]) < 2e-10
        if damping == 0:
            assert result["damping_loss"] == 0
        else:
            assert result["damping_loss"] > 0
            assert result["energy_after"] < result["energy_before"]


@pytest.mark.parametrize("scale", (0.2, 3.0, 100.0))
def test_joint_geometry_and_time_scaling_preserves_onset_and_rescales_energy(scale):
    original = mode(gap_rad_s=0.75, drive_rad_s=2.5)
    scaled = replace(original, circumference_m=scale * original.circumference_m,
                     gap_rad_s=original.gap_rad_s / scale,
                     damping_per_s=original.damping_per_s / scale,
                     drive_rad_s=original.drive_rad_s / scale)
    a, b = floquet_audit(original), floquet_audit(scaled)
    change = np.diag((1.0, 1.0 / scale))
    np.testing.assert_allclose(b["monodromy"], change @ a["monodromy"] @ np.linalg.inv(change),
                               atol=2e-12, rtol=2e-12)
    assert b["spectral_radius"] == pytest.approx(a["spectral_radius"], rel=2e-13)
    assert b["growth_rate_per_s"] == pytest.approx(a["growth_rate_per_s"] / scale, rel=2e-12)
    e1 = energy_audit(original, velocity_m_s=0.3, periods=3)
    e2 = energy_audit(scaled, velocity_m_s=0.3 / scale, periods=3)
    for name in ("energy_before", "energy_after", "drive_work", "damping_loss"):
        assert e2[name] == pytest.approx(e1[name] / scale**2, rel=2e-12, abs=1e-14)


def test_holding_a_nonzero_gap_fixed_breaks_geometry_time_similarity():
    original = mode(gap_rad_s=0.75, drive_rad_s=2.5)
    fixed_gap = replace(original, circumference_m=3 * original.circumference_m,
                        damping_per_s=original.damping_per_s / 3,
                        drive_rad_s=original.drive_rad_s / 3)
    assert fixed_gap.omega_rad_s != pytest.approx(original.omega_rad_s / 3)
    assert floquet_audit(original)["spectral_radius"] > 1.01
    assert floquet_audit(fixed_gap)["spectral_radius"] < 0.99


@pytest.mark.parametrize("changes", ({"circumference_m": 0}, {"wave_speed_m_s": -1},
    {"mode_number": 1.5}, {"mode_number": True}, {"mode_number": 0}, {"gap_rad_s": -1},
    {"damping_per_s": -1}, {"modulation": 1}, {"modulation": -0.1},
    {"drive_rad_s": 0}, {"drive_rad_s": float("nan")}, {"gap_rad_s": float("inf")},
    {"gap_rad_s": 1e200}))
def test_invalid_or_unresolved_model_parameters_are_rejected(changes):
    with pytest.raises(ValueError):
        mode(**changes)


@pytest.mark.parametrize("steps", (True, 15, 32.5))
def test_integration_resolution_must_be_an_explicit_integer(steps):
    with pytest.raises(ValueError):
        floquet_audit(mode(), steps=steps)


@pytest.mark.parametrize("steps", (256, 512, 1024))
def test_tiny_period_damping_cannot_silently_be_reported_as_zero_growth(steps):
    reference = mode(modulation=0, drive_rad_s=1e14)
    # The true unmodulated growth rate is -0.02/s at every drive period.
    # These increments are too small to retain the decay in float64 RK4.
    for audit in (floquet_audit, energy_audit):
        with pytest.raises(ValueError, match="damping is unresolved"):
            audit(reference, steps=steps)
