from __future__ import annotations

import math

import numpy as np
import pytest

from src.conservative_toroidal_field import ToroidalContentCurrent
from src.toroidal_connector_topology import (
    ANNULAR_PORT,
    DISK_LIKE_PORT,
    AnnularPiolaConnector,
    CutOpenToroidalChannel,
    CutSide,
    nonsingular_sweep_compatible,
    rectangular_to_toroidal_cut_is_no_fit,
)


def gauss_integral(function, lower, upper, count=36):
    nodes, weights = np.polynomial.legendre.leggauss(count)
    points = (upper + lower) / 2 + (upper - lower) / 2 * nodes
    return (upper - lower) / 2 * sum(
        weight * function(point)
        for point, weight in zip(points, weights, strict=True)
    )


def test_rectangle_to_annulus_is_an_explicit_topology_no_fit():
    assert DISK_LIKE_PORT.boundary_components == 1
    assert ANNULAR_PORT.boundary_components == 2
    assert DISK_LIKE_PORT.first_betti_number == 0
    assert ANNULAR_PORT.first_betti_number == 1
    assert not nonsingular_sweep_compatible(DISK_LIKE_PORT, ANNULAR_PORT)
    assert nonsingular_sweep_compatible(ANNULAR_PORT, ANNULAR_PORT)
    assert rectangular_to_toroidal_cut_is_no_fit()


@pytest.mark.parametrize("flux", [1.7, -0.8, 0.0])
def test_cut_open_torus_has_two_annular_boundary_copies_with_opposite_flux(flux):
    cut = CutOpenToroidalChannel(
        ToroidalContentCurrent(
            major_radius=2.3,
            minor_radius=0.6,
            poloidal_flux=flux,
            toroidal_flux=0.0,
        )
    )
    assert cut.topology is ANNULAR_PORT
    assert cut.outward_flux(CutSide.INLET_COPY) == -flux
    assert cut.outward_flux(CutSide.OUTLET_COPY) == flux
    assert cut.outward_flux(CutSide.INLET_COPY) + cut.outward_flux(CutSide.OUTLET_COPY) == 0.0


@pytest.mark.parametrize("flux", [1.3, -0.9])
def test_connector_source_and_target_surface_fluxes_equal_graph_flux(flux):
    cut = CutOpenToroidalChannel(
        ToroidalContentCurrent(2.1, 0.5, flux, 0.0),
        center_z=4.0,
    )
    connector = AnnularPiolaConnector(cut, 0.7, 1.4, length=1.8)

    source_flux = 2 * math.pi * gauss_integral(
        lambda radius: radius * connector.source_normal_density(radius),
        connector.source_inner_radius,
        connector.source_outer_radius,
    )
    target_flux = 2 * math.pi * gauss_integral(
        lambda radius: radius * connector.current((radius, 0.0, connector.target_z))[2],
        cut.inner_radius,
        cut.outer_radius,
    )
    assert source_flux == pytest.approx(flux, abs=2e-12)
    assert target_flux == pytest.approx(flux, abs=2e-12)


def test_connector_matches_toroidal_field_pointwise_on_target_cut():
    cut = CutOpenToroidalChannel(ToroidalContentCurrent(2.4, 0.7, 1.1, 0.0), center_z=3.0)
    connector = AnnularPiolaConnector(cut, 0.8, 1.5, length=2.0)

    for q in (0.1, 0.25, 0.5, 0.75, 0.9):
        radius = cut.inner_radius + cut.field.minor_radius * q
        assert connector.target_vector_residual(radius) < 1e-12


def test_smoothstep_makes_connector_normal_to_both_interface_planes():
    cut = CutOpenToroidalChannel(ToroidalContentCurrent(2.0, 0.45, 0.8, 0.0))
    connector = AnnularPiolaConnector(cut, 0.6, 1.2, length=1.5)
    q = 0.43

    source = connector.map_point(0.0, q, 0.0)
    target = connector.map_point(1.0, q, 0.0)
    assert connector.current(source)[0] == pytest.approx(0.0, abs=1e-12)
    assert connector.current(target)[0] == pytest.approx(0.0, abs=1e-12)


def test_piola_connector_is_divergence_free_in_the_interior():
    cut = CutOpenToroidalChannel(ToroidalContentCurrent(2.2, 0.5, 0.9, 0.0), center_z=2.5)
    connector = AnnularPiolaConnector(cut, 0.75, 1.35, length=1.7)
    point = connector.map_point(0.47, 0.41, 0.37)

    errors = []
    for h in (2e-4, 1e-4, 5e-5):
        divergence = 0.0
        for axis in range(3):
            plus = list(point)
            minus = list(point)
            plus[axis] += h
            minus[axis] -= h
            divergence += (
                connector.current(tuple(plus))[axis] - connector.current(tuple(minus))[axis]
            ) / (2 * h)
        errors.append(abs(divergence))
    assert errors[-1] < 5e-7
    assert errors[-1] < errors[0] / 8


def test_connector_jacobian_remains_positive_everywhere_sampled():
    cut = CutOpenToroidalChannel(ToroidalContentCurrent(2.0, 0.4, 1.0, 0.0))
    connector = AnnularPiolaConnector(cut, 0.5, 1.1, length=1.3)
    assert min(
        connector.jacobian_determinant(s, q)
        for s in (0.0, 0.2, 0.5, 0.8, 1.0)
        for q in (0.0, 0.25, 0.5, 0.75, 1.0)
    ) > 0.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source_inner_radius": 0.0, "source_outer_radius": 1.0},
        {"source_inner_radius": 1.0, "source_outer_radius": 1.0},
        {"source_inner_radius": 1.0, "source_outer_radius": 1.5, "length": 0.0},
    ],
)
def test_invalid_annular_connector_geometry_is_rejected(kwargs):
    cut = CutOpenToroidalChannel(ToroidalContentCurrent(2.0, 0.4, 1.0, 0.0))
    with pytest.raises(ValueError):
        AnnularPiolaConnector(cut, **kwargs)


def test_nonzero_toroidal_swirl_requires_a_more_general_connector():
    cut = CutOpenToroidalChannel(ToroidalContentCurrent(2.0, 0.4, 1.0, 0.2))
    with pytest.raises(ValueError, match="purely poloidal"):
        AnnularPiolaConnector(cut, 0.5, 1.0)
