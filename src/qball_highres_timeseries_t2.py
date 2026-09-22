"""Extended high-resolution Q-ball time series through t=2.0 with half-cycle diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

from .qball_highres_timeseries import HighResolutionTimeSeriesResult, run_high_resolution_timeseries
from .qball_highres_timeseries_t1p5 import (
    ExtendedChannelDiagnosticsT1p5,
    _extended,
    _format_events,
    _format_intervals,
)


@dataclass(frozen=True)
class HighResolutionTimeSeriesT2:
    result: HighResolutionTimeSeriesResult
    direct: ExtendedChannelDiagnosticsT1p5
    perturbed: ExtendedChannelDiagnosticsT1p5

    @property
    def perturbed_peak_half_cycle_candidate(self) -> float | None:
        events = self.perturbed.peak_turning_events
        if len(events) < 2:
            return None
        first, second = events[0], events[1]
        if first.kind == second.kind:
            return None
        return second.time - first.time


def run_high_resolution_timeseries_t2() -> HighResolutionTimeSeriesT2:
    result = run_high_resolution_timeseries(
        steps=2000,
        dt=0.001,
        sample_stride=25,
    )
    return HighResolutionTimeSeriesT2(
        result=result,
        direct=_extended(result.direct),
        perturbed=_extended(result.perturbed),
    )


def _format_optional(value: float | None) -> str:
    return "none" if value is None else f"{value:.6f}"


def format_high_resolution_timeseries_t2_report(
    run: HighResolutionTimeSeriesT2,
) -> str:
    lines = [
        "Q-BALL HIGH-RESOLUTION IN-RUN TIME SERIES T=2.0",
        f"steps={run.result.steps}",
        f"dt={run.result.dt:.10f}",
        f"sample_stride={run.result.sample_stride}",
        f"sample_count={len(run.result.direct.samples)}",
        f"perturbed_peak_half_cycle_candidate={_format_optional(run.perturbed_peak_half_cycle_candidate)}",
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
        format_high_resolution_timeseries_t2_report(
            run_high_resolution_timeseries_t2()
        )
    )


if __name__ == "__main__":
    main()
