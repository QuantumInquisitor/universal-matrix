import math

import pytest

from scripts.report_chiral_phase_controls import field, run
from scripts.report_phase_pattern_controls import field as reciprocal_field


def test_zero_asymmetry_recovers_reciprocal_baseline():
    errors = [0.4, -0.2, 0.8, -0.1]
    velocity, force, imposed, potential = field(errors, 1.2, 0)
    baseline, v = reciprocal_field(errors, [0] * 4, 1.2)
    assert velocity == pytest.approx(baseline)
    assert force == velocity
    assert imposed == [0] * 4
    assert potential == pytest.approx(v)


def test_instantaneous_balance_and_telescoping_identity():
    errors = [0.4, -0.2, 0.8, -0.1, 0.5]
    velocity, force, imposed, _ = field(errors, 1.2, 0.6)
    assert sum(f * h for f, h in zip(force, imposed, strict=True)) == pytest.approx(0, abs=1e-14)
    eps = 1e-6
    plus = field([p + eps * v for p, v in zip(errors, velocity, strict=True)], 1.2, 0.6)[3]
    minus = field([p - eps * v for p, v in zip(errors, velocity, strict=True)], 1.2, 0.6)[3]
    power = sum(h * v - v * v for h, v in zip(imposed, velocity, strict=True))
    assert (plus - minus) / (2 * eps) == pytest.approx(power, abs=1e-9)
    assert power == pytest.approx(-sum(f * f for f in force))


def test_sign_control_changes_transport_not_time_direction():
    plus, zero, minus = [run(asymmetry=a) for a in (0.5, 0, -0.5)]
    assert plus["measured_mode_angular_rate"] > 0
    assert zero["measured_mode_angular_rate"] == pytest.approx(0, abs=1e-14)
    assert minus["measured_mode_angular_rate"] == pytest.approx(-plus["measured_mode_angular_rate"])
    assert minus["final_errors"] == pytest.approx(
        [plus["final_errors"][(-i) % 16] for i in range(16)]
    )
    for case in (plus, minus, zero):
        assert case["final_potential"] < case["initial_potential"]
        assert abs(case["balance_residual"]) < 1e-9


def test_linear_prediction_and_coupling_off():
    small = run(amplitude=0.001)
    assert small["measured_mode_angular_rate"] == pytest.approx(
        small["linearized_mode_angular_rate"], abs=1e-8
    )
    off = run(coupling=0)
    assert off["initial_errors"] == off["final_errors"]
    assert off["integrated_model_work"] == off["integrated_model_dissipation"] == 0


def test_step_convergence_and_explicit_work():
    coarse, fine = run(dt=0.1), run(dt=0.05)
    assert abs(fine["balance_residual"]) < abs(coarse["balance_residual"]) / 8
    assert fine["final_errors"] == pytest.approx(coarse["final_errors"], abs=1e-8)
    assert fine["integrated_model_work"] > 0


def test_small_input_is_rejected_and_decayed_mode_is_unavailable():
    with pytest.raises(ValueError, match="observability floor"):
        run(amplitude=1e-200)
    decayed = run(n=8, duration=60)
    assert decayed["measured_mode_angular_rate"] is None
    assert decayed["first_unobservable_time"] is not None
    assert decayed["trace"][-1]["mode_angle_unwrapped"] is None
    assert abs(decayed["balance_residual"]) < 1e-8


def test_unresolved_step_and_large_amplitude_are_rejected():
    with pytest.raises(ValueError, match="dt \\* coupling"):
        run(dt=0.2)
    with pytest.raises(ValueError, match="amplitude"):
        run(amplitude=1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n": 2},
        {"asymmetry": 1.1},
        {"coupling": -1},
        {"dt": 0},
        {"duration": 0.13},
        {"amplitude": math.nan},
    ],
)
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        run(**kwargs)
