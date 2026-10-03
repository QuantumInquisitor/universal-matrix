import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_aperture_attachment import audit_aperture_attachment, build_aperture_attachment
from src.toroidal_bore_downstream import _field


@pytest.fixture(scope="module", params=[1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0])
def reference(request):
    return build_aperture_attachment(request.param)


def physical_cut(field, center, axis, inner, outer):
    axis = np.asarray(axis, dtype=float)
    u = np.eye(3)[(np.argmax(abs(axis)) + 1) % 3]
    u = u - axis * np.dot(u, axis)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    nodes, weights = np.polynomial.legendre.leggauss(12)
    terms = []
    for x, w in zip(nodes, weights, strict=True):
        r = inner + (x + 1) * (outer - inner) / 2
        for theta in np.arange(32) * 2 * math.pi / 32:
            p = np.asarray(center) + r * (math.cos(theta) * u + math.sin(theta) * v)
            terms.append(np.dot(field(p), axis) * r * w * (outer - inner) / 2 * 2 * math.pi / 32)
    return math.fsum(terms)


def global_point(ref, local):
    return np.asarray(ref.origin) + np.asarray(local) * (1.0, ref.sign, ref.sign)


def test_exact_inventory_interfaces_and_explicit_open_faces(reference):
    report = audit_aperture_attachment(reference)
    assert report["inner_pair_count"] == 117 and report["aperture_pair_count"] == 56
    assert len(report["interfaces"]) == 3
    assert all(row["determinant_lower_bound"] > 0 for row in report["jacobians"])
    assert report["whole_bend_core_gap"] == pytest.approx(3.655996254682)
    assert report["aperture_host_gap"] == pytest.approx(3.448991570971)
    assert sum(b["outward_flux"] for b in report["open_boundaries"]) == 0
    assert np.linalg.norm(np.subtract(*[b["center"] for b in report["open_boundaries"]])) > 100
    assert not any(
        report[k]
        for k in ("full_graph_closed", "retained_collisions_resolved", "safe_motion_established")
    )


def test_host_hole_is_removed_and_outside_patch_field_is_preserved(reference):
    hole = global_point(reference, (12.4, 0, 0))
    assert not reference.modified_host_contains(hole)
    assert reference.modified_host_current(hole) is None
    for z in (-15.0, 15.0, 20.0):
        for theta in (0.0, 0.4, 1.2, math.pi):
            p = global_point(reference, (12.4 * math.cos(theta), 12.4 * math.sin(theta), z))
            actual = reference.modified_host_current(p)
            expected = _field(reference.host.geometry, p, 0.6 * reference.downstream.current)
            np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=0)


def test_host_physical_flux_across_modified_patch(reference):
    # Independent area integral, split at streamfunction transition boundaries.
    nodes, weights = np.polynomial.legendre.leggauss(48)
    rn, rw = np.polynomial.legendre.leggauss(8)
    access = reference.access
    for z in (-15.0, -5.0, 0.0, 5.0, 15.0):
        breaks = [-math.pi, 0.0, math.pi]
        for rho in (1.0, 2.0):
            rest = rho * rho - (z / access.height_scale) ** 2
            if rest > 0:
                breaks.extend((-access.alpha * math.sqrt(rest), access.alpha * math.sqrt(rest)))
        breaks = sorted(set(breaks))
        terms = []
        for lo, hi in zip(breaks, breaks[1:], strict=False):
            for x, w in zip(nodes, weights, strict=True):
                theta = lo + (x + 1) * (hi - lo) / 2
                for y, wr in zip(rn, rw, strict=True):
                    r = 12.2 + (y + 1) * 0.4 / 2
                    p = global_point(reference, (r * math.cos(theta), r * math.sin(theta), z))
                    field = reference.modified_host_current(p)
                    axial = 0.0 if field is None else field[2] * reference.sign
                    terms.append(axial * r * w * (hi - lo) / 2 * wr * 0.4 / 2)
        measured = math.fsum(terms)
        assert measured == pytest.approx(0.6 * reference.downstream.current, rel=1e-10, abs=0)


def test_inner_attachment_physical_cut_flux(reference):
    flux = reference.downstream.flux
    for item in (reference.aperture, reference.bend, reference.straight):
        volume = item.geometry.volume
        if item is reference.bend:
            cuts = [
                (volume.centerline_point(phi), volume.tangent(phi))
                for phi in (0.0, 0.31, 0.91, math.pi / 2)
            ]
        else:
            cuts = [
                (np.asarray(volume.start) * (1 - t) + np.asarray(volume.end) * t, volume.direction)
                for t in (0.0, 0.37, 1.0)
            ]
        for center, axis in cuts:
            measured = physical_cut(
                lambda p, item=item: _field(item.geometry, p, flux), center, axis, 2.0, 2.4
            )
            assert measured == pytest.approx(flux, rel=1e-10, abs=0)


def test_boundary_current_and_divergence(reference):
    # The aperture wall rho=1 has zero field; test the analytic chart directly.
    a = reference.access
    for angle in (0.0, 0.4, 1.2):
        theta = a.alpha * math.cos(angle)
        z = a.height_scale * math.sin(angle)
        np.testing.assert_allclose(
            a.host_current((12.4 * math.cos(theta), 12.4 * math.sin(theta), z)), 0, atol=1e-13
        )
    p = global_point(reference, (12.4 * math.cos(0.6), 12.4 * math.sin(0.6), 2.0))
    errors = []
    for h in (1e-2, 5e-3, 2.5e-3):
        div = 0.0
        for i in range(3):
            delta = np.eye(3)[i] * h
            div += (
                reference.modified_host_current(p + delta)[i]
                - reference.modified_host_current(p - delta)[i]
            ) / (2 * h)
        errors.append(abs(div / reference.downstream.current))
    assert errors[-1] < errors[0] / 8
    assert errors[-1] < 1e-6


def test_mutated_contracts_are_rejected():
    ref = build_aperture_attachment()
    bad = [
        replace(ref, origin=(ref.origin[0] + 1e-11, *ref.origin[1:])),
        replace(ref, access=replace(ref.access, alpha=0.51)),
        replace(ref, host_name="junction_B"),
        replace(ref, retained=ref.retained[:-1]),
        replace(ref, retained=(*ref.retained[:-1], ref.retained[0])),
        replace(
            ref,
            bend=replace(
                ref.bend,
                geometry=replace(
                    ref.bend.geometry,
                    volume=replace(ref.bend.geometry.volume, flux=-ref.downstream.flux),
                ),
            ),
        ),
    ]
    for candidate in bad:
        with pytest.raises(ValueError):
            audit_aperture_attachment(candidate)
    for p in ((1, 2), (1, 2, float("nan")), (1, 2, 1j)):
        with pytest.raises(ValueError):
            ref.modified_host_current(p)
