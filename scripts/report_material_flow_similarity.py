"""Cross-adapter shape regression; no material-to-flow point correspondence."""

import argparse
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np

from scripts.report_fold_kinematics import PIN, kinematics, prescribed
from src.toroidal_assembly_breathing import AssemblyBreathing


def normalized_distances(ids, positions):
    """Labeled squared distances divided by their sum, without fitting a map."""
    points = np.asarray(positions, dtype=float)
    if len(ids) < 2 or len(set(ids)) != len(ids):
        raise ValueError("unique point identities required")
    if points.shape != (len(ids), 3) or not np.all(np.isfinite(points)):
        raise ValueError("finite Nx3 positions matching identities required")
    pairs = list(combinations(range(len(ids)), 2))
    distances = np.array([np.sum((points[i] - points[j]) ** 2) for i, j in pairs])
    total = float(distances.sum())
    if not math.isfinite(total) or total <= 0:
        raise ValueError("noncollapsed finite point cloud required")
    return [(ids[i], ids[j]) for i, j in pairs], distances / total


def hub_ratio(state):
    points = dict(zip(state["ids"], state["position"], strict=True))
    return float(
        np.sum((points["hub-1"] - points["hub-3"]) ** 2)
        / np.sum((points["hub-0"] - points["hub-1"]) ** 2)
    )


def analytic_hub_ratio(theta):
    """Independent dot-product formula for the declared positive transverse basis."""
    return (2 + math.cos(theta) - math.sqrt(3) * math.sin(theta)) / 3


def report():
    baseline = kinematics((1.0, 0.0))
    ids = baseline["ids"]
    labels, reference = normalized_distances(ids, baseline["position"])
    cycle = AssemblyBreathing()
    rotation = np.array(((0.0, -1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)))
    rigid = baseline["position"] @ rotation.T + np.array((0.3, -0.2, 0.7))
    _, transformed = normalized_distances(ids, rigid)
    rigid_error = float(np.max(abs(transformed - reference)))
    rows = []
    for phase in np.linspace(0, 1, 17):
        phase = float(phase)
        q = prescribed(phase)
        material = kinematics(q)
        pure_scale = kinematics((q[0], 0.0))
        if material["ids"] != ids or pure_scale["ids"] != ids:
            raise ValueError("material owner identities or ordering changed")
        flow_action = np.array([cycle.forward(point, phase) for point in baseline["position"]])
        values = []
        for points in (material["position"], pure_scale["position"], flow_action):
            pair_ids, distances = normalized_distances(ids, points)
            if pair_ids != labels:
                raise ValueError("labeled point identities changed")
            values.append(distances)
        rows.append(
            dict(
                phase=phase,
                q=list(q),
                common_scale_difference=abs(q[0] - cycle.state(phase)["scale"]),
                material_shape_change=float(np.max(abs(values[0] - reference))),
                material_scale_only_error=float(np.max(abs(values[1] - reference))),
                flow_common_scale_error=float(np.max(abs(values[2] - reference))),
                hub_squared_distance_ratio=hub_ratio(material),
                analytic_hub_squared_distance_ratio=analytic_hub_ratio(q[1]),
            )
        )
    midpoint = rows[8]
    tolerance = 1e-12  # Regression roundoff bound; not a physical or clearance tolerance.
    if rigid_error > tolerance or any(
        max(
            row["common_scale_difference"],
            row["material_scale_only_error"],
            row["flow_common_scale_error"],
            abs(row["hub_squared_distance_ratio"] - row["analytic_hub_squared_distance_ratio"]),
        )
        > tolerance
        for row in rows
    ):
        raise ValueError("existing scale or analytic shape control failed")
    if midpoint["material_shape_change"] <= tolerance:
        raise ValueError("relative fold witness disappeared")
    root = Path(__file__).resolve().parents[1]
    sources = (
        "scripts/report_material_flow_similarity.py",
        "scripts/report_fold_kinematics.py",
        "src/toroidal_assembly_breathing.py",
    )
    return dict(
        schema=1,
        original_specimen_commit=PIN,
        scope="Cross-adapter regression of existing motion laws, not a new rigidity theorem",
        point_ids=ids,
        labeled_pair_count=len(labels),
        point_policy="Existing 22 body owner markers; panels use vertex means, not centroids",
        flow_action_policy="Apply existing uniform-scale operator to material reference points; these are not flow-component anchors",
        roundoff_regression_tolerance=tolerance,
        rigid_control_error=rigid_error,
        samples=rows,
        conclusion="Existing common similarity cannot reproduce the labeled relative-fold marker trajectory",
        actual_material_to_flow_correspondence=False,
        arbitrary_nonlinear_correspondence_ruled_out=False,
        clearance_audited=False,
        physical_attachment_validated=False,
        source_sha256_normalized_text={
            name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest()
            for name in sources
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Verified {result['labeled_pair_count']} labeled pairs across 17 phases")


if __name__ == "__main__":
    main()
