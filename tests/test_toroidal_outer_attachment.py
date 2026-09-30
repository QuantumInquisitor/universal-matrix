from dataclasses import replace

import pytest

from src.toroidal_aperture_attachment import build_aperture_attachment
from src.toroidal_bore_downstream import _interface, _jacobian
from src.toroidal_outer_attachment import build_candidate, check_b_port


@pytest.mark.parametrize("current", [1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0])
def test_outer_route_oriented_interfaces_and_jacobians(current):
    ref = build_aperture_attachment(current)
    parts = build_candidate(ref)
    report = check_b_port(ref, parts[0].geometry)
    assert report["maximum_relative_vector_residual"] < 1e-10
    for left, right in zip(parts, (*parts[1:], ref.aperture), strict=True):
        assert (
            _interface(left, right, ref.downstream.flux).sampled_relative_current_residual < 1e-10
        )
    assert min(_jacobian(p).determinant_lower_bound for p in parts) > 0
    assert report["signed_flux"] == ref.downstream.flux


@pytest.mark.parametrize("current", [1.0, -1.0, 2e-8, -2e-8])
def test_B_port_rejects_small_displacement_radius_flux_and_orientation_errors(current):
    ref = build_aperture_attachment(current)
    connector = build_candidate(ref)[0].geometry
    malformed = [
        replace(connector, origin=(connector.origin[0] + 1e-11, *connector.origin[1:])),
        replace(connector, axis_sign=-connector.axis_sign),
        replace(
            connector, transition=replace(connector.transition, source_outer_radius=1.5 + 1e-11)
        ),
        replace(
            connector, transition=replace(connector.transition, flux=-connector.transition.flux)
        ),
        replace(
            connector,
            transition=replace(connector.transition, flux=connector.transition.flux * 0.99),
        ),
    ]
    for candidate in malformed:
        with pytest.raises(ValueError):
            check_b_port(ref, candidate)
