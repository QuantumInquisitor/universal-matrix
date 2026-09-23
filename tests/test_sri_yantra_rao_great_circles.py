import math

import pytest

from src.sri_yantra_rao_great_circles import (
    corrected_x16,
    derive_rao_great_circle_complex,
    gnomonic_lift,
    gnomonic_project,
    great_circle_residual,
    huet_vertex_correspondence,
    spherical_axis_point,
)
from src.sri_yantra_rao_spherical_reference import (
    RAO_TABLE1_REFERENCE_PARAMETERS,
    selected_constraint_residuals,
)


@pytest.fixture(scope="module")
def geometry():
    return derive_rao_great_circle_complex()


def test_refinement_stays_in_published_rounding_intervals(geometry):
    for name in ("b", "c", "d", "e", "g", "h"):
        assert (
            abs(
                getattr(geometry.derived.parameters, name)
                - getattr(RAO_TABLE1_REFERENCE_PARAMETERS, name)
            )
            < 5e-7
        )
    assert selected_constraint_residuals(geometry.derived).maximum_absolute < 1e-12


def test_printed_equation_2_22_is_a_detectable_geometric_mismatch(geometry):
    assert geometry.printed_x16_line_residual > 0.16
    assert geometry.corrected_x16_line_residual < 1e-12
    assert corrected_x16(geometry.derived) == pytest.approx(0.3061976124, abs=1e-10)
    # Preserve the literal printed value for audit; never hide the discrepancy.
    assert geometry.derived.x16 == pytest.approx(0.1083091702, abs=1e-10)


def test_equation_2_41_uses_lowercase_v8_and_lies_on_defining_arc(geometry):
    d = geometry.derived
    p = d.parameters
    p8 = spherical_axis_point(p.d + d.v8)
    point10 = spherical_axis_point(-p.g, d.x10)
    point14 = spherical_axis_point(p.d - d.u7, d.x14)
    assert great_circle_residual(p8, point10, point14) < 1e-12
    old_width = math.atan(
        math.sin(d.u7 + d.capital_v8) / math.sin(p.d + p.g + d.v8) * math.tan(d.x10)
    )
    assert great_circle_residual(p8, point10, spherical_axis_point(p.d - d.u7, old_width)) > 1e-2


def test_spherical_generators_have_common_circle_and_five_down_four_up(geometry):
    roots = geometry.root_triangles
    assert len(roots) == 9
    assert all(v[2] > 0 and abs(math.hypot(*v) - 1) < 1e-12 for t in roots for v in t)
    for i, (apex, right, left) in enumerate(roots):
        assert right[0] == pytest.approx(-left[0], abs=1e-12)
        assert right[1:] == pytest.approx(left[1:], abs=1e-12)
        apex_y = gnomonic_project(apex)[1]
        base_y = gnomonic_project(right)[1]
        assert (apex_y < base_y) == (i < 5)
    for i in (2, 6):
        assert all(
            v[2] == pytest.approx(math.cos(geometry.derived.parameters.r), abs=1e-12)
            for v in roots[i]
        )


def test_all_atomic_edge_paths_are_great_circle_arcs(geometry):
    planar = geometry.projected
    for i, j in planar.edges:
        a, b = planar.vertices[i], planar.vertices[j]
        for t in (0, 0.125, 0.5, 0.875, 1):
            sample = ((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1])
            spherical = gnomonic_lift(sample)
            assert math.hypot(*spherical) == pytest.approx(1, abs=1e-12)
            assert gnomonic_project(spherical) == pytest.approx(sample, abs=1e-12)
            assert (
                great_circle_residual(
                    geometry.spherical_nodes[i], geometry.spherical_nodes[j], spherical
                )
                < 1e-12
            )


def test_complete_labelled_complex_matches_huet(geometry):
    planar = geometry.projected
    mapping = huet_vertex_correspondence(geometry)
    assert len(mapping) == len(set(mapping)) == len(planar.vertices) == 69
    assert len(planar.edges) == 142
    assert len(planar.faces) == 74
    assert len(planar.chamber_ids) == 43
    assert tuple(len(planar.ring_cycle(r)) for r in planar.rings) == (14, 10, 10, 8, 1)
    assert all(len(f.generators) == f.depth for f in planar.faces)


@pytest.mark.parametrize("point", [(0, 0, -1), (1, 0, 0), (0, 0, 2), (math.nan, 0, 1)])
def test_gnomonic_chart_rejects_invalid_points(point):
    with pytest.raises(ValueError):
        gnomonic_project(point)
