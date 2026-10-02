"""Deterministic switched-drive restart and separate body/link energy ledgers."""

import argparse
import hashlib
import json
import math
from dataclasses import asdict, replace
from pathlib import Path

try:
    from scripts.report_material_specimen import Specimen
except ModuleNotFoundError:
    from report_material_specimen import Specimen


def source_hashes():
    return {
        name: hashlib.sha256(
            Path(__file__).with_name(name).read_text(encoding="utf-8").encode()
        ).hexdigest()
        for name in ("report_material_restart.py", "report_material_specimen.py")
    }


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()
    ).hexdigest()


def integer(value):
    if type(value) is not int or not 0 <= value <= 1_000_000:
        raise ValueError("step must be an integer in [0, 1000000]")


def finite(values):
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError("finite numeric values required")


def contract(model, dt, cutoff_step):
    finite((dt,))
    integer(cutoff_step)
    if dt <= 0 or not math.isfinite(dt * 1_000_000):
        raise ValueError("dt must be positive with finite time range")
    return {
        "schema": 1,
        "model": "two-mass-switched-rk4-v1",
        "sources": source_hashes(),
        "parameters": asdict(model),
        "dt_s": dt,
        "cutoff_step": cutoff_step,
        "cutoff_time_s": cutoff_step * dt,
        "channels": [
            "x0_m",
            "x1_m",
            "v0_mps",
            "v1_mps",
            "work_j",
            "loss_j",
            "anchor0_loss_j",
            "anchor1_loss_j",
            "link_loss_j",
            "link_to_body0_j",
            "link_to_body1_j",
        ],
    }


def start(model, dt=0.01, cutoff_step=400, initial=(0.1, 0.0, 0.0, 0.0)):
    if len(initial) != 4:
        raise ValueError("four initial values required")
    finite(initial)
    return {
        "contract": contract(model, dt, cutoff_step),
        "step": 0,
        "time_s": 0.0,
        "initial": list(initial),
        "state": list(initial) + [0.0] * 7,
    }


def validate(record, model, dt, cutoff_step):
    if set(record) != {"contract", "step", "time_s", "initial", "state"}:
        raise ValueError("checkpoint fields differ")
    if digest(record["contract"]) != digest(contract(model, dt, cutoff_step)):
        raise ValueError("checkpoint model, sources, parameters or schedule mismatch")
    integer(record["step"])
    finite((record["time_s"],))
    if record["time_s"] != record["step"] * dt:
        raise ValueError("checkpoint time disagrees with absolute step")
    if len(record["initial"]) != 4 or len(record["state"]) != 11:
        raise ValueError("checkpoint state shape differs")
    finite(record["initial"] + record["state"])
    y = record["state"]
    if any(y[i] < 0 for i in (5, 6, 7, 8)) or not math.isclose(
        y[5], sum(y[6:9]), abs_tol=1e-12, rel_tol=1e-12
    ):
        raise ValueError("inconsistent loss ledger")
    if record["step"] == 0 and y != record["initial"] + [0.0] * 7:
        raise ValueError("inconsistent initial checkpoint")


def dumps(record):
    return json.dumps(
        {"payload": record, "sha256": digest(record)}, sort_keys=True, allow_nan=False
    )


def loads(encoded, model, dt, cutoff_step):
    envelope = json.loads(encoded)
    if set(envelope) != {"payload", "sha256"} or digest(envelope["payload"]) != envelope["sha256"]:
        raise ValueError("checkpoint checksum mismatch")
    record = envelope["payload"]
    validate(record, model, dt, cutoff_step)
    return record


def owned_energy(model, y):
    x0, x1, v0, v1 = y[:4]
    return (
        0.5 * (model.mass_kg * v0**2 + model.anchor_stiffness_n_per_m * x0**2),
        0.5 * (model.mass_kg * v1**2 + model.anchor_stiffness_n_per_m * x1**2),
        0.5 * model.link_stiffness_n_per_m * (x1 - x0) ** 2,
    )


