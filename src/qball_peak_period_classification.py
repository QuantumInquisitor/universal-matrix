"""Prominence-based classification of sampled Q-ball peak reversals.

The classifier removes only adjacent maximum/minimum pairs whose connecting
swing is small relative to the largest observed swing.  It then compares the
remaining same-kind intervals without forcing them into a single period.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean

from .qball_highres_timeseries_t2p5 import ValuedTurningEvent


@dataclass(frozen=True)
class PeakPeriodClassification:
    retained_events: tuple[ValuedTurningEvent, ...]
    removed_modulation_pairs: tuple[tuple[ValuedTurningEvent, ValuedTurningEvent], ...]
    minimum_intervals: tuple[float, ...]
    maximum_intervals: tuple[float, ...]
    candidate_period: float | None
    interval_relative_spread: float | None
    status: str


def _same_kind_intervals(
    events: tuple[ValuedTurningEvent, ...], kind: str
) -> tuple[float, ...]:
    times = tuple(event.time for event in events if event.kind == kind)
    return tuple(
        right - left for left, right in zip(times, times[1:], strict=False)
    )


def classify_peak_period(
    events: tuple[ValuedTurningEvent, ...],
    *,
    modulation_fraction: float = 0.01,
    consistency_tolerance: float = 0.15,
) -> PeakPeriodClassification:
    """Separate tiny reversals and assess whether one repeatable period exists."""
    if not 0.0 < modulation_fraction < 1.0:
        raise ValueError("modulation_fraction must lie between zero and one")
    if consistency_tolerance < 0.0:
        raise ValueError("consistency_tolerance must be non-negative")

    retained = list(events)
    removed: list[tuple[ValuedTurningEvent, ValuedTurningEvent]] = []
    if len(retained) >= 2:
        largest_swing = max(
            abs(right.value - left.value)
            for left, right in zip(retained, retained[1:], strict=False)
        )
        threshold = modulation_fraction * largest_swing
        index = 0
        while index < len(retained) - 1:
            left, right = retained[index], retained[index + 1]
            if abs(right.value - left.value) < threshold:
                removed.append((left, right))
                del retained[index : index + 2]
                index = max(0, index - 1)
            else:
                index += 1

    retained_tuple = tuple(retained)
    minimum_intervals = _same_kind_intervals(retained_tuple, "minimum")
    maximum_intervals = _same_kind_intervals(retained_tuple, "maximum")
    intervals = minimum_intervals + maximum_intervals

    interval_mean = fmean(intervals) if intervals else None
    spread = None
    if interval_mean is not None and len(intervals) >= 2:
        spread = (max(intervals) - min(intervals)) / interval_mean

    if not intervals:
        status = "insufficient_repeated_extrema"
        candidate = None
    elif len(intervals) == 1:
        status = "single_period_candidate"
        candidate = interval_mean
    elif spread is not None and spread <= consistency_tolerance:
        status = "consistent_period_candidate"
        candidate = interval_mean
    else:
        status = "inconsistent_period_candidates"
        candidate = None

    return PeakPeriodClassification(
        retained_events=retained_tuple,
        removed_modulation_pairs=tuple(removed),
        minimum_intervals=minimum_intervals,
        maximum_intervals=maximum_intervals,
        candidate_period=candidate,
        interval_relative_spread=spread,
        status=status,
    )
