import pytest

from src.qball_highres_timeseries import TimeSeriesSample, summarize_channel
from src.qball_highres_timeseries_t1 import _extended


def _sample(step, peak, radius):
    return TimeSeriesSample(
        step=step,
        time=step * 0.001,
        energy_drift=0.0,
        charge_drift=0.0,
        peak_ratio=peak,
        radius_ratio=radius,
    )


def test_extended_channel_records_extrema_times():
    summary = summarize_channel(
        (
            _sample(0, 1.0, 1.0),
            _sample(25, 0.99, 1.01),
            _sample(50, 0.995, 1.005),
        )
    )
    result = _extended(summary)
    assert result.peak_min_time == pytest.approx(0.025)
    assert result.peak_max_time == pytest.approx(0.0)
    assert result.radius_min_time == pytest.approx(0.0)
    assert result.radius_max_time == pytest.approx(0.025)
