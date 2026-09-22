"""In-run time-series diagnostics for the high-resolution Q-ball persistence test."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .charged_matter_persistence import (
    localized_amplitude_perturbation,
    map_candidate_to_3d,
)
from .localized_matter_persistence import rms_radius
from .qball_highres_persistence_stage1 import refined_above_threshold_record
from .qball_threshold_preserving_grid import TARGET_SHAPE, TARGET_SPACING


@dataclass(frozen=True)
class TimeSeriesSample:
    step: int
    time: float
    energy_drift: float
    charge_drift: float
    peak_ratio: float
    radius_ratio: float


@dataclass(frozen=True)
class TimeSeriesChannelSummary:
    samples: tuple[TimeSeriesSample, ...]
    peak_turning_points: int
    radius_turning_points: int
    peak_monotonic_nonincreasing: bool
    radius_monotonic_nondecreasing: bool
    maximum_peak_deviation: float
    maximum_radius_deviation: float
    endpoint_peak_deviation: float
    endpoint_radius_deviation: float

    @property
    def peak_endpoint_to_maximum_ratio(self) -> float:
        if self.maximum_peak_deviation == 0:
            return 1.0
        return self.endpoint_peak_deviation / self.maximum_peak_deviation

    @property
    def radius_endpoint_to_maximum_ratio(self) -> float:
        if self.maximum_radius_deviation == 0:
            return 1.0
        return self.endpoint_radius_deviation / self.maximum_radius_deviation


@dataclass(frozen=True)
class HighResolutionTimeSeriesResult:
    direct: TimeSeriesChannelSummary
    perturbed: TimeSeriesChannelSummary
    steps: int
    dt: float
    sample_stride: int


def _relative(value: float, reference: float) -> float:
    if reference == 0:
        return 0.0
    return (value - reference) / reference


def _snapshot(
    *,
    state,
    step: int,
    dt: float,
    initial_energy: float,
    initial_charge: float,
    initial_peak: float,
    initial_radius: float,
) -> TimeSeriesSample:
    peak = float(np.max(np.abs(state.phi)))
    radius = rms_radius(state.phi, state.lattice_spacing)
    return TimeSeriesSample(
        step=step,
        time=step * dt,
        energy_drift=_relative(state.energy, initial_energy),
        charge_drift=_relative(state.charge, initial_charge),
        peak_ratio=peak / initial_peak if initial_peak != 0 else math.inf,
        radius_ratio=radius / initial_radius if initial_radius != 0 else math.inf,
    )


def sample_evolution(
    state,
    *,
    steps: int = 500,
    dt: float = 0.001,
    sample_stride: int = 25,
) -> tuple[TimeSeriesSample, ...]:
    if steps < 1:
        raise ValueError("steps must be positive")
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError("dt must be finite and positive")
    if sample_stride < 1:
        raise ValueError("sample_stride must be positive")
    if steps % sample_stride != 0:
        raise ValueError("steps must be divisible by sample_stride")

    initial_energy = state.energy
    initial_charge = state.charge
    initial_peak = float(np.max(np.abs(state.phi)))
    initial_radius = rms_radius(state.phi, state.lattice_spacing)

    out = [
        _snapshot(
            state=state,
            step=0,
            dt=dt,
            initial_energy=initial_energy,
            initial_charge=initial_charge,
            initial_peak=initial_peak,
            initial_radius=initial_radius,
        )
    ]
    for step in range(1, steps + 1):
        state.step(dt)
        if step % sample_stride == 0:
            out.append(
                _snapshot(
                    state=state,
                    step=step,
                    dt=dt,
                    initial_energy=initial_energy,
                    initial_charge=initial_charge,
                    initial_peak=initial_peak,
                    initial_radius=initial_radius,
                )
            )
    return tuple(out)


def _turning_points(values: tuple[float, ...], *, atol: float = 1e-12) -> int:
    diffs = []
    for left, right in zip(values, values[1:]):
        delta = right - left
        if abs(delta) <= atol:
            continue
        diffs.append(1 if delta > 0 else -1)
    return sum(a != b for a, b in zip(diffs, diffs[1:]))


def summarize_channel(
    samples: tuple[TimeSeriesSample, ...],
    *,
    monotonic_tolerance: float = 1e-10,
) -> TimeSeriesChannelSummary:
    if len(samples) < 2:
        raise ValueError("at least two samples are required")

    peak = tuple(sample.peak_ratio for sample in samples)
    radius = tuple(sample.radius_ratio for sample in samples)

    peak_deviations = tuple(abs(value - 1.0) for value in peak)
    radius_deviations = tuple(abs(value - 1.0) for value in radius)

    return TimeSeriesChannelSummary(
        samples=samples,
        peak_turning_points=_turning_points(peak),
        radius_turning_points=_turning_points(radius),
        peak_monotonic_nonincreasing=all(
            right <= left + monotonic_tolerance
            for left, right in zip(peak, peak[1:])
        ),
        radius_monotonic_nondecreasing=all(
            right + monotonic_tolerance >= left
            for left, right in zip(radius, radius[1:])
        ),
        maximum_peak_deviation=max(peak_deviations),
        maximum_radius_deviation=max(radius_deviations),
        endpoint_peak_deviation=peak_deviations[-1],
        endpoint_radius_deviation=radius_deviations[-1],
    )


def run_high_resolution_timeseries(
    *,
    steps: int = 500,
    dt: float = 0.001,
    sample_stride: int = 25,
) -> HighResolutionTimeSeriesResult:
    """Sample direct and perturbed threshold-preserving evolution in-run."""
    record = refined_above_threshold_record()

    direct_state = map_candidate_to_3d(
        record,
        shape=TARGET_SHAPE,
        spacing=TARGET_SPACING,
    )
    perturbed_state = localized_amplitude_perturbation(
        map_candidate_to_3d(
            record,
            shape=TARGET_SHAPE,
            spacing=TARGET_SPACING,
        ),
        fractional_amplitude=0.005,
        width=1.0,
    )

    direct_samples = sample_evolution(
        direct_state,
        steps=steps,
        dt=dt,
        sample_stride=sample_stride,
    )
    perturbed_samples = sample_evolution(
        perturbed_state,
        steps=steps,
        dt=dt,
        sample_stride=sample_stride,
    )
    return HighResolutionTimeSeriesResult(
        direct=summarize_channel(direct_samples),
        perturbed=summarize_channel(perturbed_samples),
        steps=steps,
        dt=dt,
        sample_stride=sample_stride,
    )


def _format_channel(prefix: str, channel: TimeSeriesChannelSummary) -> list[str]:
    lines = [
        f"{prefix}_peak_turning_points={channel.peak_turning_points}",
        f"{prefix}_radius_turning_points={channel.radius_turning_points}",
        f"{prefix}_peak_monotonic_nonincreasing={channel.peak_monotonic_nonincreasing}",
        f"{prefix}_radius_monotonic_nondecreasing={channel.radius_monotonic_nondecreasing}",
        f"{prefix}_maximum_peak_deviation={channel.maximum_peak_deviation:.10e}",
        f"{prefix}_maximum_radius_deviation={channel.maximum_radius_deviation:.10e}",
        f"{prefix}_endpoint_peak_deviation={channel.endpoint_peak_deviation:.10e}",
        f"{prefix}_endpoint_radius_deviation={channel.endpoint_radius_deviation:.10e}",
        f"{prefix}_peak_endpoint_to_maximum={channel.peak_endpoint_to_maximum_ratio:.10f}",
        f"{prefix}_radius_endpoint_to_maximum={channel.radius_endpoint_to_maximum_ratio:.10f}",
    ]
    for sample in channel.samples:
        lines.append(
            f"{prefix}_sample="
            f"step:{sample.step},"
            f"time:{sample.time:.6f},"
            f"energy_drift:{sample.energy_drift:.6e},"
            f"charge_drift:{sample.charge_drift:.6e},"
            f"peak_ratio:{sample.peak_ratio:.10f},"
            f"radius_ratio:{sample.radius_ratio:.10f}"
        )
    return lines


def format_high_resolution_timeseries_report(
    result: HighResolutionTimeSeriesResult,
) -> str:
    lines = [
        "Q-BALL HIGH-RESOLUTION IN-RUN TIME SERIES",
        f"shape={TARGET_SHAPE}",
        f"spacing={TARGET_SPACING:.10f}",
        f"steps={result.steps}",
        f"dt={result.dt:.10f}",
        f"sample_stride={result.sample_stride}",
        f"sample_count={len(result.direct.samples)}",
    ]
    lines.extend(_format_channel("direct", result.direct))
    lines.extend(_format_channel("perturbed", result.perturbed))
    return "\n".join(lines)


def main() -> None:
    print(format_high_resolution_timeseries_report(run_high_resolution_timeseries()))


if __name__ == "__main__":
    main()
