"""Energy-consistent cubic cosine Galerkin audit; dimensionless model units."""

import argparse
import hashlib
import json
from numbers import Real
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = "docs/recovery/wave-source-provenance.json"


def finite(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be finite real")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{name} must be finite real") from error
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite real")
    return result


class Galerkin:
    """u(x,t)=sum q_n(t) cos(nx); <cos(nx)^2>=1/2 on [0,2pi)."""

    def __init__(self, modes=(1, 3, 5), *, beta=1.0, damping=0.02, modulation=0.2, points=64):
        if not isinstance(modes, (list, tuple)) or tuple(modes) not in ((1,), (1, 3), (1, 3, 5)):
            raise ValueError("modes must be (1), (1,3), or (1,3,5)")
        if any(type(n) is not int for n in modes):
            raise ValueError("mode indices must be integers")
        if type(points) is not int or points < 64:
            raise ValueError("quadrature requires at least64 integer points")
        self.beta = finite(beta, "beta")
        self.damping = finite(damping, "damping")
        self.modulation = finite(modulation, "modulation")
        if self.beta < 0 or self.damping < 0 or not 0 <= self.modulation < 1:
            raise ValueError("beta/damping nonnegative and modulation in[0,1) required")
        self.modes = np.array(modes)
        self.points = points
        self.basis = np.cos(self.modes[:, None] * (2 * np.pi * np.arange(points) / points))
        self.omega2 = self.modes.astype(float) ** 2
        self.drive = 2.0

    def cubic(self, q):
        field = np.asarray(q) @ self.basis
        # Divide the projection by modal mass <cos^2>=1/2.
        return 2 * self.beta * (self.basis @ field**3) / self.points

    def quartic(self, q):
        field = np.asarray(q) @ self.basis
        # E is twice the spatially averaged field energy, i.e. unit modal mass.
        return float(self.beta * np.mean(field**4) / 2)

    def energy(self, time, state):
        n = len(self.modes)
        q, v = state[:n], state[n : 2 * n]
        return float(
            (v @ v + (1 + self.modulation * np.cos(self.drive * time)) * (self.omega2 @ q**2)) / 2
            + self.quartic(q)
        )

    def rhs(self, time, state):
        n = len(self.modes)
        q, v = state[:n], state[n : 2 * n]
        acceleration = (
            -(1 + self.modulation * np.cos(self.drive * time)) * self.omega2 * q
            - self.cubic(q)
            - 2 * self.damping * v
        )
        work = -self.modulation * self.drive * np.sin(self.drive * time) * (self.omega2 @ q**2) / 2
        loss = 2 * self.damping * (v @ v)
        return np.r_[v, acceleration, work, loss]


def simulate(modes=(1, 3, 5), *, periods=20, steps_per_period=32, rtol=1e-9, modulation=0.2):
    if type(periods) is not int or not 1 <= periods <= 20:
        raise ValueError("periods must be integer in[1,20]")
    if type(steps_per_period) is not int or not 16 <= steps_per_period <= 256:
        raise ValueError("steps_per_period must be integer in[16,256]")
    rtol = finite(rtol, "rtol")
    if not 1e-12 <= rtol <= 1e-6:
        raise ValueError("rtol must lie in[1e-12,1e-6]")
    model = Galerkin(modes, modulation=modulation)
    n = len(modes)
    initial = np.zeros(2 * n + 2)
    initial[0] = 0.1
    period = 2 * np.pi / model.drive
    times = np.linspace(0, periods * period, periods * 10 + 1)
    solution = solve_ivp(
        model.rhs,
        (0, times[-1]),
        initial,
        method="DOP853",
        t_eval=times,
        max_step=period / steps_per_period,
        rtol=rtol,
        atol=rtol * 1e-3,
    )
    if not solution.success or len(solution.t) != len(times) or not np.isfinite(solution.y).all():
        raise RuntimeError("integration failed to complete finite matched-time output")
    states = solution.y.T
    energy = np.array([model.energy(t, state) for t, state in zip(times, states, strict=True)])
    work, loss = states[:, -2], states[:, -1]
    residual = energy - energy[0] - work + loss
    quadratic = (states[:, n : 2 * n] ** 2 + states[:, :n] ** 2 * model.omega2) / 2
    return dict(
        parameters=dict(
            modes=list(modes),
            beta=model.beta,
            damping=model.damping,
            modulation=model.modulation,
            drive=model.drive,
            periods=periods,
            steps_per_period=steps_per_period,
            rtol=rtol,
            atol=rtol * 1e-3,
            quadrature_points=model.points,
            initial_state=initial.tolist(),
        ),
        completed=True,
        times=times.tolist(),
        states=states.tolist(),
        total_energy=energy.tolist(),
        drive_work=work.tolist(),
        damping_loss=loss.tolist(),
        balance_residual=residual.tolist(),
        max_abs_balance_residual=float(max(abs(residual))),
        max_abs_q_per_mode=np.max(abs(states[:, :n]), axis=0).tolist(),
        final_quadratic_energy_per_mode=quadratic[-1].tolist(),
        max_quadratic_energy_per_mode=np.max(quadratic, axis=0).tolist(),
        final_total_energy=float(energy[-1]),
        final_drive_work=float(work[-1]),
        final_damping_loss=float(loss[-1]),
        function_evaluations=solution.nfev,
    )


