"""Serialize already-computed Q-ball samples; never invoke a numerical evolution."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from .qball_threshold_preserving_grid import TARGET_SHAPE, TARGET_SPACING


def timeseries_payload(result, *, configuration, provenance):
    """Preserve both channels and every sample field at Python float precision.

    Configuration and provenance are supplied explicitly: arbitrary callers must
    not have a synthetic/stub result silently labeled as the default experiment.
    """
    return {
        "schema": 1,
        "sampling": {
            "steps": result.steps,
            "dt": result.dt,
            "sample_stride": result.sample_stride,
        },
        "configuration": configuration,
        "provenance": provenance,
        "columns": {
            "step": "integer integration step",
            "time": "model time; no physical seconds calibration asserted",
            "energy_drift": "dimensionless (E-E_initial)/E_initial, per channel",
            "charge_drift": "dimensionless (Q-Q_initial)/Q_initial, per channel",
            "peak_ratio": "dimensionless max(abs(phi))/initial max(abs(phi)), per channel",
            "radius_ratio": "dimensionless RMS radius/initial RMS radius, per channel",
        },
        "channels": {
            name: [asdict(sample) for sample in getattr(result, name).samples]
            for name in ("direct", "perturbed")
        },
        "scope": "Sampled scalar diagnostics, not field checkpoints. No identified period, sustained-cycle, stability or particle claim. Cannot restart evolution from these samples.",
    }


def source_provenance(root):
    """Hash the complete local src/*.py snapshot, not a guessed dependency list."""
    root = Path(root)
    commit = None
    dirty = None
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain", "--", "src"],
                cwd=root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        pass
    return {
        "git_head": commit,
        "source_tree_dirty": dirty,
        "python": platform.python_version(),
        "packages": {name: version(name) for name in ("numpy", "scipy")},
        "source_hash_scope": "All top-level src/*.py files present at export; includes unused modules, not an execution dependency trace.",
        "source_hash_convention": "SHA256 of UTF-8 text with universal newlines normalized to LF",
        "source_sha256": {
            path.relative_to(root).as_posix(): hashlib.sha256(
                path.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for path in sorted((root / "src").glob("*.py"))
        },
    }


def write_timeseries_samples(result, destination, *, configuration, provenance):
    """Write JSON from an existing result; refuse nonfinite JSON values."""
    payload = timeseries_payload(result, configuration=configuration, provenance=provenance)
    encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(encoded, encoding="utf-8")


def export_t2p5_samples(run, destination):
    """Export an existing default-driver result; no solver or second run called."""
    configuration = {
        "driver": "src.qball_highres_timeseries_t2p5.run_high_resolution_timeseries_t2p5",
        "shape": list(TARGET_SHAPE),
        "lattice_spacing": TARGET_SPACING,
        "length_units": "model length; no physical metre calibration asserted",
        "candidate_selection": "src.qball_highres_persistence_stage1.refined_above_threshold_record",
        "candidate_selection_parameters": {"refinement_rounds": 2, "interior_points_per_round": 4},
        "perturbation": {"fractional_amplitude": 0.005, "width": 1.0},
        "configuration_scope": "Declared default driver configuration. Detailed potential, radial solver defaults and tolerance values remain in the hashed source snapshot; selected radial state and field arrays are not captured.",
    }
    write_timeseries_samples(
        run.result,
        destination,
        configuration=configuration,
        provenance=source_provenance(Path(__file__).resolve().parents[1]),
    )
