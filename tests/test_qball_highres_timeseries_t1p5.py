import pytest

from src.qball_highres_timeseries import TimeSeriesSample, summarize_channel
from src.qball_highres_timeseries_t1p5 import (
    _extended,
    _turning_events,
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


def test_turning_events_record_kind_and_time():
    samples = (
        _sample(0, 1.0, 1.0),
        _sample(25, 0.9, 1.1),
        _sample(50, 0.95, 1.2),
        _sample(75, 0.92, 1.3),
    )

    events = _turning_events(samples, attribute="peak_ratio")

    assert [(event.kind, event.time) for event in events] == [
        ("minimum", pytest.approx(0.025)),
        ("maximum", pytest.approx(0.050)),
    ]


def test_extended_reports_turning_interval():
    summary = summarize_channel(
        (
            _sample(0, 1.0, 1.0),
            _sample(25, 0.9, 1.1),
            _sample(50, 0.95, 1.2),
            _sample(75, 0.92, 1.3),
        )
    )

    extended = _extended(summary)

    assert extended.peak_turning_intervals == pytest.approx((0.025,))
    assert extended.radius_turning_events == ()
