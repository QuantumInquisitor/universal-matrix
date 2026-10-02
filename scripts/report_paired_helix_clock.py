"""Reproduce the preserved 28 grouped helix-clock kinematic controls."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from src import canonical_polarity_clock as clock
from src.paired_helix_clock import PairedHelixClock, rotation

ROOT = Path(__file__).resolve().parents[1]


def build_report():
    source = Path(clock.__file__)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    check(
        "existing clock contract passes at all 108 base nodes",
        all(clock.verify_clock_identities(base) for base in range(108)),
    )
    check(
        "existing routing clock has 36 ticks, quarter 9, polarity 18",
        (
            clock.ROUTING_TICKS_PER_CYCLE,
            clock.ROUTING_TICKS_PER_QUARTER_CYCLE,
            clock.ROUTING_TICKS_PER_HALF_CYCLE,
        )
        == (36, 9, 18),
    )
    matrices = [rotation(clock.polarity_phase_from_tick(k)) for k in range(36)]
    orthogonality = max(np.max(np.abs(r.T @ r - np.eye(3))) for r in matrices)
    determinant = max(abs(np.linalg.det(r) - 1) for r in matrices)
    composition = max(
        np.max(np.abs(matrices[(j + k) % 36] - matrices[j] @ matrices[k]))
        for j in range(36)
        for k in range(36)
    )
    check("36 adapter rotations are orthogonal", orthogonality < 1e-14)
    check("36 adapter rotations preserve orientation", determinant < 1e-14)
    check("adapter preserves tick addition for all 1296 pairs", composition < 1e-14)
    check(
        "existing phase wraps at 36 instead of changing its API",
        clock.polarity_phase_from_tick(36) == clock.polarity_phase_from_tick(0) == 0,
    )

    radius = 0.4
    tilt = 0.49
    q = PairedHelixClock(radius=radius, tilt_rad=tilt).orientation
    axis = q[:, 2]
    u = np.linspace(-2 * math.pi, 2 * math.pi, 101)
    records = []
    for pitch in (0.3, -0.3):
        adapter = PairedHelixClock(radius=radius, pitch=pitch, tilt_rad=tilt)
        strand = adapter.strand

        def at(tick, adapter=adapter):
            return adapter.frame(tick, u)

        half_error = full_error = quarter_error = axial_error = distance_error = 0.0
        quarter_in_lab = q @ np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]) @ q.T
        for tick in range(36):
            now, half = at(tick), at(tick + 18)
            half_error = max(half_error, float(np.max(np.abs(half - now[::-1]))))
            full_error = max(full_error, float(np.max(np.abs(at(tick + 36) - now))))
            quarter_error = max(
                quarter_error, float(np.max(np.abs(at(tick + 9) - now @ quarter_in_lab.T)))
            )
            axial_error = max(axial_error, float(np.max(np.abs((now - at(0)) @ axis))))
            distance_error = max(
                distance_error,
                float(np.max(np.abs(np.linalg.norm(half - now, axis=-1) - 2 * radius))),
            )
        check(f"pitch {pitch}: all 36 half-cycles swap strands", half_error < 3e-15)
        check(f"pitch {pitch}: all 36 full cycles return labels", full_error == 0)
        check(f"pitch {pitch}: all 36 quarter-cycles rotate by 90 degrees", quarter_error < 3e-15)
        check(f"pitch {pitch}: rotation never adds axial translation", axial_error < 3e-15)
        check(f"pitch {pitch}: half-cycle material displacement is 2a", distance_error < 3e-15)
        base = at(0)
        labeled_returns = [k for k in range(1, 37) if np.max(np.abs(at(k) - base)) < 1e-12]
        unlabeled_returns = [
            k
            for k in range(1, 37)
            if min(np.max(np.abs(at(k) - base)), np.max(np.abs(at(k) - base[::-1]))) < 1e-12
        ]
        check(f"pitch {pitch}: smallest labeled return is 36", labeled_returns == [36])
        check(f"pitch {pitch}: unlabeled pair returns at 18 and 36", unlabeled_returns == [18, 36])
        rise = float(((strand(2 * math.pi, 0) - strand(0, 0)) @ q.T) @ axis)
        check(
            f"pitch {pitch}: signed pitch remains independently supplied", abs(rise - pitch) < 1e-15
        )
        marker = strand(0.35, 0)
        marker_start = marker @ q.T
        marker_distances = {
            str(k): float(
                np.linalg.norm(
                    marker @ rotation(clock.polarity_phase_from_tick(k)).T @ q.T - marker_start
                )
            )
            for k in (9, 18, 36)
        }
        check(
            f"pitch {pitch}: cardinal marker distances distinguish labels",
            abs(marker_distances["9"] - radius * math.sqrt(2)) < 1e-15
            and abs(marker_distances["18"] - 2 * radius) < 1e-15
            and marker_distances["36"] == 0,
        )
        records.append(
            {
                "pitch_per_turn": pitch,
                "half_swap_max_error": half_error,
                "full_labeled_return_max_error": full_error,
                "quarter_rotation_max_error": quarter_error,
                "axial_displacement_max_error": axial_error,
                "half_material_distance_max_error": distance_error,
                "labeled_return_ticks": labeled_returns,
                "unlabeled_return_ticks": unlabeled_returns,
                "marker_displacements": marker_distances,
            }
        )

    # Incorrectly spreading one rotation over all 108 node labels violates the
    # cardinal tick meanings even though 108 correctly also equals three cycles.
    marker = np.array([radius, 0, 0])
    wrong108 = {
        str(k): float(
            np.linalg.norm(
                marker @ rotation(2 * math.pi * k / 108).T
                - marker @ rotation(clock.polarity_phase_from_tick(k)).T
            )
        )
        for k in (9, 18, 36)
    }
    for tick, error in wrong108.items():
        check(f"negative control: 108-tick denominator breaks tick {tick}", error > 0.1)
    check(
        "canonical clock source remained unchanged",
        hashlib.sha256(source.read_bytes()).hexdigest() == source_hash,
    )
    result = {
        "scope": "chosen SO(2) adapter to existing canonical tick phase; no physical calibration",
        "clock_source": "src/canonical_polarity_clock.py",
        "clock_sha256": source_hash,
        "coverage": {
            "existing_base_node_contracts": 108,
            "ticks_per_pitch": 36,
            "pitch_signs": 2,
            "strands": 2,
            "points_per_strand": 101,
            "rotation_composition_pairs": 1296,
        },
        "parameters": {
            "radius": radius,
            "pitches": [0.3, -0.3],
            "tilt_rad": tilt,
            "azimuth_rad": -0.27,
            "length_unit": "synthetic coordinate unit",
            "tick_duration_s": None,
            "frequency_hz": None,
            "parameter_interval": [-2 * math.pi, 2 * math.pi],
        },
        "rotation_checks": {
            "orthogonality_error": float(orthogonality),
            "determinant_error": float(determinant),
            "composition_error": float(composition),
        },
        "cases": records,
        "wrong_108_tick_denominator_position_errors": wrong108,
        "checks_count": len(checks),
        "checks_passed": checks,
        "limits": [
            "Elapsed tick is supplied separately from any base-node label; no unique absolute phase is inferred from a node label.",
            "The geometry and its metric are choices; the clock supplies only a wrapped phase.",
            "This is pure rotation kinematics, with no torque, material dynamics, or frequency inferred.",
        ],
    }
    result["provenance"] = {
        "preserved_probe_sha256_raw": "577b02dfd476973e97b08a9b424ceb6b1ecad2b109d727f72a5962265caf78e3",
        "preserved_report_sha256_raw": "c5c80a5853c0b20118dcc0dc5ffc1cd42cc866a402a3f625aac939ef3bf2eba0",
        "preserved_note_sha256_raw": "67829dd1fbb962c9d65e33a0ede09225e6ebd25206ad7b3f7a7793b3351856dc",
        "preserved_clock_sha256_raw": "1ad6e30821c4283bd0f18df06d3ce0ace9b7182b2a21d8ae5f4725aa309e545a",
        "preserved_clock_sha256_utf8_lf": "e1a2f869cb62c2a9694a4bd941b217f18aaa511b5eedd49ba059a2894198c055",
        "representation_hardening": "Opposite radial coordinates use exact sign reversal instead of adding pi to the material parameter; this prevents strand collapse when a large finite parameter absorbs the pi offset. Original bounded tolerances and inputs are unchanged.",
        "current_source_sha256_utf8_lf": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for p in (
                source,
                ROOT / "src/canonical_kernel.py",
                ROOT / "src/paired_helix_clock.py",
                Path(__file__).resolve(),
            )
        },
        "hash_convention": "Preserved raw hashes retain original line endings; current UTF-8/LF hashes normalize universal newlines.",
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{result['checks_count']} preserved grouped checks passed")


if __name__ == "__main__":
    main()
