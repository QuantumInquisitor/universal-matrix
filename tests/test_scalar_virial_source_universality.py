import math

from src.scalar_virial_source_universality import (
    VirialSourceDiagnostic,
    active_geometry_source,
    difference_from_virial,
    potential_required_by_virial,
    source_energy_difference,
    total_energy,
    universal_source_ratio_on_virial_shell,
    virial_residual,
)


def test_source_energy_difference_is_minus_virial_residual():
    cases = [
        (1.0, 0.2, 0.8),
        (3.0, 1.1, 2.4),
        (0.7, 0.4, -0.1),
    ]
    for k, g, v in cases:
        assert math.isclose(
            source_energy_difference(k, g, v),
            difference_from_virial(k, g, v),
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_exact_virial_shell_has_universal_source_energy_ratio_one():
    for k, g in [
        (1.0, 0.1),
        (2.0, 0.7),
        (10.0, 3.0),
    ]:
        assert math.isclose(
            universal_source_ratio_on_virial_shell(k, g),
            1.0,
            rel_tol=0,
            abs_tol=1e-15,
        )


def test_constructed_virial_point_has_equal_active_source_and_energy():
    k = 2.4
    g = 0.9
    v = potential_required_by_virial(k, g)

    assert math.isclose(
        virial_residual(k, g, v),
        0.0,
        rel_tol=0,
        abs_tol=1e-15,
    )
    assert math.isclose(
        active_geometry_source(k, v),
        total_energy(k, g, v),
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_off_shell_source_mismatch_tracks_virial_violation():
    diagnostic = VirialSourceDiagnostic(
        time_kinetic=1.5,
        gradient=0.7,
        potential=1.0,
    )

    assert not math.isclose(
        diagnostic.virial_residual,
        0.0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        diagnostic.source_energy_difference,
        -diagnostic.virial_residual,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_free_rest_uniform_limit_is_special_zero_gradient_case():
    k = 1.3
    g = 0.0
    v = potential_required_by_virial(k, g)
    assert v == k
    assert active_geometry_source(k, v) == total_energy(k, g, v)
