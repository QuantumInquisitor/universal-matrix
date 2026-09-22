import pytest

from src.qball_highres_timeseries import TimeSeriesSample, summarize_channel
from src.qball_highres_timeseries_t2p5 import (
    _extended,
    _same_kind_intervals,
    _valued_turning_events,
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


def test_valued_turning_events_keep_extremum_values():
    samples = (
        _sample(0, 1.0, 1.0),
        _sample(25, 0.90, 1.1),
        _sample(50, 0.95, 1.2),
        _sample(75, 0.92, 1.3),
        _sample(100, 0.96, 1.4),
    )

    events = _valued_turning_events(samples, attribute="peak_ratio")

    assert [(event.kind, event.time, event.value) for event in events] == [
        ("minimum", pytest.approx(0.025), pytest.approx(0.90)),
        ("maximum", pytest.approx(0.050), pytest.approx(0.95)),
        ("minimum", pytest.approx(0.075), pytest.approx(0.92)),
    ]


def test_same_kind_intervals_measure_minimum_to_minimum_period_candidate():
    samples = (
        _sample(0, 1.0, 1.0),
        _sample(25, 0.90, 1.1),
        _sample(50, 0.95, 1.2),
        _sample(75, 0.92, 1.3),
        _sample(100, 0.96, 1.4),
    )
    events = _valued_turning_events(samples, attribute="peak_ratio")

    assert _same_kind_intervals(events, kind="minimum") == pytest.approx((0.050,))
    assert _same_kind_intervals(events, kind="maximum") == ()


def test_extended_reports_adjacent_swing_magnitudes():
    summary = summarize_channel(
        (
            _sample(0, 1.0, 1.0),
            _sample(25, 0.90, 1.1),
            _sample(50, 0.95, 1.2),
            _sample(75, 0.92, 1.3),
            _sample(100, 0.96, 1.4),
        )
    )
    extended = _extended(summary)

    assert extended.adjacent_peak_swings == pytest.approx((0.05, 0.03))
