"""Trace declared state through the real fixed-assembly common breathing cycle."""

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.declared_state_recurrence import (  # noqa: E402
    clock_phase_history,
    compare,
    dumps,
    loads,
    snapshot,
)
from src.toroidal_assembly_breathing import BreathingAssembly  # noqa: E402
from src.toroidal_bore_downstream import _bounds  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/assembly-recurrence")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / "src").glob("toroidal_*.py")) + [
        ROOT / "src" / n
        for n in (
            "declared_state_recurrence.py",
            "canonical_polarity_clock.py",
            "canonical_kernel.py",
        )
    ]
    hashes = {
        str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            p.read_text().encode()
        ).hexdigest()
        for p in sources
    }
    hashes["scripts/report_assembly_recurrence.py"] = hashlib.sha256(
        Path(__file__).read_text().encode()
    ).hexdigest()
    identity = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    units = {
        "position": "reference_length",
        "velocity": "reference_length/phase",
        "orientation": "radian",
        "phase": "radian",
        "internal.scale": "dimensionless",
        "internal.drive_current": "reference_current",
    }
    tolerances = {k: 1e-10 for k in units}
    cases = []
    for current in (1.0, -1.0):
        assembly = BreathingAssembly(current)

        def at(tick, assembly=assembly, current=current):
            # Alignment of 36 clock ticks with one size cycle is an explicit
            # adapter assumption, not a recovered physical timing law.
            phase = (tick % 36) / 36
            rows = []
            for name, body in assembly.components.items():
                lo, hi = _bounds(body)
                point = assembly.cycle.forward((np.asarray(lo) + hi) / 2, phase)
                rows.append(
                    {
                        "id": name,
                        "position": point,
                        "velocity": assembly.cycle.velocity(point, phase),
                        "orientation": np.eye(3),
                        **clock_phase_history(tick),
                        "internal": {
                            "scale": assembly.cycle.state(phase)["scale"],
                            "drive_current": current,
                        },
                    }
                )
            return snapshot(
                rows, model_id=f"{identity}:common-similarity:a=0.1:I={current}", units=units
            )

        first, half, last = at(0), at(18), at(36)
        half_result = compare(first, half, tolerances=tolerances, winding_is_state=False)
        last_result = compare(first, last, tolerances=tolerances, winding_is_state=False)
        memory_result = compare(first, last, tolerances=tolerances, winding_is_state=True)
        altered = copy.deepcopy(last)
        altered["components"][0]["internal"]["drive_current"] += 0.01
        hidden_result = compare(first, altered, tolerances=tolerances, winding_is_state=False)
        assert half_result["position_return"] and not half_result["declared_state_return"]
        assert last_result["declared_state_return"] and not last_result["history_return"]
        assert (
            not memory_result["declared_state_return"]
            and not hidden_result["declared_state_return"]
        )
        resumed = loads(dumps(at(35)))
        resume_result = compare(at(35), resumed, tolerances=tolerances, winding_is_state=True)
        assert resume_result["declared_state_return"]
        restored = resumed["components"][0]
        restored_tick = int(restored["winding"]) * 36 + round(restored["phase"] * 36 / (2 * np.pi))
        replay_exact = at(restored_tick + 1) == last
        assert replay_exact
        name = f"current-{current:g}.json"
        full = {
            "current": current,
            "snapshots": {"0": first, "18": half, "35_saved": resumed, "36": last},
            "half_cycle": half_result,
            "full_cycle": last_result,
            "winding_coupled_policy_control": memory_result,
            "changed_internal_control": hidden_result,
            "save_resume": resume_result,
        }
        (args.output_dir / name).write_text(
            json.dumps(full, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        row = {
            "current": current,
            "component_count": len(first["components"]),
            "half_cycle_position_returns": half_result["position_return"],
            "half_cycle_declared_state_returns": half_result["declared_state_return"],
            "full_cycle_declared_state_returns": last_result["declared_state_return"],
            "full_cycle_history_returns": last_result["history_return"],
            "history_changed_components": len(last_result["history_changes"]),
            "winding_coupled_policy_returns": memory_result["declared_state_return"],
            "changed_internal_returns": hidden_result["declared_state_return"],
            "save_resume_exact": resumed == at(35),
            "prescribed_clock_replay_exact": replay_exact,
            "report": name,
        }
        cases.append(row)
        print(json.dumps(row), flush=True)
    manifest = {
        "scope": "Declared common-similarity state only; representative enclosing-body centers plus shape/current parameters, not a new deformation or complete material state",
        "clock_alignment": "36 canonical routing ticks assigned to one prescribed size cycle; dimensionless adapter assumption",
        "source_hash_convention": "UTF-8 decoded text with normalized newlines",
        "source_sha256": hashes,
        "cases": cases,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
