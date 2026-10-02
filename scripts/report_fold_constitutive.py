"""Synthetic membrane and axial energies on the pinned folding geometry."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .report_fold_kinematics import PANELS, PIN, core_coefficients, kinematics, rays, scalar
except ImportError:
    from report_fold_kinematics import PANELS, PIN, core_coefficients, kinematics, rays, scalar

REFERENCE = np.array((1.0, np.pi / 12))


def material(young_pa, poisson, thickness_m, bridge_ea_n=0.0):
    young, nu, thickness, axial = (
        scalar(v, n)
        for v, n in (
            (young_pa, "young_pa"),
            (poisson, "poisson"),
            (thickness_m, "thickness_m"),
            (bridge_ea_n, "bridge_ea_n"),
        )
    )
    if not 0 <= young <= 1e12 or not -1 < nu < 0.5:
        raise ValueError("young_pa in [0,1e12] and poisson in (-1,.5) required")
    if not 1e-9 <= thickness <= 1 or not 0 <= axial <= 1e12:
        raise ValueError("thickness_m in [1e-9,1] and bridge_ea_n in [0,1e12] required")
    return young, nu, thickness, axial


def coefficient_area():
    polygon = core_coefficients()
    x, y = polygon.T
    return float(abs(x @ np.roll(y, -1) - y @ np.roll(x, -1)) / 2)


def membrane_response(current, reference, *, young_pa=1000, poisson=0.3, thickness_m=1e-4):
    """Total-Lagrangian surface St Venant-Kirchhoff law, not a shell/solid law.

    Both matrices map the same two polygon coefficient coordinates into metres.
    Effective reference thickness is an independent synthetic constitutive input.
    """
    young, nu, thickness, _ = material(young_pa, poisson, thickness_m)
    arrays = []
    for value in (current, reference):
        raw = np.asarray(value)
        if raw.shape != (3, 2):
            raise ValueError("surface matrices must have shape (3,2)")
        arrays.append(np.array([[scalar(v, "surface matrix") for v in row] for row in raw]))
    a, a0 = arrays
    metric0 = a0.T @ a0
    values, vectors = np.linalg.eigh(metric0)
    if values[0] <= 0 or not np.all(np.isfinite(values)):
        raise ValueError("reference surface must have rank two")
    inverse_root = (vectors / np.sqrt(values)) @ vectors.T
    strain = 0.5 * inverse_root @ (a.T @ a - metric0) @ inverse_root
    lam, mu = young * nu / (1 - nu**2), young / (2 * (1 + nu))
    stress = lam * np.trace(strain) * np.eye(2) + 2 * mu * strain
    area = coefficient_area() * np.sqrt(np.linalg.det(metric0))
    energy = area * thickness * (0.5 * lam * np.trace(strain) ** 2 + mu * np.trace(strain @ strain))
    if not np.isfinite(energy) or not np.all(np.isfinite(stress)):
        raise ValueError("nonfinite membrane response")
    return dict(
        energy_j=float(energy),
        reference_area_m2=float(area),
        strain=strain,
        stress_pa=stress,
        inverse_reference_metric_root=inverse_root,
    )


def geometry(q, length_m=0.1):
    """Exact source midsurface vertices, bridge endpoints and hub markers."""
    kinematics(q, length_m)  # Reuse admitted coordinate/length validation only.
    s, theta = map(float, q)
    length = float(length_m)
    r, _, _ = rays(theta)
    rows = []
    for index, pair in enumerate(PANELS):
        rows.append(
            dict(
                id=f"panel-{index}",
                vertices_m=(length * s * core_coefficients() @ r[list(pair)]).tolist(),
            )
        )
    for hub in range(4):
        rows.append(dict(id=f"hub-{hub}", vertices_m=(length * s * r[hub : hub + 1] / 2).tolist()))
    for index, pair in enumerate(PANELS):
        for hub, other in (pair, pair[::-1]):
            points = np.array((0.5 * r[hub], 0.5 * r[hub] + 0.17 * r[other]))
            rows.append(dict(id=f"bridge-{index}-{hub}", vertices_m=(length * s * points).tolist()))
    return rows


def constitutive(q, *, young_pa=1000, poisson=0.3, thickness_m=1e-4, bridge_ea_n=0.1, length_m=0.1):
    """Return a new potential and its gradient; no old modal spring is added."""
    young, nu, thickness, axial = material(young_pa, poisson, thickness_m, bridge_ea_n)
    kinematics(q, length_m)
    s, theta = map(float, q)
    length = float(length_m)
    r, dr, _ = rays(theta)
    r0 = rays(REFERENCE[1])[0]
    panels, bridges = [], []
    gradient = np.zeros(2)
    for index, pair in enumerate(PANELS):
        basis, derivative = r[list(pair)].T, dr[list(pair)].T
        a = length * s * basis
        response = membrane_response(
            a,
            length * r0[list(pair)].T,
            young_pa=young,
            poisson=nu,
            thickness_m=thickness,
        )
        b = response["inverse_reference_metric_root"]
        derivatives = (length * basis, length * s * derivative)
        local = np.array(
            [
                response["reference_area_m2"]
                * thickness
                * np.sum(response["stress_pa"] * (0.5 * b @ (da.T @ a + a.T @ da) @ b))
                for da in derivatives
            ]
        )
        gradient += local
        panels.append(
            dict(
                id=f"panel-{index}",
                ray_pair=list(pair),
                energy_j=response["energy_j"],
                reference_area_m2=response["reference_area_m2"],
                green_strain=response["strain"].tolist(),
                gradient=local.tolist(),
            )
        )
        for hub, _ in (pair, pair[::-1]):
            l0 = 0.17 * length
            extension = l0 * (s - 1)
            energy = axial * extension**2 / (2 * l0)
            local = np.array((axial * extension, 0.0))
            gradient += local
            bridges.append(
                dict(
                    id=f"bridge-{index}-{hub}",
                    length_m=l0 * s,
                    reference_length_m=l0,
                    energy_j=float(energy),
                    gradient=local.tolist(),
                )
            )
    total = sum(row["energy_j"] for row in panels + bridges)
    if not np.isfinite(total) or not np.all(np.isfinite(gradient)):
        raise ValueError("nonfinite constitutive response")
    return dict(
        q=[s, theta],
        reference_q=REFERENCE.tolist(),
        total_energy_j=float(total),
        gradient=gradient.tolist(),
        gradient_units=["J per unit scale", "J/rad"],
        panels=panels,
        bridges=bridges,
        omitted_hubs=[f"hub-{i}" for i in range(4)],
    )


def report():
    root = Path(__file__).resolve().parents[1]
    fixture_path = root / "docs/experiments/fold-original-source-fixture.json"
    fixture_text = fixture_path.read_text(encoding="utf-8")
    fixture = json.loads(fixture_text)
    if fixture["reference_commit"] != PIN:
        raise ValueError("fixture pin mismatch")
    replay = []
    for case in fixture["cases"]:
        current = geometry((case["scale"], case["theta"]))
        if [r["id"] for r in current] != [r["name"] for r in case["bodies"]]:
            raise ValueError("fixture body inventory mismatch")
        replay.extend(
            float(
                np.max(
                    abs(np.array(a["vertices_m"]) - 0.1 * np.array(b["vertices_reference_length"]))
                )
            )
            for a, b in zip(current, case["bodies"], strict=True)
        )
    cases = {
        name: constitutive(q)
        for name, q in (
            ("reference", REFERENCE),
            ("scale_only", (1.03, REFERENCE[1])),
            ("fold_only", (1.0, REFERENCE[1] + 0.08)),
            ("mixed", (1.03, REFERENCE[1] + 0.08)),
        )
    }
    step = 1e-6
    gradient_controls = []
    for q in ((0.97, 0.12), (1.03, 0.34), (1.01, 0.43)):
        q = np.array(q)
        numerical = np.array(
            [
                (
                    constitutive(q + step * d)["total_energy_j"]
                    - constitutive(q - step * d)["total_energy_j"]
                )
                / (2 * step)
                for d in np.eye(2)
            ]
        )
        exact = np.array(constitutive(q)["gradient"])
        gradient_controls.append(
            dict(
                q=q.tolist(),
                step=step,
                analytic=exact.tolist(),
                finite_difference=numerical.tolist(),
                absolute_error=abs(exact - numerical).tolist(),
            )
        )
    tangent = np.column_stack(
        [
            (
                np.array(constitutive(REFERENCE + step * d)["gradient"])
                - constitutive(REFERENCE - step * d)["gradient"]
            )
            / (2 * step)
            for d in np.eye(2)
        ]
    )
    scale = cases["scale_only"]["q"][0]
    area = sum(p["reference_area_m2"] for p in cases["reference"]["panels"])
    expected_membrane = area * 1e-4 * 1000 / (1 - 0.3) * ((scale**2 - 1) / 2) ** 2
    expected_axial = 12 * 0.1 * 0.017 * (scale - 1) ** 2 / 2
    return dict(
        schema=1,
        scope="Static synthetic membrane plus optional axial reduced-element energy; no dynamics or solid-union material claim",
        sources={
            name: hashlib.sha256(
                (root / "scripts" / name).read_text(encoding="utf-8").encode()
            ).hexdigest()
            for name in ("report_fold_constitutive.py", "report_fold_kinematics.py")
        },
        fixture=dict(
            path=str(fixture_path.relative_to(root)).replace("\\", "/"),
            sha256_normalized_text=hashlib.sha256(fixture_text.encode()).hexdigest(),
            reference_commit=PIN,
            executed_sources=fixture["executed_sources"],
            cases=len(fixture["cases"]),
            body_vertex_checks=len(replay),
            max_vertex_error_m=max(replay),
        ),
        parameters=dict(
            young_pa=1000,
            poisson=0.3,
            effective_reference_thickness_m=1e-4,
            bridge_ea_n=0.1,
            length_m_per_reference_unit=0.1,
            reference_q=REFERENCE.tolist(),
        ),
        cases=cases,
        gradient_convention="Reported gradient is dV/dq; restoring generalized force is its negative",
        coefficient_controls={
            name: dict(
                options=options,
                result=constitutive(cases["mixed"]["q"], **options),
            )
            for name, options in (
                ("membrane_only", dict(bridge_ea_n=0)),
                ("axial_only", dict(young_pa=0)),
                ("zero_law", dict(young_pa=0, bridge_ea_n=0)),
            )
        },
        gradient_controls=gradient_controls,
        scale_control=dict(
            expected_membrane_j=expected_membrane,
            expected_axial_j=expected_axial,
            computed_j=cases["scale_only"]["total_energy_j"],
            absolute_error_j=abs(
                expected_membrane + expected_axial - cases["scale_only"]["total_energy_j"]
            ),
        ),
        reference_tangent=dict(
            matrix=tangent.tolist(),
            skew_error=float(np.max(abs(tangent - tangent.T))),
            numerical_eigenvalues=np.linalg.eigvalsh((tangent + tangent.T) / 2).tolist(),
            scope="Mixed-coordinate positive-definiteness diagnostic, not physical modal frequencies",
            step=step,
        ),
        limitations=[
            "synthetic uncalibrated elastic parameters",
            "effective thickness is not collision-envelope thickness",
            "surface stretching only; no bending, plasticity, buckling or failure law",
            "bridge axial law is independent of fold angle; no bridge bending model",
            "four hub constitutive energies omitted",
            "old point inertia remains unchanged; no added density or overlapping solid-volume mass",
            "membrane and bridge energies are declared reduced elements, not a solid material partition",
            "old quadratic modal potential not added",
            "static checkpoint only; no motion or collision result",
        ],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
