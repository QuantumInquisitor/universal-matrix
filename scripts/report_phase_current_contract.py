"""Compare conservation and symmetry contracts without fitting a physical adapter."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from scripts.report_fold_dynamics import Q0
from scripts.report_fold_scale_extension import connector
from src.gauge_matter import MatterSite, link_current

BASELINE_COMMIT = "493bf95089ab6f48df4b91d66eb52a3053bb0d54"
SOURCE_PATHS = (
    "scripts/report_phase_current_contract.py",
    "scripts/report_fold_recursive_phase_power.py",
    "scripts/report_fold_scale_extension.py",
    "scripts/report_fold_mapped.py",
    "scripts/report_fold_dynamics.py",
    "src/gauge_matter.py",
    "src/gauge_dynamics.py",
)


def split_power(parent_power, child_power):
    """Equal endpoint allocation of storage; an accounting convention in watts."""
    parent_power, child_power = float(parent_power), float(child_power)
    if not math.isfinite(parent_power) or not math.isfinite(child_power):
        raise ValueError("endpoint powers must be finite")
    storage = -(parent_power + child_power)
    transport = (child_power - parent_power) / 2
    return {"transport_w": transport, "storage_rate_w": storage}


def mechanical_cases():
    rows = []
    qa = Q0 + np.array((0.02, -0.03))
    qb = Q0 + np.array((-0.01, 0.04))
    for size in (1.0, 0.5, 0.25):
        for name, va, vb in (
            ("both_moving", (0.3, -0.2), (-0.1, 0.4)),
            ("parent_stationary", (0.0, 0.0), (-0.1, 0.4)),
            ("child_stationary", (0.3, -0.2), (0.0, 0.0)),
            ("both_stationary", (0.0, 0.0), (0.0, 0.0)),
        ):
            va, vb = np.asarray(va), np.asarray(vb)
            energy, fa, fb = connector(qa, qb, size, size / 2)
            pa, pb = float(fa @ va), float(fb @ vb)
            slopes = []
            for eps in (1e-5, 1e-6, 1e-7):
                slope = (
                    connector(qa + eps * va, qb + eps * vb, size, size / 2)[0]
                    - connector(qa - eps * va, qb - eps * vb, size, size / 2)[0]
                ) / (2 * eps)
                slopes.append(
                    {
                        "epsilon_s": eps,
                        "derivative_w": slope,
                        "balance_residual_w": slope + pa + pb,
                        "wrong_child_sign_residual_w": slope + pa - pb,
                    }
                )
            rows.append(
                {
                    "parent_scale": size,
                    "child_scale": size / 2,
                    "case": name,
                    "potential_j": energy,
                    "parent_power_w": pa,
                    "child_power_w": pb,
                    **split_power(pa, pb),
                    "storage_derivatives": slopes,
                }
            )
    return rows


def gauge_cases():
    rows = []
    for polarity in (-1, 1):
        for delta in (-2.1, -0.7, 0.0, 0.8, 2.4):
            a = MatterSite(1.2, 1, 0.3)
            b = MatterSite(0.8, polarity, 0.3 + delta)
            theta, coupling = 0.2, 0.5
            current = link_current(a, b, theta, coupling)
            alpha_a, alpha_b = 0.31, -0.47
            at = MatterSite(a.amplitude, a.polarity, a.phase + alpha_a)
            bt = MatterSite(b.amplitude, b.polarity, b.phase + alpha_b)
            shifted = link_current(at, bt, theta + alpha_a - alpha_b, coupling)
            rows.append(
                {
                    "target_polarity": polarity,
                    "phase_difference_rad": delta,
                    "current_model_units": current,
                    "gauge_error": abs(current - shifted),
                    "reversal_error": abs(current + link_current(b, a, -theta, coupling)),
                    "missing_link_transform_error": abs(
                        current - link_current(at, bt, theta, coupling)
                    ),
                }
            )
    return rows


def source_hashes():
    root = Path(__file__).resolve().parents[1]
    # Normalize checkout line endings so Windows and Linux record the same sources.
    return {
        name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest()
        for name in SOURCE_PATHS
    }


def report():
    return {
        "schema": 1,
        "baseline_commit": BASELINE_COMMIT,
        "scope": "Finite source-contract controls; not a trajectory or physical adapter",
        "mechanical_cases": mechanical_cases(),
        "gauge_cases": gauge_cases(),
        "storage_allocation": "equal endpoint shares; bookkeeping convention only",
        "mechanical_units": {"energy": "J", "power": "W"},
        "gauge_current_units": "model charge per model time; no SI calibration supplied",
        "physical_conversion_factor": None,
        "fitted_parameter_count": 0,
        "cross_sector_adapter_validated": False,
        "plasma_modeled": False,
        "source_hash_encoding": "UTF-8 with LF newlines",
        "sources": source_hashes(),
    }


def validate(result):
    """Acceptance checks for the declared finite controls, including fault sensitivity."""
    if result["sources"] != source_hashes():
        raise ValueError("source hash mismatch")
    assert len(result["mechanical_cases"]) == 12
    assert len(result["gauge_cases"]) == 10
    for row in result["mechanical_cases"]:
        pa, pb = row["parent_power_w"], row["child_power_w"]
        transport, storage = row["transport_w"], row["storage_rate_w"]
        assert abs(pa - (-transport - storage / 2)) < 1e-15
        assert abs(pb - (transport - storage / 2)) < 1e-15
        assert max(abs(x["balance_residual_w"]) for x in row["storage_derivatives"]) < 1e-10
        if row["case"] == "both_moving":
            assert abs(storage) > 1e-10
            assert (
                min(abs(x["wrong_child_sign_residual_w"]) for x in row["storage_derivatives"])
                > 1e-8
            )
    assert max(x["gauge_error"] for x in result["gauge_cases"]) < 1e-12
    assert max(x["reversal_error"] for x in result["gauge_cases"]) < 1e-12
    assert max(x["missing_link_transform_error"] for x in result["gauge_cases"]) > 0.1
    assert result["physical_conversion_factor"] is None
    assert not result["cross_sector_adapter_validated"]
    assert not result["plasma_modeled"]
    assert result["fitted_parameter_count"] == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    validate(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "mechanical_cases": len(result["mechanical_cases"]),
                "gauge_cases": len(result["gauge_cases"]),
                "max_balance_residual_w": max(
                    abs(d["balance_residual_w"])
                    for r in result["mechanical_cases"]
                    for d in r["storage_derivatives"]
                ),
                "physical_adapter_validated": False,
            }
        )
    )
