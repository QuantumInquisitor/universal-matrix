"""Complete fixed static inventory with two modified hosts and replacement edge 2.

Analytic geometry bounds are evaluated in floating point. No moving assembly,
material law, globally sampled field, or interval-arithmetic claim is made.
"""

import math
from collections import Counter
from dataclasses import asdict
from itertools import combinations

import numpy as np

from .toroidal_aperture_attachment import audit_aperture_attachment, build_aperture_attachment
from .toroidal_aperture_fanout import SecondAperture
from .toroidal_aperture_fanout import build_candidate as build_replacement
from .toroidal_aperture_fanout import run as audit_replacement
from .toroidal_bore_downstream import _bounds, _cap, _classify_pair, _field, _interface
from .toroidal_outer_attachment import build_candidate as build_outer
from .toroidal_outer_attachment import run as audit_outer
from .toroidal_shared_return_connectors import _connect_edge


def combined_components(reference):
    """Return enclosing geometry; host cuts are defined by the aperture domains.

    This tuple alone must not be rendered or sampled as the modified assembly.
    """
    components = (
        *(c for c in reference.retained if not c.name.startswith("edge2_")),
        *reference.downstream.components,
        reference.aperture,
        *reference.added,
        *build_outer(reference),
        *build_replacement(reference),
    )
    names = [c.name for c in components]
    if len(names) != 69 or len(set(names)) != len(names):
        raise ValueError("combined reference requires 69 unique component identities")
    return components


def check_junction_port(junction, connector, edge_index, source):
    """Exact face/support-plane geometry plus independent sampled field match."""
    port = junction.junction.port_by_edge(edge_index)
    center, axis, inner, outer = _cap(connector, source)
    normal = (0.0, 0.0, -1.0 if port.face.value == "lower" else 1.0)
    expected_axis = normal if source else tuple(-v for v in normal)
    expected_flux = port.outward_flux if source else -port.outward_flux
    face_z = junction.center[2] + normal[2] * junction.junction.length / 2
    lo, hi = _bounds(connector)
    support = lo[2] >= face_z if normal[2] > 0 else hi[2] <= face_z
    if (
        center != junction.port_axis_point(edge_index)
        or center[2] != face_z
        or axis != expected_axis
        or (inner, outer) != (port.inner_radius, port.outer_radius)
        or connector.transition.flux != expected_flux
        or connector.transition.length <= 0
        or not support
    ):
        raise ValueError(
            "connector does not match exact port, signed flux and exterior support plane"
        )
    residual = 0.0
    for q in (0.13, 0.47, 0.82):
        for theta in (0.2, 1.1, 2.7, 4.8):
            radius = inner + q * (outer - inner)
            p = (
                center[0] + radius * math.cos(theta),
                center[1] + radius * math.sin(theta),
                center[2],
            )
            a, b = np.asarray(connector.current(p)), np.asarray(_field(junction, p, expected_flux))
            if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
                raise ValueError("port vector-current profiles must be finite")
            residual = max(residual, float(np.max(np.abs(a - b))) / abs(expected_flux))
    if not math.isfinite(residual) or residual > 1e-10:
        raise ValueError("port vector-current profiles do not match")
    return {
        "junction": junction.node,
        "edge": edge_index,
        "source": source,
        "center": center,
        "outward_normal": normal,
        "outward_flux": port.outward_flux,
        "relative_vector_residual": residual,
        "support_plane_checked": True,
    }


