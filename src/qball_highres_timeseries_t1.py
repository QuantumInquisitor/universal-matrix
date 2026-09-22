"""Extended high-resolution Q-ball time series through t=1.0."""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_timeseries import (
    HighResolutionTimeSeriesResult,
    TimeSeriesChannelSummary,
    run_high_resolution_timeseries,
)


@dataclass(frozen=True)
class ExtendedChannelDiagnostics:
    summary: TimeSeriesChannelSummary
    peak_min_time: float
    peak_max_time: float
    radius_min_time: float
    radius_max_time: float


@dataclass(frozen=True)
class HighResolutionTimeSeriesT1:
    result: HighResolutionTimeSeriesResult
    direct: ExtendedChannelDiagnostics
    perturbed: ExtendedChannelDiagnostics


def _extended(summary: TimeSeriesChannelSummary) -> ExtendedChannelDiagnostics:
    peak_min = min(summary.samples, key=lambda s: s.peak_ratio)
    peak_max = max(summary.samples, key=lambda s: s.peak_ratio)
    radius_min = min(summary.samples, key=lambda s: s.radius_ratio)
    radius_max = max(summary.samples, key=lambda s: s.radius_ratio)
    return ExtendedChannelDiagnostics(
        summary=summary,
        peak_min_time=peak_min.time,
        peak_max_time=peak_max.time,
        radius_min_time=radius_min.time,
        radius_max_time=radius_max.time,
    )


def run_high_resolution_timeseries_t1() -> HighResolutionTimeSeriesT1:
    result = run_high_resolution_timeseries(
        steps=1000,
        dt=0.001,
        sample_stride=25,
    )
    return HighResolutionTimeSeriesT1(
        result=result,
        direct=_extended(result.direct),
        perturbed=_extended(result.perturbed),
    )


def format_high_resolution_timeseries_t1_report(
    run: HighResolutionTimeSeriesT1,
) -> str:
    lines = [
        "Q-BALL HIGH-RESOLUTION IN-RUN TIME SERIES T=1.0",
        f"steps={run.result.steps}",
        f"dt={run.result.dt:.10f}",
        f"sample_stride={run.result.sample_stride}",
        f"sample_count={len(run.result.direct.samples)}",
    ]
    for name, channel in (("direct", run.direct), ("perturbed", run.perturbed)):
        s = channel.summary
        lines.extend(
            [
                f"{name}_peak_turning_points={s.peak_turning_points}",
                f"{name}_radius_turning_points={s.radius_turning_points}",
                f"{name}_peak_monotonic_nonincreasing={s.peak_monotonic_nonincreasing}",
                f"{name}_radius_monotonic_nondecreasing={s.radius_monotonic_nondecreasing}",
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
        format_high_resolution_timeseries_t1_report(
            run_high_resolution_timeseries_t1()
        )
    )


if __name__ == "__main__":
    main()