def compare(a, b, *, kind):
    if a["times"] != b["times"]:
        raise ValueError("comparisons require identical sample times")
    am, bm = a["parameters"]["modes"], b["parameters"]["modes"]
    shared = sorted(set(am) & set(bm))
    x, y = np.array(a["states"]), np.array(b["states"])
    differences = {}
    for mode in shared:
        i, j = am.index(mode), bm.index(mode)
        differences[str(mode)] = dict(
            max_abs_q=float(max(abs(x[:, i] - y[:, j]))),
            max_abs_rate=float(max(abs(x[:, len(am) + i] - y[:, len(bm) + j]))),
        )
    return dict(
        kind=kind,
        matched_sample_count=len(a["times"]),
        shared_modes=shared,
        per_mode=differences,
        max_abs_total_energy_difference=float(
            max(abs(np.array(a["total_energy"]) - b["total_energy"]))
        ),
        note="Truncation energy differences compare distinct models; numerical refinement uses the same model.",
    )


def file_hash(path):
    return hashlib.sha256((ROOT / path).read_text(encoding="utf-8").encode()).hexdigest()


def report():
    sources = {path: file_hash(path) for path in ("scripts/report_wave_harmonics.py", PROVENANCE)}
    manifest = json.loads((ROOT / PROVENANCE).read_text(encoding="utf-8"))
    legacy = manifest["w1"]
    cases = {}
    for name, modes, options in (
        ("one", (1,), {}),
        ("three", (1, 3), {}),
        ("five", (1, 3, 5), {}),
        ("fine_five", (1, 3, 5), dict(steps_per_period=64, rtol=1e-10)),
        ("drive_off", (1, 3, 5), dict(modulation=0.0)),
    ):
        print(f"Running {name}", flush=True)
        cases[name] = simulate(modes, **options)
    return dict(
        schema=1,
        sources=sources,
        provenance=dict(
            manifest_path=PROVENANCE,
            published_pr=manifest["published_pr"],
            published_head=manifest["published_head"],
            legacy_report_path=legacy["artifact"],
            legacy_normalized_utf8_sha256=legacy["normalized_artifact_sha256"],
            legacy_limitations=legacy["recorded_limitation"],
            legacy_source_inventory=legacy["sources"],
            hash_scope="Legacy artifact hash inherited from the recovered provenance manifest; legacy artifact is not required or reverified during this run.",
            exact_legacy_model_continuation=False,
            reason="Legacy sources absent from this tracked checkout were located in separately published PR120; this is a separately declared cubic Galerkin experiment.",
        ),
        protocol=dict(
            units="dimensionless model units; no calibrated material parameters",
            field="u(x,t)=sum q_n(t)*cos(n*x), x in[0,2*pi)",
            modal_mass=1.0,
            spatial_average_cosine_norm_squared=0.5,
            total_energy_normalization="twice the spatial average of the field energy",
            cubic_force="2*beta*mean(cos(n*x)*u^3)",
            quartic_potential="beta*mean(u^4)/2",
            drive="uniform parametric stiffness modulation; no additive third/fifth harmonic drive",
            maximum_quartic_spatial_frequency=20,
            quadrature_points=64,
            initial_higher_harmonics="zero; only q1=0.1, all velocities and ledgers zero",
            modal_quadratic_energy_note="Unmodulated quadratic part only; excludes time-dependent pump stiffness and shared quartic potential.",
        ),
        cases=cases,
        comparisons=dict(
            one_to_three=compare(cases["one"], cases["three"], kind="truncation"),
            three_to_five=compare(cases["three"], cases["five"], kind="truncation"),
            five_to_fine=compare(cases["five"], cases["fine_five"], kind="numerical_refinement"),
        ),
        pattern_selection_established=False,
        traveling_wave=False,
        quantum_model=False,
        limitations="Finite cosine/odd-mode truncation with one seeded wavelength; no boundary/noise ensemble or calibrated physical medium.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