def audit_combined_aperture(current=1.0):
    ref = build_aperture_attachment(current)
    current = ref.downstream.current
    patch = SecondAperture(ref)
    components = combined_components(ref)
    by_name = {c.name: c for c in components}
    inner = audit_aperture_attachment(ref)
    outer = audit_outer(current)
    replacement = audit_replacement(current)
    if not outer["candidate_accepted"] or not replacement["certified"]:
        raise ValueError("a prerequisite changed-component audit failed")
    # These fixed builders share the same current and reference geometry. Prior
    # separation certificates survive subtraction of material in either host.
    certificates = {}
    for provenance, rows in (
        ("inner_attachment", inner["inner_pairs"]),
        ("first_aperture", inner["aperture_pairs"]),
        ("outer_attachment", outer["pairs"]),
        ("replacement_route", replacement["checks"]),
    ):
        for row in rows:
            if row["method"] != "unresolved":
                certificates[frozenset((row["left"], row["right"]))] = {
                    **row,
                    "provenance": provenance,
                }
    certificates[frozenset((ref.host_name, ref.aperture.name))] = {
        "method": "modified_host_aperture_bound",
        "contact": "none",
        "bound": ref.access.clearance_bound(),
        "provenance": "first_modified_host",
    }

    chains = {
        0: [*build_outer(ref), ref.aperture, *ref.added, *ref.downstream.components],
        2: build_replacement(ref),
    }
    for edge in (1, 3):
        chains[edge] = [by_name[f"edge{edge}_inlet"]]
        chains[edge] += sorted(
            (c for c in components if c.name.startswith(f"edge{edge}_piece_")), key=lambda c: c.name
        )
        chains[edge].append(by_name[f"edge{edge}_outlet"])
    ids = [c.name for chain in chains.values() for c in chain]
    expected_ids = {c.name for c in components if not c.name.startswith("junction_")}
    if len(ids) != len(set(ids)) or set(ids) != expected_ids:
        raise ValueError("each material conduit must belong to exactly one directed route")

    ports, interfaces = [], []
    for edge_index, chain in sorted(chains.items()):
        edge = ref.downstream.routing.edges[edge_index].route.edge
        flux = _connect_edge(ref.downstream.routing.edges[edge_index]).flux
        interfaces.extend(
            asdict(_interface(a, b, flux)) for a, b in zip(chain, chain[1:], strict=False)
        )
        for component, node, source in (
            (chain[0], edge.source, True),
            (chain[-1], edge.target, False),
        ):
            junction = ref.downstream.routing.global_routing.junction(node)
            result = check_junction_port(junction, component.geometry, edge_index, source)
            result["component"] = component.name
            ports.append(result)
            certificates[frozenset((component.name, f"junction_{node}"))] = {
                "method": "exact_port_support_plane",
                "contact": "declared_junction_port",
                "bound": 0.0,
                "provenance": "combined_port_audit",
            }
    expected_ports = {
        (j.node, p.edge_index)
        for j in ref.downstream.routing.global_routing.junctions
        for p in j.junction.ports
    }
    actual_ports = {(p["junction"], p["edge"]) for p in ports}
    if len(ports) != len(actual_ports) or actual_ports != expected_ports:
        raise ValueError("junction port inventory is incomplete or duplicated")
    balances = {
        j.node: math.fsum(p["outward_flux"] for p in ports if p["junction"] == j.node)
        for j in ref.downstream.routing.global_routing.junctions
    }
    if any(abs(v) / abs(current) > 1e-12 for v in balances.values()):
        raise ValueError("junction signed flux does not balance")

    rows = []
    for left, right in combinations(components, 2):
        row = asdict(_classify_pair(left, right))
        row["provenance"] = "generic_enclosing_geometry"
        if row["method"] == "unresolved":
            proof = certificates.get(frozenset((left.name, right.name)))
            if proof is not None:
                row.update({k: v for k, v in proof.items() if k not in ("left", "right")})
        rows.append(row)
    count = len(components) * (len(components) - 1) // 2
    if len(rows) != count or len({frozenset((r["left"], r["right"])) for r in rows}) != count:
        raise ValueError("whole-state pair enumeration is incomplete or duplicated")
    unresolved = [r for r in rows if r["method"] == "unresolved"]
    return {
        "current": current,
        "component_count": len(components),
        "pair_count": count,
        "components": [c.name for c in components],
        "removed_component_ids": [c.name for c in ref.retained if c.name.startswith("edge2_")],
        "modified_hosts": [ref.host_name, patch.host.name],
        "routes": {str(i): [c.name for c in chain] for i, chain in chains.items()},
        "pairs": rows,
        "methods": dict(Counter(r["method"] for r in rows)),
        "unresolved": unresolved,
        "ports": ports,
        "interfaces": interfaces,
        "junction_flux_balances": balances,
        "pair_inventory_complete": True,
        "static_pair_clearance_complete": not unresolved,
        "all_declared_ports_attached": True,
        "motion_certified": False,
        "material_dynamics_validated": False,
        "scope": "Fixed static floating-point geometric bounds and sampled current matching; not formal interval or physical validation",
    }
