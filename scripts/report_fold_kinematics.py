"""Two-coordinate, synthetic point-mass reduction of the pinned 22-body specimen."""

import argparse
import hashlib
import json
import math
from numbers import Real
from pathlib import Path

import numpy as np

PIN = "60a7fd60f57d73b89ea5397db58a3ff5d291556c"
PANELS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def scalar(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real scalar")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite real scalar") from error
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def core_coefficients():
    """Port of pinned pentagon_coefficients(.15), not a new panel construction."""
    vertices = [np.zeros(2)]
    for k in range(4):
        vertices.append(
            vertices[-1] + (math.cos(2 * math.pi * k / 5), math.sin(2 * math.pi * k / 5))
        )
    basis = np.array(((1.0, math.cos(3 * math.pi / 5)), (0.0, math.sin(3 * math.pi / 5))))
    polygon = np.linalg.solve(basis, np.array(vertices).T).T
    polygon[0], polygon[1], polygon[-1] = (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)
    for axis in (0, 1):
        clipped = []
        for a, b in zip(polygon, np.roll(polygon, -1, axis=0), strict=True):
            if a[axis] >= 0.15:
                clipped.append(a)
            if (a[axis] >= 0.15) != (b[axis] >= 0.15):
                clipped.append(a + (0.15 - a[axis]) / (b[axis] - a[axis]) * (b - a))
        polygon = np.array(clipped)
    return polygon


def inventory():
    """One synthetic lump per body; panel point is vertex mean, not mass centroid."""
    rows = []
    mean = core_coefficients().mean(axis=0)
    for panel, pair in enumerate(PANELS):
        c = np.zeros(4)
        c[list(pair)] = mean
        rows.append((f"panel-{panel}", c, 0.1))
    for hub in range(4):
        rows.append((f"hub-{hub}", 0.5 * np.eye(4)[hub], 0.02))
    for panel, pair in enumerate(PANELS):
        for hub, other in (pair, pair[::-1]):
            c = 0.5 * np.eye(4)[hub] + 0.085 * np.eye(4)[other]
            rows.append((f"bridge-{panel}-{hub}", c, 0.005))
    return rows


def rays(theta):
    """Pinned rotation plane and its first/second theta derivatives."""
    r = np.array(((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))) / math.sqrt(3)
    axis = r[0]
    cosine = float(r[3] @ axis)
    u = r[3] - cosine * axis
    radius = np.linalg.norm(u)
    u /= radius
    w = r[1] - (r[1] @ axis) * axis - (r[1] @ u) * u
    w /= np.linalg.norm(w)
    rotating = radius * (math.cos(theta) * u + math.sin(theta) * w)
    r[3] = cosine * axis + rotating
    dr, ddr = np.zeros((4, 3)), np.zeros((4, 3))
    dr[3] = radius * (-math.sin(theta) * u + math.cos(theta) * w)
    ddr[3] = -rotating
    return r, dr, ddr


def kinematics(q, length_m=0.1, masses=None):
    """Return x[n,xyz], J[n,xyz,q], H[n,xyz,q,q], M[q,q].

    Rectangle is numerical scope only, not an independent collision certificate.
    Positive masses give rank-two inertia throughout this domain: hub 0 has
    nonzero x_s and zero x_theta, so a null velocity requires sdot=0. Hub 3
    then has nonzero x_theta for positive length and s, requiring thetadot=0.
    """
    if not isinstance(q, (tuple, list, np.ndarray)) or np.shape(q) != (2,):
        raise ValueError("q must contain scale and theta")
    s, theta = (scalar(v, "q") for v in q)
    length = scalar(length_m, "length_m")
    if not 0.9 <= s <= 1.1 or not 0 <= theta <= math.pi / 6:
        raise ValueError("outside declared scope [.9,1.1] x [0,pi/6]")
    if not 1e-6 <= length <= 1e3:
        raise ValueError("length_m numerical scope is [1e-6,1e3]")
    rows = inventory()
    ids = [row[0] for row in rows]
    if masses is None:
        masses = {name: mass for name, _, mass in rows}
    if not isinstance(masses, dict) or set(masses) != set(ids):
        raise ValueError("exactly one mass owner per body ID required")
    mass = np.array([scalar(masses[name], "mass") for name in ids])
    if np.any(mass < 1e-9) or np.any(mass > 1e6):
        raise ValueError("mass numerical scope is [1e-9,1e6] kg")
    c = np.array([row[1] for row in rows])
    r, dr, ddr = rays(theta)
    base, first, second = c @ r, c @ dr, c @ ddr
    x = length * s * base
    jac = np.stack((length * base, length * s * first), axis=2)
    hess = np.zeros((22, 3, 2, 2))
    hess[:, :, 0, 1] = hess[:, :, 1, 0] = length * first
    hess[:, :, 1, 1] = length * s * second
    matrix = np.einsum("n,nxa,nxb->ab", mass, jac, jac)
    return dict(ids=ids, position=x, jacobian=jac, hessian=hess, mass=mass, mass_matrix=matrix)


