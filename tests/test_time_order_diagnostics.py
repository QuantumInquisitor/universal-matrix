import numpy as np
import pytest

from src.time_order_diagnostics import stroboscopic_diagnostics


def test_imposed_two_cycle_signal_has_strong_signature_without_crystal_claim():
    signal = (-1.0) ** np.arange(128)
    result = stroboscopic_diagnostics(np.c_[signal, 0.3 * signal])
    assert result["two_cycle_error"] == 0
    assert result["one_cycle_error"] == pytest.approx(2)
    assert result["alternating_coherence"] == pytest.approx(1)
    assert result["late_to_early_rms"] == pytest.approx(1)
    assert "not evidence sufficient" in result["classification"]


def test_stationary_or_numerically_tiny_signal_cannot_pass_as_oscillation():
    for signal in (np.ones(128), 1e-12 * (-1.0) ** np.arange(128)):
        result = stroboscopic_diagnostics(signal)
        assert not result["signal_resolved"]
        assert result["two_cycle_error"] is None


def test_decay_and_growth_are_visible_despite_alternation():
    for exponent in (-0.03, 0.03):
        result = stroboscopic_diagnostics(
            (-1.0) ** np.arange(128) * np.exp(exponent * np.arange(128))
        )
        assert result["late_to_early_rms"] == pytest.approx(np.exp(64 * exponent))
        assert result["two_cycle_error"] > 0.01


def test_four_cycle_is_not_mistaken_for_two_cycle():
    result = stroboscopic_diagnostics(np.cos(np.pi / 2 * np.arange(128)))
    assert result["alternating_coherence"] < 1e-12
    assert result["two_cycle_error"] == pytest.approx(2)


def test_velocity_coordinate_resolves_displacement_sampling_node():
    result = stroboscopic_diagnostics(np.c_[np.zeros(128), (-1.0) ** np.arange(128)])
    assert result["signal_resolved"]
    assert result["alternating_coherence"] == pytest.approx(1)


@pytest.mark.parametrize(
    "signal", ([], [1] * 15, [np.nan] * 16, np.zeros((16, 0)), np.ones(16) * 1j)
)
def test_invalid_records(signal):
    with pytest.raises(ValueError):
        stroboscopic_diagnostics(signal)
