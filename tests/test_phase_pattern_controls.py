import math

import pytest

from scripts.report_phase_pattern_controls import field, order, run


def test_field_is_negative_gradient_and_reciprocal():
    p, targets = [0.2, -0.4, 1.1, 0.7], [0, 0.5, 1, 1.5]
    forces, _ = field(p, targets, 1.3)
    assert abs(sum(forces)) < 1e-14
    for i in range(4):
        plus, minus = p[:], p[:]
        plus[i] += 1e-6
        minus[i] -= 1e-6
        gradient = (field(plus, targets, 1.3)[1] - field(minus, targets, 1.3)[1]) / 2e-6
        assert forces[i] == pytest.approx(-gradient, abs=1e-9)


def test_traveling_pattern_needs_target_aware_observable():
    targets = [math.tau * i / 16 for i in range(16)]
    assert order(targets) < 1e-14
    assert order([p - a for p, a in zip(targets, targets, strict=False)]) == 1


def test_phase_conjugation_and_drift_preserve_model_balance():
    normal = run(duration=4)
    mirrored = run(duration=4, omega=-1, mirror=True)
    reversed_drift = run(duration=4, omega=-1)
    assert normal["final_rotating_phases"] == reversed_drift["final_rotating_phases"]
    assert mirrored["final_lab_phases"] == pytest.approx(
        [-p for p in normal["final_lab_phases"]], abs=1e-12
    )
    assert normal["final_potential"] < normal["initial_potential"]
    assert abs(normal["balance_residual"]) < 1e-6


def test_encoded_modes_are_equivalent_and_mean_phase_is_preserved():
    common, traveling = run(mode=0, duration=4), run(mode=1, duration=4)
    residual = [p - math.tau * i / 16 for i, p in enumerate(traveling["final_rotating_phases"])]
    assert residual == pytest.approx(common["final_rotating_phases"], abs=1e-12)
    assert sum(common["final_rotating_phases"]) == pytest.approx(
        sum(common["initial_rotating_phases"]), abs=1e-12
    )


def test_uncoupled_control_and_step_convergence():
    off = run(coupling=0, duration=4)
    assert off["initial_rotating_phases"] == off["final_rotating_phases"]
    assert off["integrated_model_dissipation"] == 0
    coarse, fine = run(duration=4), run(duration=4, dt=0.0125)
    assert abs(fine["balance_residual"]) < abs(coarse["balance_residual"]) / 8
    assert fine["final_rotating_phases"] == pytest.approx(coarse["final_rotating_phases"], abs=1e-7)


@pytest.mark.parametrize(
    "kwargs", [{"n": 2}, {"dt": 0}, {"coupling": -1}, {"omega": float("nan")}, {"duration": 0.03}]
)
def test_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        run(**kwargs)
