import pytest

from src.qball_highres_timeseries_t2p5 import ValuedTurningEvent
from src.qball_peak_period_classification import classify_peak_period


def event(time, kind, value):
    return ValuedTurningEvent(time=time, kind=kind, value=value)


def test_t2p5_perturbed_trace_separates_tiny_reversal_pair():
    events = (
        event(0.925, "minimum", 0.9944742794),
        event(1.600, "maximum", 0.9965145163),
        event(1.650, "minimum", 0.9965094692),
        event(1.800, "maximum", 0.9965362830),
        event(2.300, "minimum", 0.9961322537),
        event(2.475, "maximum", 0.9963743297),
    )

    result = classify_peak_period(events)

    assert [(left.time, right.time) for left, right in result.removed_modulation_pairs] == [
        (1.600, 1.650)
    ]
    assert [item.time for item in result.retained_events] == pytest.approx(
        [0.925, 1.800, 2.300, 2.475]
    )
    assert result.minimum_intervals == pytest.approx((1.375,))
    assert result.maximum_intervals == pytest.approx((0.675,))
    assert result.candidate_period == pytest.approx(1.025)
    assert result.interval_relative_spread == pytest.approx(0.7 / 1.025)
    assert result.status == "inconsistent_period_candidates"


def test_consistent_same_kind_intervals_support_period_candidate():
    events = (
        event(0.0, "minimum", 0.9),
        event(0.5, "maximum", 1.1),
        event(1.0, "minimum", 0.9),
        event(1.5, "maximum", 1.1),
        event(2.0, "minimum", 0.9),
    )

    result = classify_peak_period(events)

    assert result.candidate_period == pytest.approx(1.0)
    assert result.interval_relative_spread == pytest.approx(0.0)
    assert result.status == "consistent_period_candidate"


def test_invalid_thresholds_are_rejected():
    with pytest.raises(ValueError):
        classify_peak_period((), modulation_fraction=0.0)
    with pytest.raises(ValueError):
        classify_peak_period((), consistency_tolerance=-0.1)
