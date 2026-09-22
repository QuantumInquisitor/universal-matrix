"""Extended high-resolution Q-ball time series through t=1.5 with turning-time diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_timeseries import (
    HighResolutionTimeSeriesResult,
    TimeSeriesChannelSummary,
    TimeSeriesSample,
    run_high_resolution_timeseries,
)


@dataclass(frozen=True)
class TurningEvent:
    time: float
    kind: str


@dataclass(frozen=True)
class ExtendedChannelDiagnosticsT1p5:
    summary: TimeSeriesChannelSummary
    peak_turning_events: tuple[TurningEvent, ...]
    radius_turning_events: tuple[TurningEvent, ...]
    peak_min_time: float
    peak_max_time: float
    radius_min_time: float
    radius_max_time: float

    @property
    def peak_turning_intervals(self) -> tuple[float, ...]:
        return tuple(
            right.time - left.time
            for left, right in zip(
                self.peak_turning_events,
                self.peak_turning_events[1:],
            )
        )


@dataclass(frozen=True)
class HighResolutionTimeSeriesT1p5:
    result: HighResolutionTimeSeriesResult
    direct: ExtendedChannelDiagnosticsT1p5
    perturbed: ExtendedChannelDiagnosticsT1p5


def _turning_events(
    samples: tuple[TimeSeriesSample, ...],
    *,
    attribute: str,
    atol: float = 1e-12,
) -> tuple[TurningEvent, ...]:
    values = tuple(float(getattr(sample, attribute)) for sample in samples)
    events: list[TurningEvent] = []

    previous_sign: int | None = None
    previous_nonzero_index: int | None = None

    for index, (left, right) in enumerate(zip(values, values[1:]), start=1):
        delta = right - left
        if abs(delta) <= atol:
            continue
        sign = 1 if delta > 0 else -1
        if previous_sign is not None and sign != previous_sign:
            turning_index = previous_nonzero_index if previous_nonzero_index is not None else index - 1
            sample = samples[turning_index]
            kind = "minimum" if previous_sign < 0 and sign > 0 else "maximum"
            events.append(TurningEvent(time=sample.time, kind=kind))
        previous_sign = sign
        previous_nonzero_index = index

    return tuple(events)


def _extended(
    summary: TimeSeriesChannelSummary,
) -> ExtendedChannelDiagnosticsT1p5:
    peak_min = min(summary.samples, key=lambda s: s.peak_ratio)
    peak_max = max(summary.samples, key=lambda s: s.peak_ratio)
    radius_min = min(summary.samples, key=lambda s: s.radius_ratio)
    radius_max = max(summary.samples, key=lambda s: s.radius_ratio)

    return ExtendedChannelDiagnosticsT1p5(
        summary=summary,
        peak_turning_events=_turning_events(
            summary.samples,
            attribute="peak_ratio",
        ),
        radius_turning_events=_turning_events(
            summary.samples,
            attribute="radius_ratio",
        ),
        peak_min_time=peak_min.time,
        peak_max_time=peak_max.time,
        radius_min_time=radius_min.time,
        radius_max_time=radius_max.time,
    )


def run_high_resolution_timeseries_t1p5() -> HighResolutionTimeSeriesT1p5:
    result = run_high_resolution_timeseries(
        steps=1500,
        dt=0.001,
        sample_stride=25,
    )
    return HighResolutionTimeSeriesT1p5(
        result=result,
        direct=_extended(result.direct),
        perturbed=_extended(result.perturbed),
    )


def _format_events(events: tuple[TurningEvent, ...]) -> str:
    if not events:
        return "none"
    return ";".join(
        f"{event.kind}@{event.time:.6f}"
        for event in events
    )


def _format_intervals(intervals: tuple[float, ...]) -> str:
    if not intervals:
        return "none"
    return ";".join(f"{value:.6f}" for value in intervals)


def format_high_resolution_timeseries_t1p5_report(
    run: HighResolutionTimeSeriesT1p5,
) -> str:
    lines = [
        "Q-BALL HIGH-RESOLUTION IN-RUN TIME SERIES T=1.5",
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
                f"{name}_peak_turning_intervals={_format_intervals(channel.peak_turning_intervals)}",
                f"{name}_peak_min_time={channel.peak_min_time:.6f}",
                f"{name}_peak_max_time={channel.peak_max_time:.6f}",
                f"{name}_radius_min_time={channel.radius_min_time:.6f}",
                f"{name}_radius_max_time={channel.radius_max_time:.6f}",
                f"{name}_maximum_peak_deviation={s.maximum_peak_deviation:.10e}",
                f"{name}_maximum_radius_deviation={s.maximum_radius_deviation:.10e}",
                f"{name}_endpoint_peak_deviation={s.endpoint_peak_deviation:.10e}",
                f"{name}_endpoint_radius_deviation={s.endpoint_radius_deviation:.10e}",
                f"{name}_peak_endpoint_to_maximum={s.peak_endpoint_to_maximum_ratio:.10f}",
                f"{name}_radius_endpoint_to_maximum={s.radius_endpoint_to_maximum_ratio:.10f}",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    print(
        format_high_resolution_timeseries_t1p5_report(
            run_high_resolution_timeseries_t1p5()
        )
    )


if __name__ == "__main__":
    main()
