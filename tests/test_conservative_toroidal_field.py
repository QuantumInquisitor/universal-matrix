import math

import numpy as np
import pytest

from src.conservative_toroidal_field import ToroidalContentCurrent


def gauss_integral(function, lower, upper, count=24):
    nodes, weights = np.polynomial.legendre.leggauss(count)
    points = (upper + lower) / 2 + (upper - lower) / 2 * nodes
    return (upper - lower) / 2 * sum(w * function(p) for p, w in zip(points, weights, strict=True))


@pytest.mark.parametrize("poloidal,toroidal", [(1, 0), (0, 1), (-2.3, 0.7)])
def test_actual_surface_integrals_recover_signed_cut_fluxes(poloidal, toroidal):
    field = ToroidalContentCurrent(2.1, 0.7, poloidal, toroidal)
    R, a = field.major_radius, field.minor_radius

    def cut(rho):
        return 2 * math.pi * rho * field.current((rho, 0, 0))[2]

    assert gauss_integral(cut, R, R + a) == pytest.approx(-poloidal, abs=1e-12)
    assert gauss_integral(cut, R - a, R) == pytest.approx(poloidal, abs=1e-12)
    # The phi=0 section has normal +y, area element s ds dtheta.
    disk = gauss_integral(
        lambda s: gauss_integral(
            lambda theta: s * field.current((R + s * math.cos(theta), 0, s * math.sin(theta)))[1],
            0,
            2 * math.pi,
        ),
        0,
        a,
    )
    assert disk == pytest.approx(toroidal, abs=1e-12)


def test_cartesian_divergence_converges_and_flow_stays_on_nested_tori():
    field = ToroidalContentCurrent(poloidal_flux=0.8, toroidal_flux=-0.6)
    points = [(2.1, 0.2, 0.17), (1.85, -0.3, -0.24), (0.6, 1.95, 0.12)]
    for point in points:
        errors = []
        for h in (1e-3, 5e-4, 2.5e-4):
            divergence = 0
            for axis in range(3):
                plus, minus = list(point), list(point)
                plus[axis] += h
                minus[axis] -= h
                divergence += (field.current(plus)[axis] - field.current(minus)[axis]) / (2 * h)
            errors.append(abs(divergence))
        assert errors[-1] < errors[0] / 10
        assert errors[-1] < 2e-5
        x, y, z = point
        rho = math.hypot(x, y)
        normal = ((rho - field.major_radius) * x / rho, (rho - field.major_radius) * y / rho, z)
        assert sum(
            a * b for a, b in zip(normal, field.current(point), strict=True)
        ) == pytest.approx(0, abs=1e-12)


def test_stream_function_generates_poloidal_components():
    field = ToroidalContentCurrent(toroidal_flux=0)
    rho, z, h = 2.15, 0.2, 1e-6
    d_z = (field.stream_function((rho, 0, z + h)) - field.stream_function((rho, 0, z - h))) / (
        2 * h
    )
    d_rho = (field.stream_function((rho + h, 0, z)) - field.stream_function((rho - h, 0, z))) / (
        2 * h
    )
    assert field.current((rho, 0, z)) == pytest.approx((-d_z / rho, 0, d_rho / rho), abs=1e-9)


def test_mirrors_are_vector_pushforwards_and_distinct_from_flow_reversal():
    field = ToroidalContentCurrent(poloidal_flux=0.7, toroidal_flux=-0.9)
    for point in [(2.1, 0.2, 0.1), (1.8, -0.1, -0.2)]:
        value = field.current(point)
        assert field.central_mirror().current(tuple(-v for v in point)) == pytest.approx(
            tuple(-v for v in value), abs=1e-12
        )
        assert field.axial_plane_mirror().current((point[0], -point[1], point[2])) == pytest.approx(
            (value[0], -value[1], value[2]), abs=1e-12
        )
        assert field.reverse_flow().current(point) == pytest.approx(
            tuple(-v for v in value), abs=1e-12
        )
    assert field.central_mirror().central_mirror() == field
    assert field.axial_plane_mirror().axial_plane_mirror() == field
    assert field.reverse_flow().reverse_flow() == field
    assert (
        field.central_mirror().axial_plane_mirror() == field.axial_plane_mirror().central_mirror()
    )


def test_support_boundary_axis_and_zero_current():
    field = ToroidalContentCurrent()
    for point in [(0, 0, 0), (0, 0, 100), (3, 0, 0), (2.5, 0, 0), (1.5, 0, 0), (2, 0, 0.5)]:
        assert field.current(point) == (0, 0, 0)
    assert ToroidalContentCurrent(poloidal_flux=0, toroidal_flux=0).current((2.1, 0, 0.1)) == (
        0,
        0,
        0,
    )
    # Quadratic cutoff makes the field and first derivative vanish at the boundary.
    values = [math.hypot(*field.current((2.5 - epsilon, 0, 0))) for epsilon in (1e-3, 5e-4)]
    assert values[1] / values[0] == pytest.approx(0.25, rel=0.01)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"minor_radius": 0},
        {"major_radius": 0.5, "minor_radius": 0.5},
        {"poloidal_flux": math.inf},
        {"toroidal_flux": math.nan},
    ],
)
def test_invalid_domain_or_flux_is_rejected(kwargs):
    with pytest.raises(ValueError):
        ToroidalContentCurrent(**kwargs)


def test_nonfinite_position_is_rejected():
    with pytest.raises(ValueError):
        ToroidalContentCurrent().current((math.nan, 0, 0))
