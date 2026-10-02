"""Join original prescribed geometry to a reference-correct synthetic material overlay."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

try:
    from . import report_fold_constitutive as material
    from .report_fold_kinematics import scalar
except ImportError:
    import report_fold_constitutive as material
    from report_fold_kinematics import scalar

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/experiments/fold-original-source-fixture.json"
LENGTH = 0.1


def vertices(value):
    raw = np.asarray(value)
    if raw.ndim != 2 or raw.shape[1] != 3 or len(raw) < 1:
        raise ValueError("vertices must be a nonempty Nx3 array")
    return np.array([[scalar(v, "vertex") for v in row] for row in raw])


def affine_stretches(reference, current):
    """Fit a 2D-to-3D affine map from independent corresponding source vertices."""
    reference, current = vertices(reference), vertices(current)
    if reference.shape != current.shape or len(reference) < 3:
        raise ValueError("matching polygon vertices required")
    centered = reference - reference.mean(axis=0)
    _, singular, basis = np.linalg.svd(centered, full_matrices=False)
    if singular[1] <= 1e-12 or singular[2] > 1e-10 * singular[0]:
        raise ValueError("reference polygon must have a nondegenerate planar span")
    coordinates = centered @ basis[:2].T
    target = current - current.mean(axis=0)
    mapping, _, rank, _ = np.linalg.lstsq(coordinates, target, rcond=None)
    if rank != 2:
        raise ValueError("reference affine fit must have rank two")
    return dict(
        principal_stretches=np.sort(np.linalg.svd(mapping, compute_uv=False)).tolist(),
        maximum_fit_residual_m=float(np.max(abs(coordinates @ mapping - target))),
    )


def build_overlay(fixture):
    if fixture.get("schema") != 1 or fixture.get("reference_commit") != material.PIN:
        raise ValueError("unsupported fixture schema or reference commit")
    cases = fixture.get("cases")
    if not isinstance(cases, list) or len(cases) != 9:
        raise ValueError("the pinned nine-frame source fixture is required")
    phases = [scalar(case["phase"], "phase") for case in cases]
    if phases != [i / 8 for i in range(9)]:
        raise ValueError("fixture phases must cover the original nine ordered samples")
    expected_ids = [row["id"] for row in material.geometry(material.REFERENCE)]
    source_errors = []
    for case in cases:
        q = (scalar(case["scale"], "scale"), scalar(case["theta"], "theta"))
        phase = case["phase"]
        if not math.isclose(
            q[0], 1 + 0.1 * math.sin(2 * math.pi * phase), abs_tol=1e-14
        ) or not math.isclose(q[1], math.pi / 6 * math.sin(math.pi * phase) ** 2, abs_tol=1e-14):
            raise ValueError("fixture coordinates do not match the declared prescribed phase")
        original = case["bodies"]
        if [row["name"] for row in original] != expected_ids:
            raise ValueError("fixture body IDs/order do not match the pinned inventory")
        for actual, expected in zip(original, material.geometry(q), strict=True):
            points = vertices(actual["vertices_reference_length"])
            mean = vertices([actual["coefficient_mean_position"]])[0]
            if not np.allclose(mean, points.mean(axis=0), rtol=1e-12, atol=1e-14):
                raise ValueError("fixture mean marker does not match source vertices")
            kind = actual["name"].split("-")[0]
            if actual["kind"] != kind or points.shape != np.shape(expected["vertices_m"]):
                raise ValueError("fixture body kind or vertex shape mismatch")
            radius = scalar(actual["radius_reference_length"], "offset radius")
            expected_radius = q[0] * {"panel": 0.01, "hub": 0.05, "bridge": 0.008}[kind]
            if not math.isclose(radius, expected_radius, rel_tol=1e-12, abs_tol=1e-14):
                raise ValueError("fixture offset radius does not match source geometry")
            error = float(np.max(abs(LENGTH * points - expected["vertices_m"])))
            if error > 1e-12:
                raise ValueError("fixture vertices disagree with the pinned geometry adapter")
            source_errors.append(error)
    reference = next(
        (
            case
            for case in cases
            if math.isclose(case["theta"], material.REFERENCE[1], abs_tol=1e-14)
        ),
        None,
    )
    if reference is None:
        raise ValueError("fixture lacks the material reference angle")
    reference_panels = {
        b["name"]: LENGTH * vertices(b["vertices_reference_length"]) / reference["scale"]
        for b in reference["bodies"]
        if b["kind"] == "panel"
    }
    old_reference = {
        b["name"]: LENGTH * vertices(b["vertices_reference_length"]) / cases[0]["scale"]
        for b in cases[0]["bodies"]
        if b["kind"] == "panel"
    }
    frames, errors, fit_errors, mismatch_errors, ownership_errors = [], [], [], [], []
    for case in cases:
        response = material.constitutive((case["scale"], case["theta"]))
        elements = {b["id"]: b for b in response["panels"] + response["bridges"]}
        bodies = []
        for source in case["bodies"]:
            name, kind = source["name"], source["kind"]
            points = LENGTH * vertices(source["vertices_reference_length"])
            body = dict(
                id=name,
                kind=kind,
                vertices_reference_length=source["vertices_reference_length"],
                radius_reference_length=source["radius_reference_length"],
                source_coefficient_mean_position=source["coefficient_mean_position"],
                vertices_m=points.tolist(),
                offset_radius_m=LENGTH * source["radius_reference_length"],
                offset_scope="source occupied-envelope radius; not effective material thickness",
            )
            if kind == "hub":
                body["material"] = dict(
                    status="unmodeled", energy_j=None, restoring_generalized_force=None
                )
            else:
                element = elements[name]
                overlay = dict(
                    status="synthetic membrane"
                    if kind == "panel"
                    else "synthetic axial centerline",
                    energy_j=element["energy_j"],
                    restoring_generalized_force=(-np.array(element["gradient"])).tolist(),
                )
                if kind == "panel":
                    independent = affine_stretches(reference_panels[name], points)
                    expected = np.sqrt(
                        np.linalg.eigvalsh(np.eye(2) + 2 * np.array(element["green_strain"]))
                    )
                    error = float(np.max(abs(expected - independent["principal_stretches"])))
                    wrong = affine_stretches(old_reference[name], points)["principal_stretches"]
                    mismatch = float(np.max(abs(expected - wrong)))
                    errors.append(error)
                    fit_errors.append(independent["maximum_fit_residual_m"])
                    mismatch_errors.append(mismatch)
                    overlay.update(
                        green_strain=element["green_strain"],
                        principal_stretches=expected.tolist(),
                        original_vertex_affine_fit=independent,
                        principal_stretch_absolute_error=error,
                        theta_zero_reference_negative_control=dict(
                            principal_stretches=wrong, discrepancy=mismatch
                        ),
                    )
                body["material"] = overlay
            bodies.append(body)
        owned_energy = sum(b["material"]["energy_j"] for b in bodies if b["kind"] != "hub")
        ownership_errors.append(abs(owned_energy - response["total_energy_j"]))
        frames.append(
            dict(
                phase=case["phase"],
                q=response["q"],
                motion="prescribed source phase; not a force-driven trajectory or physical time",
                total_energy_j=response["total_energy_j"],
                restoring_generalized_force=(-np.array(response["gradient"])).tolist(),
                bodies=bodies,
            )
        )
    return dict(
        schema="lynchpin-material-overlay-v1",
        units="metres, joules; scale dimensionless and angle radians",
        parameters=dict(
            young_pa=1000,
            poisson=0.3,
            effective_reference_thickness_m=1e-4,
            bridge_ea_n=0.1,
            length_m_per_reference_unit=LENGTH,
        ),
        reference=dict(
            material_q=material.REFERENCE.tolist(),
            source_fixture_phase=reference["phase"],
            divided_out_source_scale=reference["scale"],
            old_geometry_reference_q=[1, 0],
            independent_method="Center source reference vertices, obtain plane basis by SVD, least-squares affine map to each source polygon, then singular values",
        ),
        force_convention="negative potential gradient; components J per unit scale and J/rad; not Cartesian nodal force",
        frames=frames,
        controls=dict(
            source_vertex_checks=len(source_errors),
            maximum_source_vertex_error_m=max(source_errors),
            panel_stretch_comparisons=len(errors),
            maximum_principal_stretch_error=max(errors),
            maximum_affine_fit_residual_m=max(fit_errors),
            maximum_energy_ownership_error_j=max(ownership_errors),
            mismatched_theta_zero_reference_maximum_discrepancy=max(mismatch_errors),
        ),
        limitations=[
            "nine existing fixture phases, not a replacement for the 202-frame source exporter",
            "all motions prescribed; no time integration or new force-driven trajectory",
            "six membrane and twelve axial energy owners; four hubs have no constitutive law",
            "synthetic uncalibrated parameters; no added mass or full-solid material partition",
            "offset envelopes are preserved metadata, not a through-thickness material map",
            "no viewer or headset integration performed by this exporter",
            "old theta-zero reference must not be substituted for the material reference",
        ],
    )


def report(fixture_path=FIXTURE, *, expected_fixture_sha256=None):
    text = Path(fixture_path).read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    if expected_fixture_sha256 is not None and expected_fixture_sha256 != digest:
        raise ValueError("fixture normalized-text SHA256 mismatch")
    fixture = json.loads(text)
    result = build_overlay(fixture)
    result["source_fixture"] = dict(
        reference_commit=fixture["reference_commit"],
        sha256_normalized_text=digest,
        executed_sources=fixture["executed_sources"],
    )
    result["sources"] = {
        name: hashlib.sha256(
            (ROOT / "scripts" / name).read_text(encoding="utf-8").encode()
        ).hexdigest()
        for name in (
            "export_lynchpin_material_scene.py",
            "report_fold_constitutive.py",
            "report_fold_kinematics.py",
        )
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
