import math

import pytest

from src.sri_yantra_chambers import extract_chambers
from src.sri_yantra_huet_planar import HUET_PLANAR_SOLUTION
from src.sri_yantra_meru_candidate import (
    ConeMetric,
    audit_straight_root_chords,
    derive_meru_candidate,
)


@pytest.mark.parametrize("height,scale", [(0, 1), (0.2, 0.5), (1, 1), (3.5, 2)])
def test_all_vertices_and_edge_paths_preserve_projection_and_mirror(height, scale):
    candidate = derive_meru_candidate(ConeMetric(height, scale))
    metric, planar = candidate.metric, candidate.planar
    assert len(candidate.vertices) == len(set(candidate.vertices)) == 69
    for p, v in zip(planar.vertices, candidate.vertices, strict=True):
        assert metric.recover(v) == pytest.approx(p, abs=1e-12)
        assert metric.lift((p[0], -p[1])) == pytest.approx((v[0], -v[1], v[2]), abs=1e-12)
    for index, (a, b) in enumerate(planar.edges):
        start, end = planar.vertices[a], planar.vertices[b]
        for t in (0, 0.125, 0.5, 0.875, 1):
            v = candidate.edge_point(index, t)
            expected = tuple((1 - t) * x + t * y for x, y in zip(start, end, strict=True))
            assert metric.recover(v) == pytest.approx(expected, abs=1e-12)
            assert v[2] == pytest.approx(
                height * (1 - math.hypot(v[0], v[1]) / (scale * metric.radius)), abs=1e-12
            )
    # Recover and re-extract the generators independently of stored IDs.
    roots = tuple(
        tuple(metric.recover(metric.lift(v)) for v in t.vertices)
        for t in HUET_PLANAR_SOLUTION.triangles
    )
    recovered = extract_chambers(roots)
    assert recovered.edges == planar.edges
    assert tuple(f.boundary for f in recovered.faces) == tuple(f.boundary for f in planar.faces)
    assert recovered.chamber_contacts == planar.chamber_contacts
    assert tuple(len(recovered.ring_cycle(r)) for r in recovered.rings) == (14, 10, 10, 8, 1)


def test_straight_root_substitution_breaks_concurrency_only_when_raised():
    flat = audit_straight_root_chords(derive_meru_candidate(ConeMetric(height=0)))
    raised = audit_straight_root_chords(derive_meru_candidate())
    doubled = audit_straight_root_chords(derive_meru_candidate(ConeMetric(height=2)))
    assert flat.broken_vertex_ids == ()
    assert flat.maximum_height_spread == 0
    assert len(raised.broken_vertex_ids) == 53
    assert raised.maximum_height_spread == pytest.approx(0.796)
    assert doubled.broken_vertex_ids == raised.broken_vertex_ids
    assert doubled.maximum_height_spread == pytest.approx(2 * raised.maximum_height_spread)


def test_complete_edge_is_not_its_endpoint_chord():
    candidate = derive_meru_candidate()
    deviations = []
    for index, (a, b) in enumerate(candidate.planar.edges):
        midpoint = candidate.edge_point(index, 0.5)
        chord_height = (candidate.vertices[a][2] + candidate.vertices[b][2]) / 2
        deviations.append(abs(midpoint[2] - chord_height))
    assert max(deviations) > 1e-3


@pytest.mark.parametrize(
    "kwargs",
    [
        {"height": -1},
        {"height": math.nan},
        {"horizontal_scale": 0},
        {"horizontal_scale": math.inf},
        {"radius": 0},
    ],
)
def test_invalid_metrics_fail_closed(kwargs):
    with pytest.raises(ValueError):
        ConeMetric(**kwargs)


def test_invalid_points_and_parameters_fail_closed():
    metric = ConeMetric()
    for point in ((2, 0), (math.nan, 0)):
        with pytest.raises(ValueError):
            metric.lift(point)
    with pytest.raises(ValueError):
        metric.recover((0, 0, 0))
    for t in (-0.1, 1.1, math.inf):
        with pytest.raises(ValueError):
            metric.edge_point((0, 0), (1, 0), t)
