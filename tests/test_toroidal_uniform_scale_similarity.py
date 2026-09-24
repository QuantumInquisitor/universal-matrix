from __future__ import annotations

import pytest

from src.toroidal_uniform_scale_similarity import (
    ToroidalGeometryLengths,
    evaluate_vesica_similarity_clearance,
    similarity_family,
)


def test_geometry_lengths_scale_every_length_uniformly():
    geometry = ToroidalGeometryLengths()
    scaled = geometry.scaled(2.5)
    for name in geometry.__dataclass_fields__:
        assert getattr(scaled, name) == pytest.approx(
            2.5 * getattr(geometry, name)
        )


@pytest.mark.parametrize(
    ("gap", "margin", "expected_free"),
    (
        (2.5, 0.05, False),
        (3.0, 0.05, True),
        (6.5, 0.005, False),
        (8.25, 0.005, True),
    ),
)
def test_uniform_similarity_preserves_collision_classification_and_penetration(
    gap,
    margin,
    expected_free,
):
    family = similarity_family(
        gap,
        margin,
        scale_factors=(0.5, 1.0, 2.0),
    )
    assert all(result.collision_free is expected_free for result in family)
    collision_counts = {result.collision_count for result in family}
    assert len(collision_counts) == 1

    normalized = [result.normalized_penetration for result in family]
    assert normalized == pytest.approx(
        [normalized[1]] * len(normalized),
        rel=1e-10,
        abs=1e-10,
    )


def test_scaled_case_scales_declared_gap_and_margin():
    result = evaluate_vesica_similarity_clearance(2.5, 0.05, 2.0)
    assert result.scaled_shell_gap == pytest.approx(5.0)
    assert result.scaled_bend_margin == pytest.approx(0.1)


@pytest.mark.parametrize("factor", (0.0, -1.0, float("inf"), float("nan")))
def test_similarity_scale_must_be_positive_and_finite(factor):
    with pytest.raises(ValueError):
        evaluate_vesica_similarity_clearance(2.5, 0.05, factor)


def test_similarity_family_requires_at_least_one_scale():
    with pytest.raises(ValueError):
        similarity_family(2.5, 0.05, scale_factors=())
