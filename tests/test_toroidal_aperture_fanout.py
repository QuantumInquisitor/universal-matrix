import math
from dataclasses import replace

import numpy as np
import pytest

from src.toroidal_aperture_attachment import build_aperture_attachment
from src.toroidal_aperture_fanout import SecondAperture, build_candidate, check_port, run
from src.toroidal_bore_downstream import _field
from src.toroidal_outer_attachment import physical_cut
from src.toroidal_shared_return_connectors import PlacedAnnularTransition
from src.toroidal_smooth_bends import AnnularQuarterBend


@pytest.fixture(params=(1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0))
def ref(request):
    return build_aperture_attachment(request.param)


def test_complete_replacement_pair_inventory(ref):
    result = run(ref.downstream.current)
    assert result["certified"]
    assert result["pair_count"] == 861
    assert len({(r["left"], r["right"]) for r in result["checks"]}) == 861
    assert len(result["interfaces"]) == 13
    assert all(j["determinant_lower_bound"] > 0 for j in result["jacobians"])
    assert not result["unresolved"] and not result["raw_host_intersections"]
    assert not result["full_network_certified"] and not result["motion_certified"]


def test_replacement_physical_cut_flux(ref):
    flux = 0.4 * ref.downstream.current
    for item in build_candidate(ref):
        obj = item.geometry
        if isinstance(obj, PlacedAnnularTransition):
            cuts = [
                (
                    (obj.origin[0], obj.origin[1], obj.origin[2] + ref.sign * t),
                    (0.0, 0.0, ref.sign),
                    obj.transition.radius(t, 0.0),
                    obj.transition.radius(t, 1.0),
                )
                for t in (0.0, 0.37, 1.0)
            ]
        else:
            v = obj.volume
            if isinstance(v, AnnularQuarterBend):
                cuts = [
                    (v.centerline_point(phi), v.tangent(phi), 2.0, 2.4)
                    for phi in (0.0, 0.31, 0.91, math.pi / 2)
                ]
            else:
                cuts = [
                    (np.asarray(v.start) * (1 - t) + np.asarray(v.end) * t, v.direction, 2.0, 2.4)
                    for t in (0.0, 0.37, 1.0)
                ]
        for center, axis, inner, outer in cuts:
            assert physical_cut(
                lambda p, obj=obj: _field(obj, p, flux), center, axis, inner, outer
            ) == pytest.approx(flux, rel=1e-10, abs=0)


def test_rotated_host_flux_and_patch_matching(ref):
    patch = SecondAperture(ref)
    nodes, weights = np.polynomial.legendre.leggauss(48)
    rn, rw = np.polynomial.legendre.leggauss(8)
    for z in (-15.0, -5.0, 0.0, 5.0, 15.0):
        breaks = [-math.pi, 0.0, math.pi]
        for rho in (1.0, 2.0):
            rest = rho * rho - (z / 6.0) ** 2
            if rest > 0:
                breaks.extend((-0.5 * math.sqrt(rest), 0.5 * math.sqrt(rest)))
        breaks = sorted(set(breaks))
        terms = []
        for lo, hi in zip(breaks, breaks[1:], strict=False):
            for x, w in zip(nodes, weights, strict=True):
                theta = lo + (x + 1) * (hi - lo) / 2
                for y, wr in zip(rn, rw, strict=True):
                    r = 12.2 + (y + 1) * 0.4 / 2
                    field = patch.current(
                        patch.to_global((r * math.cos(theta), r * math.sin(theta), z))
                    )
                    axial = 0.0 if field is None else field[2] * ref.sign
                    terms.append(axial * r * w * (hi - lo) / 2 * wr * 0.4 / 2)
        assert math.fsum(terms) == pytest.approx(0.6 * ref.downstream.current, rel=1e-10, abs=0)
    for z in (-20.0, -15.0, 15.0, 20.0):
        p = patch.to_global((12.4, 0.0, z))
        np.testing.assert_allclose(
            patch.current(p),
            _field(patch.host.geometry, p, 0.6 * ref.downstream.current),
            rtol=1e-10,
            atol=1e-20,
        )
    assert not patch.contains(patch.to_global((12.4, 0.0, 0.0)))


def test_rotated_host_divergence_and_port_rejection(ref):
    patch = SecondAperture(ref)
    p = patch.to_global((12.4 * math.cos(0.6), 12.4 * math.sin(0.6), 2.0))
    errors = []
    for h in (1e-2, 5e-3, 2.5e-3):
        div = sum(
            (patch.current(p + np.eye(3)[i] * h)[i] - patch.current(p - np.eye(3)[i] * h)[i])
            / (2 * h)
            for i in range(3)
        )
        errors.append(abs(div / ref.downstream.current))
    assert errors[-1] < errors[0] / 8 and errors[-1] < 1e-6
    route = build_candidate(ref)
    for connector, node, source in (
        (route[0].geometry, "A", True),
        (route[-1].geometry, "B", False),
    ):
        for bad in (
            replace(connector, origin=(connector.origin[0] + 1e-11, *connector.origin[1:])),
            replace(
                connector, transition=replace(connector.transition, flux=-connector.transition.flux)
            ),
        ):
            with pytest.raises(ValueError):
                check_port(ref, bad, node, source)