def derivative(model, t, y):
    x0, x1, v0, v1 = y[:4]
    link_force = model.link_stiffness_n_per_m * (x1 - x0) + model.link_damping_n_s_per_m * (v1 - v0)
    return model.derivative(t, y) + (
        model.anchor_damping_n_s_per_m * v0**2,
        model.anchor_damping_n_s_per_m * v1**2,
        model.link_damping_n_s_per_m * (v1 - v0) ** 2,
        link_force * v0,
        -link_force * v1,
    )


def advance(record, model, end_step):
    cfg = record["contract"]
    dt, cutoff = cfg["dt_s"], cfg["cutoff_step"]
    validate(record, model, dt, cutoff)
    integer(end_step)
    if end_step < record["step"]:
        raise ValueError("cannot step backward")
    y = tuple(record["state"])
    off = replace(model, drive_amplitude_n=0)
    for step in range(record["step"], end_step):
        # One model over the complete RK interval: the left interval owns its
        # endpoint evaluation. The next interval switches off exactly at cutoff.
        active = model if step < cutoff else off
        t = step * dt
        k1 = derivative(active, t, y)
        k2 = derivative(
            active, t + dt / 2, tuple(a + dt * b / 2 for a, b in zip(y, k1, strict=True))
        )
        k3 = derivative(
            active, t + dt / 2, tuple(a + dt * b / 2 for a, b in zip(y, k2, strict=True))
        )
        k4 = derivative(active, t + dt, tuple(a + dt * b for a, b in zip(y, k3, strict=True)))
        y = tuple(
            a + dt * (b + 2 * c + 2 * d + e) / 6
            for a, b, c, d, e in zip(y, k1, k2, k3, k4, strict=True)
        )
        finite(y)
    return {**record, "state": list(y), "step": end_step, "time_s": end_step * dt}


def balance(model, record):
    y = record["state"]
    before, after = owned_energy(model, record["initial"]), owned_energy(model, y)
    residuals = [
        after[0] - before[0] - y[4] + y[6] - y[9],
        after[1] - before[1] + y[7] - y[10],
        after[2] - before[2] + y[8] + y[9] + y[10],
    ]
    return {
        "owned_energy_j": list(after),
        "ownership_residuals_j": residuals,
        "total_balance_residual_j": sum(after) - sum(before) - y[4] + y[5],
        "work_j": y[4],
        "loss_j": y[5],
    }


def report():
    model = Specimen()
    cases = []
    for dt in (0.04, 0.02, 0.01):
        cutoff, end = round(4 / dt), round(12 / dt)
        initial = start(model, dt, cutoff)
        full = advance(initial, model, end)
        resumed = initial
        checkpoints = [cutoff // 2, cutoff, cutoff + cutoff // 2, end]
        for step in checkpoints:
            resumed = loads(dumps(advance(resumed, model, step)), model, dt, cutoff)
        switch = advance(initial, model, cutoff)
        cases.append(
            {
                "dt_s": dt,
                "checkpoint_steps": checkpoints,
                "exact_replay": full == resumed,
                "cutoff": balance(model, switch),
                "final": balance(model, full),
                "off_interval_work_j": full["state"][4] - switch["state"][4],
                "checkpoint": json.loads(dumps(full)),
            }
        )
    return {
        "schema_version": 1,
        "scope": "Synthetic two-mass SI baseline; no recursive assembly or autonomous breathing",
        "sources": source_hashes(),
        "cases": cases,
        "checksum_scope": "Detects payload alteration without checksum update; not authentication or proof of physical validity",
        "energy_ownership": "Each body owns its kinetic and anchor energy; spring energy belongs once to the link. Link damping has separate loss.",
        "remaining": [
            "material-to-geometry mapping",
            "recursive coupling",
            "autonomous motion",
            "cross-platform floating-point replay",
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
