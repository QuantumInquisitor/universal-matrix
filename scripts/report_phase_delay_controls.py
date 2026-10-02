"""Ordinary delayed phase tracker controls, in dimensionless rotating coordinates."""

import argparse
import hashlib
import json
import math
import random
from pathlib import Path


def run(
    *,
    delay=0.5,
    coupling=2.0,
    noise=0.03,
    seed=7,
    dt=0.01,
    duration=12.0,
    kick_time=2.0,
    noise_hold=0.1,
):
    """RK4 tracker with exact-grid held inputs and paired intervention control.

    q' = K sin(s(t-delay) + eta(t-delay) - q). Source s jumps by a
    seeded random signed amount unknown to the receiver before arrival.
    The no-kick trajectory uses exactly the same measurement noise.
    """
    values = (delay, coupling, noise, dt, duration, kick_time, noise_hold)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("finite parameters required")
    if min(delay, coupling, noise) < 0 or min(dt, duration, kick_time, noise_hold) <= 0:
        raise ValueError("nonnegative delay/coupling/noise; positive times required")
    if kick_time + delay >= duration:
        raise ValueError("intervention must arrive before end")
    counts = [round(x / dt) for x in (delay, duration, kick_time, noise_hold)]
    if any(
        not math.isclose(n * dt, x, rel_tol=1e-12, abs_tol=1e-14)
        for n, x in zip(counts, (delay, duration, kick_time, noise_hold), strict=True)
    ):
        raise ValueError("all event and hold times must align to dt")
    lag, steps, kick_step, hold_steps = counts
    if hold_steps < 1:
        raise ValueError("noise hold must span at least one step")
    rng = random.Random(seed)
    amplitude = rng.choice((-1, 1)) * rng.uniform(0.5, 0.8)
    held_noise = [rng.uniform(-noise, noise) for _ in range(steps // hold_steps + 1)]
    q = reference = effort = 0.0
    first = None
    trace = []
    residuals = []
    output_noise = []
    baseline_noise = []
    paired_prearrival = 0.0

    def advance(value, target):
        def f(x):
            return coupling * math.sin(target - x)

        a = f(value)
        b = f(value + dt * a / 2)
        c = f(value + dt * b / 2)
        d = f(value + dt * c)
        return value + dt * (a + 2 * b + 2 * c + d) / 6, dt * (
            a * a + 2 * b * b + 2 * c * c + d * d
        ) / 6

    for step in range(steps + 1):
        t = step * dt
        source_index = step - lag
        signal = amplitude if source_index >= kick_step else 0.0
        eta = held_noise[source_index // hold_steps] if source_index >= 0 else 0.0
        difference = abs(q - reference)
        if first is None and difference > 1e-6:
            first = t
        if step <= kick_step + lag:
            paired_prearrival = max(paired_prearrival, difference)
        residuals.append(abs(q - signal))
        if t >= duration - 2.0:
            output_noise.append(reference * reference)
            baseline_noise.append(eta * eta)
        if step % max(1, steps // 120) == 0 or step == steps:
            trace.append(
                {
                    "time": t,
                    "source_target_delayed": signal,
                    "tracker": q,
                    "no_kick_tracker": reference,
                    "ordinary_transport_readout": signal + eta,
                }
            )
        if step == steps:
            break
        q, used = advance(q, signal + eta)
        reference, _ = advance(reference, eta)
        effort += used
    # Recovery means within 0.05 rad through the complete remaining record,
    # with at least one dimensionless time unit of confirmed residence.
    last_outside = max(
        (i for i in range(kick_step + lag, steps + 1) if residuals[i] > 0.05),
        default=kick_step + lag - 1,
    )
    settled_step = last_outside + 1
    recovery = (
        settled_step * dt - (kick_time + delay)
        if settled_step <= steps - math.ceil(1 / dt)
        else None
    )
    return {
        "parameters": {
            "delay": delay,
            "coupling": coupling,
            "noise": noise,
            "seed": seed,
            "dt": dt,
            "duration": duration,
            "kick_time": kick_time,
            "noise_hold": noise_hold,
        },
        "injected_amplitude": amplitude,
        "earliest_allowed_arrival": kick_time + delay,
        "first_detected_paired_difference": first,
        "maximum_prearrival_paired_difference": paired_prearrival,
        "recovery_after_arrival": recovery,
        "final_tracking_error": residuals[-1],
        "final_phase": q,
        "integrated_squared_phase_drive": effort,
        "no_kick_output_rms_last_two_units": math.sqrt(sum(output_noise) / len(output_noise)),
        "ordinary_transport_noise_rms_last_two_units": math.sqrt(
            sum(baseline_noise) / len(baseline_noise)
        ),
        "trace": trace,
    }


def report():
    cases = [
        run(delay=d, coupling=k, noise=a, seed=s)
        for d in (0.0, 0.5, 1.0)
        for k in (0.0, 0.5, 2.0)
        for a in (0.0, 0.03)
        for s in (7, 19, 41)
    ]
    coarse, fine, finest = (run(dt=dt) for dt in (0.02, 0.01, 0.005))
    return {
        "schema": 1,
        "scope": "ordinary classical phase tracker; prescribed dimensionless source; no time crystal or physical energy claim",
        "source_sha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "case_count": len(cases),
        "cases": cases,
        "convergence": {
            "step_sizes": [0.02, 0.01, 0.005],
            "coarse_fine_final_difference": abs(coarse["final_phase"] - fine["final_phase"]),
            "fine_finest_final_difference": abs(fine["final_phase"] - finest["final_phase"]),
            "arrival_detection_times": [
                r["first_detected_paired_difference"] for r in (coarse, fine, finest)
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
