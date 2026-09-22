import pytest

from src.qball_highres_timeseries import TimeSeriesSample, summarize_channel
from src.qball_highres_timeseries_t1p5 import _extended
from src.qball_highres_timeseries_t2 import HighResolutionTimeSeriesT2


def _sample(step, peak, radius):
    return TimeSeriesSample(
        step=step,
        time=step * 0.001,
        energy_drift=0.0,
        charge_drift=0.0,
        peak_ratio=peak,
        radius_ratio=radius,
    )


def test_half_cycle_candidate_uses_first_opposite_kind_turning_pair():
    perturbed = _extended(
        summarize_channel(
            (
                _sample(0, 1.0, 1.0),
                _sample(25, 0.9, 1.01),
                _sample(50, 0.95, 1.02),
                _sample(75, 0.92, 1.03),
            )
        )
    )
    direct = perturbed

    class Result:
        steps = 2000
        dt = 0.001
        sample_stride = 25

    run = HighResolutionTimeSeriesT2(
        result=Result(),
        direct=direct,
        perturbed=perturbed,
    )

    assert run.perturbed_peak_half_cycle_candidate == pytest.approx(0.025)


def test_half_cycle_candidate_absent_with_single_turning_event():
    perturbed = _extended(
        summarize_channel(
            (
                _sample(0, 1.0, 1.0),
                _sample(25, 0.9, 1.01),
                _sample(50, 0.95, 1.02),
            )
        )
    )

    class Result:
        steps = 2000
        dt = 0.001
        sample_stride = 25

    run = HighResolutionTimeSeriesT2(
        result=Result(),
        direct=perturbed,
        perturbed=perturbed,
    )

    assert run.perturbed_peak_half_cycle_candidate is None
