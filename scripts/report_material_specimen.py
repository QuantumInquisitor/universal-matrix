"""Synthetic connected two-mass SI specimen; no assembly material calibration."""

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Specimen:
    """Two equal masses, each anchored, joined by a spring and dashpot."""

    mass_kg: float = 1.0
    anchor_stiffness_n_per_m: float = 4.0
    link_stiffness_n_per_m: float = 2.0
    anchor_damping_n_s_per_m: float = 0.1
    link_damping_n_s_per_m: float = 0.2
    drive_amplitude_n: float = 0.2
    drive_omega_rad_per_s: float = 1.5

    def __post_init__(self):
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if self.mass_kg == 0:
            raise ValueError("mass must be positive")

    def energies(self, state):
        x0, x1, v0, v1 = state[:4]
        kinetic = self.mass_kg * (v0 * v0 + v1 * v1) / 2
        potential = (
            self.anchor_stiffness_n_per_m * (x0 * x0 + x1 * x1)
            + self.link_stiffness_n_per_m * (x1 - x0) ** 2
        ) / 2
        return kinetic, potential

    def derivative(self, t, state):
        x0, x1, v0, v1 = state[:4]
        force = self.drive_amplitude_n * math.sin(self.drive_omega_rad_per_s * t)
        link = self.link_stiffness_n_per_m * (x1 - x0) + self.link_damping_n_s_per_m * (v1 - v0)
        a0 = (
            force + link - self.anchor_stiffness_n_per_m * x0 - self.anchor_damping_n_s_per_m * v0
        ) / self.mass_kg
        a1 = (
            -link - self.anchor_stiffness_n_per_m * x1 - self.anchor_damping_n_s_per_m * v1
        ) / self.mass_kg
        loss = (
            self.anchor_damping_n_s_per_m * (v0 * v0 + v1 * v1)
            + self.link_damping_n_s_per_m * (v1 - v0) ** 2
        )
        return (v0, v1, a0, a1, force * v0, loss)


def run(model, dt=0.02, duration=8.0, initial=(0.1, 0.0, 0.0, 0.0)):
    """RK4 with work/loss integrated independently of endpoint energy."""
    if (
        isinstance(dt, bool)
        or isinstance(duration, bool)
        or not math.isfinite(dt)
        or not math.isfinite(duration)
        or dt <= 0
        or duration <= 0
    ):
        raise ValueError("dt and duration must be finite and positive")
    if len(initial) != 4 or any(isinstance(v, bool) or not math.isfinite(v) for v in initial):
        raise ValueError("initial must contain four finite displacement/velocity values")
    steps = round(duration / dt)
    if steps < 1 or steps > 1_000_000 or not math.isclose(steps * dt, duration, rel_tol=1e-12):
        raise ValueError("duration must contain an integer number of at most one million steps")
    y = tuple(initial) + (0.0, 0.0)
    energy0 = sum(model.energies(y))
    max_residual = 0.0
    traces = []
    for step in range(steps + 1):
        kinetic, potential = model.energies(y)
        residual = kinetic + potential - energy0 - y[4] + y[5]
        max_residual = max(max_residual, abs(residual))
        if step % max(1, steps // 20) == 0 or step == steps:
            traces.append(
                {
                    "time_s": step * dt,
                    "state_m_m_mps_mps": list(y[:4]),
                    "kinetic_j": kinetic,
                    "potential_j": potential,
                    "external_work_j": y[4],
                    "dissipated_j": y[5],
                    "balance_residual_j": residual,
                }
            )
        if step == steps:
            break
        t = step * dt
        k1 = model.derivative(t, y)
        k2 = model.derivative(t + dt / 2, tuple(a + dt * b / 2 for a, b in zip(y, k1, strict=True)))
        k3 = model.derivative(t + dt / 2, tuple(a + dt * b / 2 for a, b in zip(y, k2, strict=True)))
        k4 = model.derivative(t + dt, tuple(a + dt * b for a, b in zip(y, k3, strict=True)))
        y = tuple(
            a + dt * (b + 2 * c + 2 * d + e) / 6
            for a, b, c, d, e in zip(y, k1, k2, k3, k4, strict=True)
        )
        if not all(math.isfinite(v) for v in y):
            raise ValueError("nonfinite integration result")
    return {
        "dt_s": dt,
        "duration_s": duration,
        "initial_state": list(initial),
        "parameters": asdict(model),
        "initial_energy_j": energy0,
        "final_state": list(y[:4]),
        "final_energy_j": kinetic + potential,
        "external_work_j": y[4],
        "dissipated_j": y[5],
        "balance_residual_j": residual,
        "max_abs_balance_residual_j": max_residual,
        "trace": traces,
    }


def report():
    cases = {}
    for name, model in {
        "driven_damped": Specimen(),
        "drive_off": Specimen(drive_amplitude_n=0),
        "conservative": Specimen(
            drive_amplitude_n=0, anchor_damping_n_s_per_m=0, link_damping_n_s_per_m=0
        ),
        "disconnected": Specimen(
            drive_amplitude_n=0, link_stiffness_n_per_m=0, link_damping_n_s_per_m=0
        ),
    }.items():
        cases[name] = [run(model, dt=dt) for dt in (0.04, 0.02, 0.01)]
    coarse, medium, fine = cases["driven_damped"]
    refinement = {}
    for name, section in (("displacement_m", slice(0, 2)), ("velocity_m_per_s", slice(2, 4))):
        differences = [
            math.dist(a["final_state"][section], b["final_state"][section])
            for a, b in ((coarse, medium), (medium, fine))
        ]
        refinement[name] = {
            "coarse_medium_difference": differences[0],
            "medium_fine_difference": differences[1],
            "difference_ratio": differences[0] / differences[1],
        }
    return {
        "schema_version": 1,
        "scope": "Synthetic 1D connected two-mass specimen, not a material reduction of the 69-component assembly",
        "parameter_source": "Illustrative chosen SI coefficients; no experimental fit",
        "source_sha256": hashlib.sha256(
            Path(__file__).read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest(),
        "energy_equation": "E(final)-E(initial)=external_work-dissipated",
        "integration": "fixed-step RK4; work and dissipation quadrature at RK stages",
        "refinement": refinement,
        "cases": cases,
        "remaining": [
            "geometry-to-mass/stiffness mapping",
            "material calibration",
            "nonlinear deformation/contact",
            "recursive coupling",
            "autonomous sustained breathing",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(report(), indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