def prescribed(phase):
    p = scalar(phase, "phase")
    if not 0 <= p <= 1:
        raise ValueError("phase must be in [0,1]")
    sine = {0.0: 0.0, 0.25: 1.0, 0.5: 0.0, 0.75: -1.0, 1.0: 0.0}.get(p, math.sin(2 * math.pi * p))
    theta = 0.0 if p in (0.0, 1.0) else math.pi / 6 * math.sin(math.pi * p) ** 2
    return (1 + 0.1 * sine, theta)


def report():
    fixture_path = (
        Path(__file__).resolve().parents[1] / "docs/experiments/fold-original-source-fixture.json"
    )
    fixture_text = fixture_path.read_text(encoding="utf-8")
    fixture = json.loads(fixture_text)
    if fixture["reference_commit"] != PIN:
        raise ValueError("original-source fixture must match pinned commit")
    replay_errors = []
    for case in fixture["cases"]:
        state = kinematics((case["scale"], case["theta"]))
        if state["ids"] != [body["name"] for body in case["bodies"]]:
            raise ValueError("original-source body inventory mismatch")
        original = 0.1 * np.array([body["coefficient_mean_position"] for body in case["bodies"]])
        replay_errors.append(float(np.max(np.abs(original - state["position"]))))
    samples = []
    for p in np.linspace(0, 1, 17):
        q = prescribed(float(p))
        state = kinematics(q)
        velocity = np.array((0.21, -0.37))  # chosen per-second coordinate rates
        point_v = state["jacobian"] @ velocity
        point_energy = float(np.sum(state["mass"][:, None] * point_v**2) / 2)
        reduced_energy = float(velocity @ state["mass_matrix"] @ velocity / 2)
        samples.append(
            dict(
                phase=float(p),
                q=q,
                positions_m=state["position"].tolist(),
                mass_matrix=state["mass_matrix"].tolist(),
                minimum_eigenvalue=float(np.linalg.eigvalsh(state["mass_matrix"])[0]),
                kinetic_identity_absolute_error_j=abs(point_energy - reduced_energy),
            )
        )
    return dict(
        schema_version=1,
        source_commit=PIN,
        source_url=f"https://github.com/QuantumInquisitor/universal-matrix/tree/{PIN}",
        adapter_sha256=hashlib.sha256(
            Path(__file__).read_text(encoding="utf-8").encode()
        ).hexdigest(),
        body_ids=kinematics((1.0, 0.0))["ids"],
        source_modules=[
            f"src/lynchpin_{name}_control.py"
            for name in ("relative_motion", "finite_panel", "connected", "breathing")
        ],
        length_m_per_reference_unit=0.1,
        synthetic_mass_kg={name: mass for name, _, mass in inventory()},
        synthetic_mass_total_kg=float(sum(row[2] for row in inventory())),
        ownership="one point mass per body; no sum of overlapping solid volumes",
        admissibility="rectangle inherits geometry conditionally if all original occupied envelopes and contacts scale; see docs/fold_domain_inheritance.md; not a new clearance audit",
        independent_original_source_replay=dict(
            fixture_path="docs/experiments/fold-original-source-fixture.json",
            fixture_sha256_normalized_text=hashlib.sha256(fixture_text.encode()).hexdigest(),
            cases=len(replay_errors),
            maximum_position_absolute_error_m=max(replay_errors),
            executed_sources=fixture["executed_sources"],
            scope="sampled original-source mean-vertex positions; no continuous collision rerun",
        ),
        physical_material_validation=False,
        dynamics_implemented=False,
        phase_is_physical_time=False,
        samples=samples,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report(), indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
