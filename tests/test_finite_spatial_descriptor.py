import itertools

import numpy as np
import pytest

from src.finite_spatial_descriptor import exact_unique_population, pair_distances, structure_factor

POINTS = np.array([[0.0, 0.0, 0.0], [0.03, 0.01, 0.04], [-0.02, 0.07, 0.01], [0.08, 0.03, -0.02]])
VECTORS = np.array([[0.0, 0.0, 0.0], [17.0, 3.0, -8.0], [-23.0, 44.0, 5.0]])


def test_independent_pair_sum_normalization_and_symmetry():
    observed = structure_factor(POINTS, VECTORS)
    expected = [
        1
        + 2
        / len(POINTS)
        * sum(np.cos(np.dot(k, a - b)) for a, b in itertools.combinations(POINTS, 2))
        for k in VECTORS
    ]
    np.testing.assert_allclose(observed, expected, atol=2e-14)
    assert observed[0] == len(POINTS)
    assert np.all(observed >= 0)
    np.testing.assert_allclose(observed, structure_factor(POINTS, -VECTORS), atol=2e-14)


def test_permutation_and_translation():
    expected = structure_factor(POINTS, VECTORS)
    np.testing.assert_allclose(
        structure_factor(POINTS[[2, 0, 3, 1]], VECTORS), expected, atol=2e-14
    )
    np.testing.assert_allclose(
        structure_factor(POINTS + [0.4, -0.3, 0.2], VECTORS), expected, atol=2e-14
    )


def test_rotation_covariance_and_scale_identity():
    angle = 0.37
    rotation = np.array(
        [[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]]
    )
    expected = structure_factor(POINTS, VECTORS)
    np.testing.assert_allclose(
        structure_factor(POINTS @ rotation.T, VECTORS @ rotation.T), expected, atol=2e-14
    )
    np.testing.assert_allclose(
        structure_factor(POINTS * 2.3, VECTORS), structure_factor(POINTS, VECTORS * 2.3), atol=2e-14
    )
    # Rotating only positions is not a coordinate-invariant directional cut.
    assert np.max(np.abs(structure_factor(POINTS @ rotation.T, VECTORS) - expected)) > 0.01


def test_cubic_known_peaks_and_extinction():
    spacing = 0.05
    points = np.array(list(itertools.product(range(3), repeat=3))) * spacing
    np.testing.assert_allclose(
        structure_factor(points, np.eye(3) * (2 * np.pi / spacing)), 27, atol=2e-13
    )
    value = structure_factor(points, [[2 * np.pi / (3 * spacing), 0, 0]])[0]
    assert value < 1e-25


def test_two_point_analytic_formula():
    wavevectors = np.array([[k, 0, 0] for k in (0, 7, 31, 52)])
    actual = structure_factor([[0, 0, 0], [0.12, 0, 0]], wavevectors)
    np.testing.assert_allclose(actual, 1 + np.cos(wavevectors[:, 0] * 0.12), atol=2e-14)


def test_exact_dedup_preserves_owners_and_near_coincidence():
    points = [[0, 0, 0], [-0.0, 0, 0], [1e-16, 0, 0], [1, 0, 0]]
    unique, owners = exact_unique_population(points, ["a", "b", "c", "d"])
    assert owners == [["a", "b"], ["c"], ["d"]]
    assert len(unique) == 3
    assert structure_factor(points, [[0, 0, 0]])[0] == 4
    assert structure_factor(unique, [[0, 0, 0]])[0] == 3
    distances = pair_distances(points)
    assert len(distances) == 6 and np.count_nonzero(distances == 0) == 1


@pytest.mark.parametrize("bad", [[], [[0, 0]], [[0, 0, np.nan]], [[0, 0, np.inf]], [[0, 0, 1j]]])
def test_invalid_coordinates_or_wavevectors(bad):
    with pytest.raises(ValueError):
        structure_factor(bad, VECTORS)
    with pytest.raises(ValueError):
        structure_factor(POINTS, bad)


def test_invalid_owner_mapping():
    with pytest.raises(ValueError):
        exact_unique_population(POINTS, ["a"])
    with pytest.raises(ValueError):
        exact_unique_population(POINTS, ["a"] * 4)


def test_report_snapshot_and_random_coordinate_reproduction():
    from scripts.report_finite_spatial_descriptor import report

    first, second = report(), report()
    assert first == second
    assert first["selection"] == {
        "frame_index": 0,
        "time_s": 0.0,
        "module_id": "module-0",
        "body_count": 22,
        "coordinate_frame": "one module local frame",
    }
    assert all(identity.startswith("module-0/") for identity in first["occurrence_identities"])
    assert [
        first["populations"][key]["specimen"]["count"]
        for key in ("occurrences", "exact_unique_coordinates")
    ] == [58, 46]


def test_report_rejects_changed_source_fixture(tmp_path, monkeypatch):
    import scripts.report_finite_spatial_descriptor as reporter

    changed = tmp_path / "changed.json"
    changed.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(reporter, "FIXTURE", changed)
    with pytest.raises(ValueError, match="fixture differs"):
        reporter.report()
