"""Directed ring control: dimensionless phase transport, not a physical time-energy law."""

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path

MODE_AMPLITUDE_FLOOR = 1e-12


def field(errors, coupling, asymmetry):
    """Return velocity, conservative force, nonreciprocal drive and potential.

    e_dot = F + H; F=-grad(V). H is explicitly imposed, not free energy.
    For this uniform ring F dot H telescopes to zero.
    """
    edges = [math.sin(errors[(i + 1) % len(errors)] - x) for i, x in enumerate(errors)]
    force = [coupling * (s - edges[i - 1]) for i, s in enumerate(edges)]
    imposed = [coupling * asymmetry * (s + edges[i - 1]) for i, s in enumerate(edges)]
    velocity = [f + h for f, h in zip(force, imposed, strict=True)]
    potential = sum(
        coupling * (1 - math.cos(errors[(i + 1) % len(errors)] - x)) for i, x in enumerate(errors)
    )
    return velocity, force, imposed, potential


def fourier(errors):
    return sum(x * cmath.exp(-1j * math.tau * i / len(errors)) for i, x in enumerate(errors))


def run(n=16, coupling=1.0, asymmetry=0.5, amplitude=0.2, dt=0.05, duration=8.0):
    if type(n) is not int or n < 3:
        raise ValueError("integer n >= 3 required")
    if not all(math.isfinite(x) for x in (coupling, asymmetry, amplitude, dt, duration)):
        raise ValueError("finite parameters required")
    if coupling < 0 or abs(asymmetry) > 1 or amplitude <= 0 or dt <= 0 or duration <= 0:
        raise ValueError("K >= 0, |asymmetry| <= 1 and positive amplitude/times required")
    if amplitude <= MODE_AMPLITUDE_FLOOR or amplitude > 0.5:
        raise ValueError("amplitude must exceed the 1e-12 observability floor and be <= 0.5")
    if dt * coupling > 0.1:
        raise ValueError("resolved benchmark requires dt * coupling <= 0.1")
    steps = round(duration / dt)
    if steps < 1 or not math.isclose(steps * dt, duration, rel_tol=1e-12):
        raise ValueError("duration must be an integer number of steps")
    y = [amplitude * math.cos(math.tau * i / n) for i in range(n)]
    initial = y[:]
    v0 = field(y, coupling, asymmetry)[3]
    dissipation = work = 0.0
    angle = 0.0
    previous = fourier(y)
    mode_observable = True
    first_unobservable_time = None
    trace = []
    for step in range(steps + 1):
        if step % max(1, steps // 20) == 0 or step == steps:
            trace.append(
                {
                    "time": step * dt,
                    "potential": field(y, coupling, asymmetry)[3],
                    "mode_angle_unwrapped": angle if mode_observable else None,
                    "mode_amplitude": abs(fourier(y)) * 2 / n,
                }
            )
        if step == steps:
            break
        a = field(y, coupling, asymmetry)
        b = field([p + dt * v / 2 for p, v in zip(y, a[0], strict=True)], coupling, asymmetry)
        c = field([p + dt * v / 2 for p, v in zip(y, b[0], strict=True)], coupling, asymmetry)
        d = field([p + dt * v for p, v in zip(y, c[0], strict=True)], coupling, asymmetry)
        y = [
            p + dt * (u + 2 * v + 2 * w + z) / 6
            for p, u, v, w, z in zip(y, a[0], b[0], c[0], d[0], strict=True)
        ]
        for stage, weight in ((a, 1), (b, 2), (c, 2), (d, 1)):
            dissipation += dt * weight * sum(v * v for v in stage[0]) / 6
            work += dt * weight * sum(h * v for h, v in zip(stage[2], stage[0], strict=True)) / 6
        current = fourier(y)
        if abs(current) * 2 / n <= MODE_AMPLITUDE_FLOOR:
            if mode_observable:
                first_unobservable_time = (step + 1) * dt
            mode_observable = False
        if mode_observable:
            angle += math.remainder(cmath.phase(current) - cmath.phase(previous), math.tau)
        previous = current
    final_v = field(y, coupling, asymmetry)[3]
    return {
        "n": n,
        "coupling": coupling,
        "asymmetry": asymmetry,
        "amplitude": amplitude,
        "dt": dt,
        "duration": duration,
        "initial_errors": initial,
        "final_errors": y,
        "initial_potential": v0,
        "final_potential": final_v,
        "integrated_model_work": work,
        "integrated_model_dissipation": dissipation,
        "balance_residual": final_v - v0 - work + dissipation,
        "measured_mode_angular_rate": angle / duration if mode_observable else None,
        "mode_amplitude_floor": MODE_AMPLITUDE_FLOOR,
        "first_unobservable_time": first_unobservable_time,
        "linearized_mode_angular_rate": 2 * coupling * asymmetry * math.sin(math.tau / n),
        "trace": trace,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [
        run(n=n, coupling=k, asymmetry=a, amplitude=b)
        for n in (8, 16, 24)
        for k in (0.0, 1.0)
        for a in (-0.5, 0.0, 0.5)
        for b in (0.001, 0.2)
    ]
    coarse, fine = run(), run(dt=0.025)
    result = {
        "schema": 1,
        "scope": "Imposed directed phase coupling; dimensionless work only; no geometry/material coupling",
        "source_sha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "case_count": len(cases),
        "cases": cases,
        "convergence": {
            "coarse_balance_residual": coarse["balance_residual"],
            "fine_balance_residual": fine["balance_residual"],
            "max_phase_difference": max(
                abs(a - b)
                for a, b in zip(coarse["final_errors"], fine["final_errors"], strict=True)
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
