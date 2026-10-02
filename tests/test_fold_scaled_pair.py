"""Force gradients, full pair similarity and conservative non-similarity control."""

import numpy as np
import pytest

from scripts.report_fold_dynamics import Q0
from scripts.report_fold_scaled_pair import (
    comparison,
    connector,
    initial_state,
    measure,
    rhs,
    simulate,
    sizes,
)


@pytest.mark.parametrize("scale", [1.0, 0.75, 0.5])
def test_connector_gradient_and_uniform_scaling(scale):
    qa, qb = Q0 + (0.015, -0.02), Q0 + (-0.01, 0.015)
    u, fa, fb = connector(qa, qb, scale)
    u0, a0, b0 = connector(qa, qb)
    assert u == pytest.approx(scale**3 * u0, rel=1e-13)
    np.testing.assert_allclose(fa, scale**3 * a0, rtol=1e-13, atol=0)
    np.testing.assert_allclose(fb, scale**3 * b0, rtol=1e-13, atol=0)
    for k in range(2):
        h = np.eye(2)[k] * 1e-6
        da = (connector(qa + h, qb, scale)[0] - connector(qa - h, qb, scale)[0]) / 2e-6
        db = (connector(qa, qb + h, scale)[0] - connector(qa, qb - h, scale)[0]) / 2e-6
        assert da == pytest.approx(-fa[k], abs=1e-13)
        assert db == pytest.approx(-fb[k], abs=1e-13)


@pytest.mark.parametrize("fixed", [False, True])
def test_energy_directional_identity_for_both_stiffness_laws(fixed):
    scale = 0.5
    y = initial_state(scale)
    y[7:9] = (0.03, -0.04)
    d = rhs(y, scale, fixed_stiffness=fixed)
    eps = 1e-6
    plus = measure(y + eps * d, scale, fixed_stiffness=fixed)[2]
    minus = measure(y - eps * d, scale, fixed_stiffness=fixed)[2]
    assert abs((plus - minus) / 2 / eps) < 1e-12


def test_full_acceleration_and_work_similarity():
    y = initial_state()
    y[7:9] = (0.03, -0.04)
    scale = 0.75
    small = y.copy()
    small[[2, 3, 7, 8]] /= scale
    d0 = rhs(y)
    ds = rhs(small, scale)
    np.testing.assert_allclose(ds[[0, 1, 5, 6]], d0[[0, 1, 5, 6]] / scale, atol=1e-15, rtol=1e-13)
    np.testing.assert_allclose(
        ds[[2, 3, 7, 8]], d0[[2, 3, 7, 8]] / scale**2, atol=1e-15, rtol=1e-13
    )
    np.testing.assert_allclose(
        ds[[4, 9, 10, 11]], d0[[4, 9, 10, 11]] * scale**2, atol=1e-18, rtol=1e-13
    )


def test_trajectory_similarity_and_fixed_stiffness_contrast():
    reference = simulate()
    small = simulate(0.5)
    fixed = simulate(0.5, fixed_stiffness=True)
    good = comparison(small, reference)
    different = comparison(fixed, reference)
    assert max(map(max, good["coordinate_max_differences"])) < 1e-12
    assert max(map(max, different["coordinate_max_differences"])) > 1e-5
    for run in (small, fixed):
        assert run["max_total_residual_j"] < 1e-12
        assert run["max_connector_residual_j"] < 1e-12
        assert run["trace"][-1]["mechanical_j"][1] > 0


@pytest.mark.parametrize(
    "scale,ratio", [(0.25, 0.5), (0.5, 0.25), (True, 0.5), (1, False), (1, 1.1), (1, float("nan"))]
)
def test_invalid_absolute_or_relative_sizes(scale, ratio):
    with pytest.raises(ValueError):
        sizes(scale, ratio)


def test_invalid_refinement():
    with pytest.raises(ValueError):
        simulate(refinement=True)


@pytest.mark.parametrize("mismatch", ["scale", "grid", "ratio"])
def test_incompatible_similarity_reference_rejected(mismatch):
    run = {
        "settings": {"parent_scale": 0.5, "relative_size": 0.5},
        "trace": [{"reference_time_s": 0}],
    }
    reference = {
        "settings": {"parent_scale": 1.0, "relative_size": 0.5},
        "trace": [{"reference_time_s": 0}],
    }
    if mismatch == "scale":
        reference["settings"]["parent_scale"] = 0.5
    elif mismatch == "grid":
        reference["trace"][0]["reference_time_s"] = 0.01
    else:
        reference["settings"]["relative_size"] = 1.0
    with pytest.raises(ValueError):
        comparison(run, reference)
