"""Dimensionless reciprocal ring benchmark; no physical energy/time claim."""

import argparse
import cmath
import hashlib
import json
import math
import random
from pathlib import Path


def field(phases, targets, coupling):
    """Negative gradient of V=sum K*(1-cos(relative phase error))."""
    forces = [0.0] * len(phases)
    potential = 0.0
    for i in range(len(phases)):
        j = (i + 1) % len(phases)
        delta = phases[j] - phases[i] + targets[i] - targets[j]
        drive = coupling * math.sin(delta)
        forces[i] += drive
        forces[j] -= drive
        potential += coupling * (1.0 - math.cos(delta))
    return forces, potential


def order(phases):
    return abs(sum(cmath.exp(1j * p) for p in phases) / len(phases))


def run(n=16, mode=1, omega=1.0, coupling=1.0, seed=7, dt=0.025, duration=40.0, mirror=False):
    """RK4 in the rotating frame; integrate dissipation at the same stages.

    omega is prescribed uniform phase drift, not an energy reservoir.
    Targets are encoded in edge offsets, not spontaneously selected.
    """
    if type(n) is not int or n < 3 or type(mode) is not int:
        raise ValueError("n >= 3 and integer mode required")
    if not all(math.isfinite(x) for x in (omega, coupling, dt, duration)):
        raise ValueError("finite parameters required")
    if coupling < 0 or dt <= 0 or duration <= 0:
        raise ValueError("nonnegative coupling and positive times required")
    steps = round(duration / dt)
    if steps < 1 or not math.isclose(steps * dt, duration, rel_tol=1e-12):
        raise ValueError("duration must be an integer number of steps")
    sign = -1 if mirror else 1
    rng = random.Random(seed)
    targets = [sign * math.tau * mode * i / n for i in range(n)]
    y = [a + sign * rng.uniform(-0.45, 0.45) for a in targets]
    initial = y[:]
    v0 = field(y, targets, coupling)[1]
    dissipation = 0.0
    trace = []
    for step in range(steps + 1):
        if step % max(1, steps // 20) == 0 or step == steps:
            trace.append(
                {
                    "time": step * dt,
                    "potential": field(y, targets, coupling)[1],
                    "common_order": order(y),
                    "target_alignment": order([p - a for p, a in zip(y, targets, strict=False)]),
                }
            )
        if step == steps:
            break
        k1 = field(y, targets, coupling)[0]
        k2 = field([p + dt * f / 2 for p, f in zip(y, k1, strict=False)], targets, coupling)[0]
        k3 = field([p + dt * f / 2 for p, f in zip(y, k2, strict=False)], targets, coupling)[0]
        k4 = field([p + dt * f for p, f in zip(y, k3, strict=False)], targets, coupling)[0]
        y = [
            p + dt * (a + 2 * b + 2 * c + d) / 6
            for p, a, b, c, d in zip(y, k1, k2, k3, k4, strict=False)
        ]
        dissipation += (
            dt * sum(sum(f * f for f in k) * w for k, w in ((k1, 1), (k2, 2), (k3, 2), (k4, 1))) / 6
        )
    final_v = field(y, targets, coupling)[1]
    return {
        "n": n,
        "mode": mode,
        "omega": omega,
        "coupling": coupling,
        "seed": seed,
        "dt": dt,
        "duration": duration,
        "mirror": mirror,
        "initial_rotating_phases": initial,
        "final_rotating_phases": y,
        "final_lab_phases": [p + omega * duration for p in y],
        "initial_potential": v0,
        "final_potential": final_v,
        "integrated_model_dissipation": dissipation,
        "balance_residual": final_v - v0 + dissipation,
        "trace": trace,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [
        run(n=n, seed=s, mode=m, omega=w, coupling=k)
        for n in (8, 16, 24)
        for s in (7, 19, 41)
        for m in (0, 1)
        for w in (-1.0, 0.0, 1.0)
        for k in (0.0, 1.0)
    ]
    coarse = run()
    fine = run(dt=0.0125)
    mirrored = run(mode=1, omega=-1.0, mirror=True)
    result = {
        "schema": 1,
        "scope": "dimensionless reciprocal ring; prescribed drift; no physical energy units",
        "source_sha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "case_count": len(cases),
        "cases": cases,
        "convergence": {
            "coarse_balance": coarse["balance_residual"],
            "fine_balance": fine["balance_residual"],
            "max_phase_difference": max(
                abs(a - b)
                for a, b in zip(
                    coarse["final_rotating_phases"], fine["final_rotating_phases"], strict=False
                )
            ),
        },
        "mirror_max_phase_error": max(
            abs(a + b)
            for a, b in zip(coarse["final_lab_phases"], mirrored["final_lab_phases"], strict=False)
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
