from dataclasses import replace
from itertools import combinations

import pytest

from src.toroidal_aperture_attachment import build_aperture_attachment
from src.toroidal_combined_aperture import (
    audit_combined_aperture,
    check_junction_port,
    combined_components,
)


@pytest.mark.parametrize("current", [1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0])
def test_complete_inventory_and_connected_routes(current):
    result = audit_combined_aperture(current)
    names = result["components"]
    expected = {frozenset(p) for p in combinations(names, 2)}
    actual = [frozenset((p["left"], p["right"])) for p in result["pairs"]]
    assert len(names) == 69
    assert len(actual) == len(set(actual)) == 2346
    assert set(actual) == expected
    assert not result["unresolved"]
    assert result["static_pair_clearance_complete"]
    assert len(result["removed_component_ids"]) == 13
    assert not set(names).intersection(result["removed_component_ids"])
    assert set(result["modified_hosts"]) == {"edge3_piece_00", "edge3_piece_10"}
    routed = [n for route in result["routes"].values() for n in route]
    assert len(routed) == len(set(routed)) == 66
    assert set(routed) == set(names) - {"junction_A", "junction_B", "junction_C"}
    expected_interfaces = {
        (a, b)
        for route in result["routes"].values()
        for a, b in zip(route, route[1:], strict=False)
    }
    assert len(result["interfaces"]) == len(expected_interfaces) == 62
    assert {(p["left"], p["right"]) for p in result["interfaces"]} == expected_interfaces
    assert len(result["ports"]) == 8
    assert {(p["edge"], p["source"]) for p in result["ports"]} == {
        (edge, source) for edge in range(4) for source in (True, False)
    }
    assert max(abs(v / current) for v in result["junction_flux_balances"].values()) < 1e-12
    assert not result["motion_certified"]
    assert not result["material_dynamics_validated"]


@pytest.mark.parametrize("current", [1.0, -1.0, 2e-8, -2e-8])
@pytest.mark.parametrize("source", [True, False])
def test_retained_ports_reject_small_geometry_and_signed_flux_errors(current, source):
    ref = build_aperture_attachment(current)
    by_name = {c.name: c for c in combined_components(ref)}
    connector = by_name["edge1_inlet" if source else "edge1_outlet"].geometry
    edge = ref.downstream.routing.edges[1].route.edge
    junction = ref.downstream.routing.global_routing.junction(
        edge.source if source else edge.target
    )
    check_junction_port(junction, connector, 1, source)
    radius_name = "source_outer_radius" if source else "target_outer_radius"
    for bad in (
        replace(connector, origin=(connector.origin[0] + 1e-11, *connector.origin[1:])),
        replace(connector, axis_sign=-connector.axis_sign),
        replace(
            connector,
            transition=replace(
                connector.transition,
                **{radius_name: getattr(connector.transition, radius_name) + 1e-11},
            ),
        ),
        replace(
            connector, transition=replace(connector.transition, flux=-connector.transition.flux)
        ),
        replace(
            connector,
            transition=replace(connector.transition, flux=0.99 * connector.transition.flux),
        ),
    ):
        with pytest.raises(ValueError):
            check_junction_port(junction, bad, 1, source)


def test_nonfinite_port_field_is_rejected(monkeypatch):
    ref = build_aperture_attachment(1.0)
    connector = next(c.geometry for c in combined_components(ref) if c.name == "edge1_inlet")
    junction = ref.downstream.routing.global_routing.junction("C")
    monkeypatch.setattr(type(connector), "current", lambda self, point: (float("nan"), 0, 0))
    with pytest.raises(ValueError, match="finite"):
        check_junction_port(junction, connector, 1, True)
