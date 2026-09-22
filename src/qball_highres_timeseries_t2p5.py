"""Extended high-resolution Q-ball time series through t=2.5.

Adds turning-event values and same-kind interval diagnostics so closely spaced
peak wiggles can be distinguished from a repeatable dominant oscillation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_timeseries import (
    HighResolutionTimeSeriesResult,
    TimeSeriesChannelSummary,
    TimeSeriesSample,
    run_high_resolution_timeseries,
)


@dataclass(frozen=True)
class ValuedTurningEvent:
    time: float
    kind: str
    value: float


@dataclass(frozen=True)
class ExtendedChannelDiagnosticsT2p5:
    summary: TimeSeriesChannelSummary
    peak_turning_events: tuple[ValuedTurningEvent, ...]
    radius_turning_events: tuple[ValuedTurningEvent, ...]
    peak_min_to_min_intervals: tuple[float, ...]
    peak_max_to_max_intervals: tuple[float, ...]
    adjacent_peak_swings: tuple[float, ...]
    peak_min_time: float
    peak_max_time: float
    radius_min_time: float
    radius_max_time: float


@dataclass(frozen=True)
class HighResolutionTimeSeriesT2p5:
    result: HighResolutionTimeSeriesResult
    direct: ExtendedChannelDiagnosticsT2p5
    perturbed: ExtendedChannelDiagnosticsT2p5


def _valued_turning_events(
    samples: tuple[TimeSeriesSample, ...],
    *,
    attribute: str,
    atol: float = 1e-12,
) -> tuple[ValuedTurningEvent, ...]:
    values = tuple(float(getattr(sample, attribute)) for sample in samples)
    events: list[ValuedTurningEvent] = []

    previous_sign: int | None = None
    previous_nonzero_index: int | None = None

    for index, (left, right) in enumerate(zip(values, values[1:]), start=1):
        delta = right - left
        if abs(delta) <= atol:
            continue
        sign = 1 if delta > 0 else -1
        if previous_sign is not None and sign != previous_sign:
            turning_index = (
                previous_nonzero_index
                if previous_nonzero_index is not None
                else index - 1
            )
            sample = samples[turning_index]
            kind = "minimum" if previous_sign < 0 and sign > 0 else "maximum"
            events.append(
                ValuedTurningEvent(
                    time=sample.time,
                    kind=kind,
                    value=float(getattr(sample, attribute)),
                )
            )
        previous_sign = sign
        previous_nonzero_index = index

    return tuple(events)


def _same_kind_intervals(
    events: tuple[ValuedTurningEvent, ...],
    *,
    kind: str,
) -> tuple[float, ...]:
    times = tuple(event.time for event in events if event.kind == kind)
    return tuple(right - left for left, right in zip(times, times[1:]))


def _adjacent_swings(
    events: tuple[ValuedTurningEvent, ...],
) -> tuple[float, ...]:
    return tuple(
        abs(right.value - left.value)
        for left, right in zip(events, events[1:])
    )


def _extended(
    summary: TimeSeriesChannelSummary,
) -> ExtendedChannelDiagnosticsT2p5:
    peak_events = _valued_turning_events(
        summary.samples,
        attribute="peak_ratio",
    )
    radius_events = _valued_turning_events(
        summary.samples,
        attribute="radius_ratio",
    )

    peak_min = min(summary.samples, key=lambda s: s.peak_ratio)
    peak_max = max(summary.samples, key=lambda s: s.peak_ratio)
    radius_min = min(summary.samples, key=lambda s: s.radius_ratio)
    radius_max = max(summary.samples, key=lambda s: s.radius_ratio)

    return ExtendedChannelDiagnosticsT2p5(
        summary=summary,
        peak_turning_events=peak_events,
        radius_turning_events=radius_events,
        peak_min_to_min_intervals=_same_kind_intervals(
            peak_events,
            kind="minimum",
        ),
        peak_max_to_max_intervals=_same_kind_intervals(
            peak_events,
            kind="maximum",
        ),
        adjacent_peak_swings=_adjacent_swings(peak_events),
        peak_min_time=peak_min.time,
        peak_max_time=peak_max.time,
        radius_min_time=radius_min.time,
        radius_max_time=radius_max.time,
    )


def run_high_resolution_timeseries_t2p5() -> HighResolutionTimeSeriesT2p5:
    result = run_high_resolution_timeseries(
        steps=2500,
        dt=0.001,
        sample_stride=25,
    )
    return HighResolutionTimeSeriesT2p5(
        result=result,
        direct=_extended(result.direct),
        perturbed=_extended(result.perturbed),
    )


def _format_events(events: tuple[ValuedTurningEvent, ...]) -> str:
    if not events:
        return "none"
    return ";".join(
        f"{event.kind}@{event.time:.6f}:value={event.value:.10f}"
        for event in events
    )


def _format_values(values: tuple[float, ...]) -> str:
    if not values:
        return "none"
    return ";".join(f"{value:.10f}" for value in values)


def format_high_resolution_timeseries_t2p5_report(
    run: HighResolutionTimeSeriesT2p5,
) -> str:
    lines = [
        "Q-BALL HIGH-RESOLUTION IN-RUN TIME SERIES T=2.5",
        f"steps={run.result.steps}",
        f"dt={run.result.dt:.10f}",
        f"sample_stride={run.result.sample_stride}",
        f"sample_count={len(run.result.direct.samples)}",
    ]

    for name, channel in (
        ("direct", run.direct),
        ("perturbed", run.perturbed),
    ):
        s = channel.summary
        lines.extend(
            [
                f"{name}_peak_turning_points={s.peak_turning_points}",
                f"{name}_radius_turning_points={s.radius_turning_points}",
                f"{name}_peak_turning_events={_format_events(channel.peak_turning_events)}",
                f"{name}_radius_turning_events={_format_events(channel.radius_turning_events)}",
                f"{name}_peak_min_to_min_intervals={_format_values(channel.peak_min_to_min_intervals)}",
                f"{name}_peak_max_to_max_intervals={_format_values(channel.peak_max_to_max_intervals)}",
                f"{name}_adjacent_peak_swings={_format_values(channel.adjacent_peak_swings)}",
                f"{name}_peak_min_time={channel.peak_min_time:.6f}",
                f"{name}_peak_max_time={channel.peak_max_time:.6f}",
                f"{name}_radius_min_time={channel.radius_min_time:.6f}",
                f"{name}_radius_max_time={channel.radius_max_time:.6f}",
                f"{name}_maximum_peak_deviation={s.maximum_peak_deviation:.10e}",
                f"{name}_maximum_radius_deviation={s.maximum_radius_deviation:.10e}",
                f"{name}_endpoint_peak_deviation={s.endpoint_peak_deviation:.10e}",
                f"{name}_endpoint_radius_deviation={s.endpoint_radius_deviation:.10e}",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    print(
        format_high_resolution_timeseries_t2p5_report(
            run_high_resolution_timeseries_t2p5()
        )
    )


if __name__ == "__main__":
    main()
