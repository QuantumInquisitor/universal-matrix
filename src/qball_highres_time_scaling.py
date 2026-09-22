"""Time-scaling diagnostics for completed high-resolution Q-ball persistence stages.

The three observations are frozen evidence from the merged Stage-1, Stage-2,
and Stage-3 CI reports. The analysis intentionally separates conservation drift
from structural deviation and treats all power-law extrapolations as local
diagnostics rather than asymptotic laws.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PersistenceScalingObservation:
    time: float
    direct_energy_drift: float
    perturbed_energy_drift: float
    direct_peak_deviation: float
    perturbed_peak_deviation: float
    direct_radius_deviation: float
    perturbed_radius_deviation: float


@dataclass(frozen=True)
class ScalingChannel:
    name: str
    global_exponent: float
    early_exponent: float
    late_exponent: float
    latest_value: float
    projected_value_at_0p5: float


STAGE_OBSERVATIONS: tuple[PersistenceScalingObservation, ...] = (
    PersistenceScalingObservation(
        time=0.025,
        direct_energy_drift=7.880076e-12,
        perturbed_energy_drift=7.915454e-12,
        direct_peak_deviation=1.0 - 0.9999909487,
        perturbed_peak_deviation=1.0 - 0.9999809562,
        direct_radius_deviation=1.0000002078 - 1.0,
        perturbed_radius_deviation=1.0000005845 - 1.0,
    ),
    PersistenceScalingObservation(
        time=0.1,
        direct_energy_drift=5.884253e-11,
        perturbed_energy_drift=5.944744e-11,
        direct_peak_deviation=1.0 - 0.9998792689,
        perturbed_peak_deviation=1.0 - 0.9997211464,
        direct_radius_deviation=1.0000033970 - 1.0,
        perturbed_radius_deviation=1.0000093885 - 1.0,
    ),
    PersistenceScalingObservation(
        time=0.25,
        direct_energy_drift=6.124757e-11,
        perturbed_energy_drift=6.461953e-11,
        direct_peak_deviation=1.0 - 0.9997323586,
        perturbed_peak_deviation=1.0 - 0.9988027891,
        direct_radius_deviation=1.0000230580 - 1.0,
        perturbed_radius_deviation=1.0000593241 - 1.0,
    ),
)


def local_power_exponent(t0: float, y0: float, t1: float, y1: float) -> float:
    if t0 <= 0 or t1 <= t0:
        raise ValueError("times must satisfy 0 < t0 < t1")
    if y0 <= 0 or y1 <= 0:
        raise ValueError("values must be positive")
    return math.log(y1 / y0) / math.log(t1 / t0)


def _channel(name: str, values: tuple[float, float, float]) -> ScalingChannel:
    times = tuple(obs.time for obs in STAGE_OBSERVATIONS)
    early = local_power_exponent(times[0], values[0], times[1], values[1])
    late = local_power_exponent(times[1], values[1], times[2], values[2])
    global_exp = local_power_exponent(times[0], values[0], times[2], values[2])
    projected = values[2] * (0.5 / times[2]) ** late
    return ScalingChannel(
        name=name,
        global_exponent=global_exp,
        early_exponent=early,
        late_exponent=late,
        latest_value=values[2],
        projected_value_at_0p5=projected,
    )


def analyze_stage_scaling() -> tuple[ScalingChannel, ...]:
    obs = STAGE_OBSERVATIONS
    return (
        _channel(
            "direct_energy_drift",
            tuple(item.direct_energy_drift for item in obs),
        ),
        _channel(
            "perturbed_energy_drift",
            tuple(item.perturbed_energy_drift for item in obs),
        ),
        _channel(
            "direct_peak_deviation",
            tuple(item.direct_peak_deviation for item in obs),
        ),
        _channel(
            "perturbed_peak_deviation",
            tuple(item.perturbed_peak_deviation for item in obs),
        ),
        _channel(
            "direct_radius_deviation",
            tuple(item.direct_radius_deviation for item in obs),
        ),
        _channel(
            "perturbed_radius_deviation",
            tuple(item.perturbed_radius_deviation for item in obs),
        ),
    )


def recommended_stage4_time(
    *,
    structural_limit: float = 0.01,
) -> float:
    """Return the next cautious duration candidate from the late-time local trend.

    The recommendation is intentionally conservative: only t=0.5 is considered,
    and only when all projected peak/radius deviations remain below the supplied
    structural limit.
    """
    if structural_limit <= 0:
        raise ValueError("structural_limit must be positive")
    structural = [
        channel
        for channel in analyze_stage_scaling()
        if "peak_deviation" in channel.name or "radius_deviation" in channel.name
    ]
    if all(
        channel.projected_value_at_0p5 < structural_limit
        for channel in structural
    ):
        return 0.5
    return 0.25


def format_scaling_report() -> str:
    lines = [
        "Q-BALL HIGH-RESOLUTION TIME-SCALING DIAGNOSTIC",
        "observed_times=(0.025, 0.1, 0.25)",
    ]
    for channel in analyze_stage_scaling():
        lines.extend(
            [
                f"{channel.name}_early_exponent={channel.early_exponent:.10f}",
                f"{channel.name}_late_exponent={channel.late_exponent:.10f}",
                f"{channel.name}_global_exponent={channel.global_exponent:.10f}",
                f"{channel.name}_latest_value={channel.latest_value:.10e}",
                f"{channel.name}_projected_at_0p5={channel.projected_value_at_0p5:.10e}",
            ]
        )
    lines.append(
        f"recommended_stage4_time={recommended_stage4_time():.10f}"
    )
    lines.append(
        "interpretation=local exponents are diagnostics, not asymptotic laws"
    )
    return "\n".join(lines)


def main() -> None:
    print(format_scaling_report())


if __name__ == "__main__":
    main()
