import numpy as np

from src.weyl_measure_stokes import (
    curvature_flux,
    normalized_stokes_residual,
    rectangular_holonomy_phase,
    shrinking_loop_diagnostics,
    stokes_phase_residual,
)


def _background(seed=2301):
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(seed)
    links = rng.normal(
        scale=0.008,
        size=(4,) + shape,
    )
    direction_a = rng.normal(
        scale=0.12,
        size=(4,) + shape,
    )
    direction_b = rng.normal(
        scale=0.12,
        size=(4,) + shape,
    )
    return links, direction_a, direction_b


def test_curvature_flux_reverses_when_directions_are_swapped():
    links, da, db = _background(2302)
    flux_ab = curvature_flux(
        links,
        da,
        db,
        0.01,
        0.015,
        derivative_epsilon=2e-5,
    )
    flux_ba = curvature_flux(
        links,
        db,
        da,
        0.015,
        0.01,
        derivative_epsilon=2e-5,
    )
    assert abs(flux_ab + flux_ba) < 1e-9


def test_rectangular_holonomy_reverses_with_orientation():
    links, da, db = _background(2303)
    phase_ab = rectangular_holonomy_phase(
        links,
        da,
        db,
        0.01,
        0.012,
    )
    phase_ba = rectangular_holonomy_phase(
        links,
        db,
        da,
        0.012,
        0.01,
    )
    assert abs(phase_ab + phase_ba) < 2e-7


def test_small_loop_holonomy_matches_local_curvature_flux():
    links, da, db = _background(2304)
    side = 0.004

    phase = rectangular_holonomy_phase(
        links,
        da,
        db,
        side,
        side,
    )
    flux = curvature_flux(
        links,
        da,
        db,
        side,
        side,
        derivative_epsilon=2e-5,
    )

    # Both are O(area). The finite rectangle samples a changing projector, so
    # the agreement is asymptotic rather than exact at finite side length.
    assert abs(phase - flux) < 3e-6


def test_normalized_stokes_residual_is_small_for_tiny_loop():
    links, da, db = _background(2305)
    residual = normalized_stokes_residual(
        links,
        da,
        db,
        side_a=0.003,
        side_b=0.003,
        derivative_epsilon=2e-5,
    )
    assert abs(residual) < 0.08


def test_shrinking_loop_diagnostics_converge_toward_local_curvature():
    links, da, db = _background(2306)
    diagnostics = shrinking_loop_diagnostics(
        links,
        da,
        db,
        sizes=(0.012, 0.006, 0.003),
        derivative_epsilon=2e-5,
    )

    errors = [
        abs(item["residual_per_area"])
        for item in diagnostics
    ]

    # The smallest loop should be a better local-curvature approximation than
    # the largest one, allowing tiny floating fluctuations.
    assert errors[-1] <= errors[0] + 2e-3


def test_zero_area_is_rejected_for_normalized_residual():
    links, da, db = _background(2307)
    try:
        normalized_stokes_residual(
            links,
            da,
            db,
            side_a=0.0,
            side_b=0.01,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("zero-area rectangle should fail")


def test_stokes_residual_changes_sign_under_orientation_reversal():
    links, da, db = _background(2308)
    rab = stokes_phase_residual(
        links,
        da,
        db,
        0.005,
        0.007,
        derivative_epsilon=2e-5,
    )
    rba = stokes_phase_residual(
        links,
        db,
        da,
        0.007,
        0.005,
        derivative_epsilon=2e-5,
    )
    assert abs(rab + rba) < 3e-7
