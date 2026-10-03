"""Small frozen-grid comparison of one accepted local-frame material snapshot."""

# ruff: noqa: E402
import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.finite_spatial_descriptor import exact_unique_population, pair_distances, structure_factor

FIXTURE = ROOT / "docs/experiments/finite-spatial-descriptor-input.json"
FIXTURE_SHA256 = "639a51656f15ea0af103fb3421d3a892ec834a8985e64f2054189092eaf19323"


def describe(points):
    result = {
        "count": len(points),
        "coordinates_m": np.asarray(points).tolist(),
        "pair_distances_m": pair_distances(points).tolist(),
        "cuts": {},
    }
    for axis, name in enumerate("xyz"):
        samples = []
        for step in (2.0, 1.0):
            magnitudes = np.arange(0.0, 200.0 + step / 2, step)
            vectors = np.zeros((len(magnitudes), 3))
            vectors[:, axis] = magnitudes
            values = structure_factor(points, vectors)
            # This is the largest sampled nonzero value, not a resolved Bragg peak.
            index = 1 + int(np.argmax(values[1:]))
            samples.append(
                {
                    "step_rad_m": step,
                    "k_rad_m": magnitudes.tolist(),
                    "S": values.tolist(),
                    "nonzero_maximum": float(values[index]),
                    "nonzero_maximum_k_rad_m": float(magnitudes[index]),
                }
            )
        result["cuts"][name] = samples
    return result


def report():
    fixture_text = FIXTURE.read_text(encoding="utf-8")
    if hashlib.sha256(fixture_text.encode("utf-8")).hexdigest() != FIXTURE_SHA256:
        raise ValueError("fixture differs from accepted snapshot; review before changing its pin")
    fixture = json.loads(fixture_text)
    if fixture["units"] != "metre":
        raise ValueError("selected fixture must use metre coordinates")
    points = np.array(fixture["coordinates_m"])
    identities = fixture["occurrence_identities"]
    unique, memberships = exact_unique_population(points, identities)
    populations = {"occurrences": points, "exact_unique_coordinates": unique}
    comparisons = {}
    for label, population in populations.items():
        low, high = population.min(axis=0), population.max(axis=0)
        random_points = np.random.Generator(np.random.PCG64(7)).uniform(low, high, population.shape)
        jitter = np.random.Generator(np.random.PCG64(19)).normal(0, 0.002, population.shape)
        comparisons[label] = {
            "specimen": describe(population),
            "random": describe(random_points),
            "jittered": describe(population + jitter),
            "random_window_min_m": low.tolist(),
            "random_window_max_m": high.tolist(),
        }
    lattice = np.array(list(itertools.product(range(3), repeat=3)), dtype=float) * 0.05
    peaks = np.eye(3) * (2 * np.pi / 0.05)
    lattice_control = describe(lattice)
    lattice_control["known_reciprocal_vectors_rad_m"] = peaks.tolist()
    lattice_control["known_peak_S"] = structure_factor(lattice, peaks).tolist()
    sources = [FIXTURE, ROOT / "src/finite_spatial_descriptor.py", Path(__file__)]
    return {
        "schema": 1,
        "accepted_source_commit": "57f812f0122aea43b085204777950010fd6c8c87",
        "selection": fixture["selection"],
        "original_source_reference": fixture["source_reference"],
        "occurrence_identities": identities,
        "unique_coordinate_memberships": memberships,
        "controls": {
            "random_generator": "NumPy PCG64",
            "uniform_seed": 7,
            "jitter_seed": 19,
            "jitter_sigma_m": 0.002,
            "jitter_clipped_to_window": False,
            "lattice_shape": [3, 3, 3],
            "lattice_spacing_m": 0.05,
            "random_realizations_per_population": 1,
        },
        "grid": {
            "axes": ["x", "y", "z"],
            "range_rad_m": [0, 200],
            "steps_rad_m": [2, 1],
            "zero_excluded_from_maximum": True,
            "no_forward_lobe_exclusion": True,
        },
        "populations": comparisons,
        "periodic_control": lattice_control,
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(
                p.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest()
            for p in sources
        },
        "hash_convention": "UTF-8 text normalized to LF",
        "numpy_version": np.__version__,
        "scope": "Finite equal-weight point patterns only; no mass weights, physical scattering, bulk order, global placement or 22-to-69 mapping. Largest nonzero sample can remain in the forward lobe. One random realization supplies a comparator, not statistical significance. Quasiperiodic control deferred pending independently validated construction.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "selection": result["selection"],
                "counts": {
                    key: value["specimen"]["count"] for key, value in result["populations"].items()
                },
                "known_lattice_peak_S": result["periodic_control"]["known_peak_S"],
            }
        )
    )


if __name__ == "__main__":
    main()
