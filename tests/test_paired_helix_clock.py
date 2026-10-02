"""Independent controls for a chosen kinematic adapter, not physical evidence."""

import hashlib
import math
from pathlib import Path

import numpy as np
import pytest

from scripts.report_paired_helix_clock import build_report
from src import paired_helix_clock
from src.paired_helix_clock import PairedHelixClock, clock_rotation


@pytest.mark.parametrize("pitch", [0.3, -0.3])
def test_cardinal_coordinates_from_direct_geometry(pitch):
    adapter = PairedHelixClock(pitch=pitch, tilt_rad=0, azimuth_rad=0)
    # Two fixed material points, rather than recomputing expected rotations.
    points = [0, math.pi / 2]
    initial = [[0.4, 0, 0], [0, 0.4, pitch / 4]]
    quarter = [[0, 0.4, 0], [-0.4, 0, pitch / 4]]
    half = [[-0.4, 0, 0], [0, -0.4, pitch / 4]]
    for tick, expected in [(0, initial), (9, quarter), (18, half), (36, initial)]:
        frame = adapter.frame(tick, points)
        np.testing.assert_allclose(frame[0], expected, atol=2e-16, rtol=0)
        np.testing.assert_allclose(frame[1, :, :2], -np.array(expected)[:, :2], atol=3e-16, rtol=0)
        np.testing.assert_allclose(frame[1, :, 2], np.array(expected)[:, 2], atol=0, rtol=0)


def test_wrapping_signed_and_large_elapsed_ticks():
    for tick in (-37, -1, 0, 36, 107, 10**100, np.int64(18)):
        np.testing.assert_array_equal(clock_rotation(tick), clock_rotation(int(tick) % 36))


@pytest.mark.parametrize("pitch", [0.3, -0.3])
def test_tilted_frame_preserves_material_distances_axis_and_signed_rise(pitch):
    adapter = PairedHelixClock(pitch=pitch)
    u = np.array([-2 * math.pi, 0.35, 2 * math.pi])
    first = adapter.frame(0, u)
    axis = adapter.orientation[:, 2]
    for tick in (1, 9, 18, 27, 35, 36):
        frame = adapter.frame(tick, u)
        np.testing.assert_allclose((frame - first) @ axis, 0, atol=3e-16, rtol=0)
        np.testing.assert_allclose(
            np.linalg.norm(frame[0] - frame[1], axis=1), 0.8, atol=3e-16, rtol=0
        )
        assert np.dot(frame[0, -1] - frame[0, 0], axis) == pytest.approx(2 * pitch, abs=3e-16)
    # Full labeled return and half-cycle strand exchange are different claims.
    np.testing.assert_array_equal(adapter.frame(36, u), first)
    np.testing.assert_allclose(adapter.frame(18, u), first[::-1], atol=4e-16, rtol=0)
    assert np.linalg.norm(adapter.frame(18, u)[0, 1] - first[0, 1]) > 0.79


@pytest.mark.parametrize("tick", [9, 18, 36])
def test_wrong_108_tick_action_is_detectable(tick):
    actual = PairedHelixClock(tilt_rad=0, azimuth_rad=0).frame(tick, 0)[0]
    wrong = np.array(
        [0.4 * math.cos(2 * math.pi * tick / 108), 0.4 * math.sin(2 * math.pi * tick / 108), 0]
    )
    assert np.linalg.norm(actual - wrong) > 0.1


def test_preserved_28_checks_execute_against_published_adapter():
    report = build_report()
    assert report["checks_count"] == len(report["checks_passed"]) == 28
    assert report["parameters"]["tick_duration_s"] is None
    assert report["parameters"]["frequency_hz"] is None
    assert report["coverage"]["rotation_composition_pairs"] == 1296
    root = Path(__file__).parents[1]
    for name, digest in report["provenance"]["current_source_sha256_utf8_lf"].items():
        assert (
            hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest() == digest
        )
    assert (
        report["provenance"]["current_source_sha256_utf8_lf"]["src/canonical_polarity_clock.py"]
        == report["provenance"]["preserved_clock_sha256_utf8_lf"]
    )


def test_preserved_audit_rejects_wrong_clock_action(monkeypatch):
    monkeypatch.setattr(
        paired_helix_clock,
        "polarity_phase_from_tick",
        lambda tick: (tick % 108) * 2 * math.pi / 108,
    )
    with pytest.raises(AssertionError, match="half-cycles swap strands"):
        build_report()


@pytest.mark.parametrize("tick", [True, np.bool_(False), 1.5, "9", 1j, np.array(9)])
def test_reject_invalid_tick(tick):
    with pytest.raises(ValueError, match="tick"):
        PairedHelixClock().frame(tick, [0])


@pytest.mark.parametrize("field", ["radius", "pitch", "tilt_rad", "azimuth_rad"])
@pytest.mark.parametrize(
    "value", [True, complex(1), np.complex128(1), float("inf"), float("nan"), "0.4"]
)
def test_reject_invalid_geometric_inputs(field, value):
    with pytest.raises(ValueError, match=field):
        PairedHelixClock(**{field: value})


@pytest.mark.parametrize("value", [[], [[1]], [1, True], [0, complex(1)], [0, float("inf")]])
def test_reject_invalid_material_parameters(value):
    with pytest.raises(ValueError, match="parameter"):
        PairedHelixClock().frame(0, value)


def test_reject_nonpositive_radius_bad_label_and_unrepresentable_positions():
    for radius in (0, -1):
        with pytest.raises(ValueError, match="radius"):
            PairedHelixClock(radius=radius)
    for label in (True, -1, 2, 0.5):
        with pytest.raises(ValueError, match="label"):
            PairedHelixClock().strand(0, label)
    with pytest.raises(ValueError, match="finite and resolved"):
        PairedHelixClock(pitch=1e308).frame(0, [1e308])
