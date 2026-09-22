import pytest

from src.qball_highres_timeseries import (
    TimeSeriesSample,
    sample_evolution,
    summarize_channel,
)


def _sample(step, peak, radius):
    return TimeSeriesSample(
        step=step,
        time=step * 0.001,
        energy_drift=0.0,
        charge_drift=0.0,
        peak_ratio=peak,
        radius_ratio=radius,
    )


def test_summary_detects_monotonic_relaxation():
    summary = summarize_channel(
        (
            _sample(0, 1.0, 1.0),
            _sample(25, 0.9999, 1.00001),
            _sample(50, 0.9998, 1.00004),
        )
    )
    assert summary.peak_turning_points == 0
    assert summary.radius_turning_points == 0
    assert summary.peak_monotonic_nonincreasing is True
    assert summary.radius_monotonic_nondecreasing is True
    assert summary.peak_endpoint_to_maximum_ratio == pytest.approx(1.0)
    assert summary.radius_endpoint_to_maximum_ratio == pytest.approx(1.0)


def test_summary_detects_turning_behavior():
    summary = summarize_channel(
        (
            _sample(0, 1.0, 1.0),
            _sample(25, 0.999, 1.001),
            _sample(50, 0.9995, 1.0005),
        )
    )
    assert summary.peak_turning_points == 1
    assert summary.radius_turning_points == 1
    assert summary.peak_monotonic_nonincreasing is False
    assert summary.radius_monotonic_nondecreasing is False
    assert summary.peak_endpoint_to_maximum_ratio == pytest.approx(0.5)
    assert summary.radius_endpoint_to_maximum_ratio == pytest.approx(0.5)


def test_sample_evolution_validates_sampling_grid():
    class Dummy:
        energy = 1.0
        charge = 1.0
        lattice_spacing = 1.0
        phi = __import__("numpy").ones((3, 3, 3), dtype=complex)

        def step(self, dt):
            pass

    with pytest.raises(ValueError, match="divisible"):
        sample_evolution(Dummy(), steps=10, sample_stride=6)
