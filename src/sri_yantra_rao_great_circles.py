"""Audited Rao spherical root triangles and their projected chamber complex.

Rao's printed Table 1 parameters are preserved in the reference module. Here
they seed a six-equation refinement before incidence is computed. Equation
2.22 is geometrically inconsistent as printed: the P4-to-P7 denominator is
sin(d+g), not sin(r+c). Both values remain inspectable in this result.

The gnomonic chart is used only on the open northern hemisphere. It maps
great-circle arcs to straight segments, so the complete chamber extraction
can use the independent planar arrangement algorithm without chord sampling.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

from .sri_yantra_chambers import ChamberComplex, extract_chambers
from .sri_yantra_rao_spherical_reference import (
    RAO_TABLE1_REFERENCE_PARAMETERS,
    RaoSphericalDerived,
    RaoSphericalParameters,
    derive_rao_spherical,
    selected_constraint_residuals,
)

type Point3D = tuple[float, float, float]
type Triangle3D = tuple[Point3D, Point3D, Point3D]


@lru_cache(maxsize=1)
def refine_rao_reference() -> RaoSphericalDerived:
    """Refine only the published reference row; requires the scientific extra."""
    from scipy.optimize import root

    names = ("b", "c", "d", "e", "g", "h")
    initial = tuple(getattr(RAO_TABLE1_REFERENCE_PARAMETERS, name) for name in names)

    def residual(values):
        return selected_constraint_residuals(
            derive_rao_spherical(RaoSphericalParameters(*values))
        ).values

    solved = root(residual, initial, tol=1e-11)
    if not solved.success:
        raise RuntimeError(f"Rao reference refinement failed: {solved.message}")
    derived = derive_rao_spherical(RaoSphericalParameters(*solved.x))
    if selected_constraint_residuals(derived).maximum_absolute > 1e-12:
        raise RuntimeError("refined spherical constraints do not close")
    if any(abs(a - b) > 5e-7 for a, b in zip(initial, solved.x, strict=True)):
        raise RuntimeError("refinement left the published six-decimal rounding intervals")
    return derived


def spherical_axis_point(latitude: float, transverse_arc: float = 0.0) -> Point3D:
    """Point reached by a perpendicular great-circle arc from the symmetry axis."""
    if not all(math.isfinite(value) for value in (latitude, transverse_arc)):
        raise ValueError("spherical angles must be finite")
    return (
        math.sin(transverse_arc),
        math.cos(transverse_arc) * math.sin(latitude),
        math.cos(transverse_arc) * math.cos(latitude),
    )


def gnomonic_project(point: Point3D) -> tuple[float, float]:
    if not all(math.isfinite(value) for value in point):
        raise ValueError("sphere coordinates must be finite")
    if abs(math.hypot(*point) - 1.0) > 1e-11 or point[2] <= 1e-12:
        raise ValueError("point must lie on the open northern unit hemisphere")
    return point[0] / point[2], point[1] / point[2]


def gnomonic_lift(point: tuple[float, float]) -> Point3D:
    x, y = point
    if not math.isfinite(x) or not math.isfinite(y):
        raise ValueError("planar coordinates must be finite")
    norm = math.hypot(x, y, 1.0)
    return x / norm, y / norm, 1.0 / norm


def corrected_x16(derived: RaoSphericalDerived) -> float:
    """Use the shared P4 vertex and the arc P4P7=d+g in Figure 2.2."""
    p = derived.parameters
    return math.atan(math.sin(p.d + p.e + p.g) / math.sin(p.d + p.g) * math.tan(derived.x6))


def great_circle_residual(a: Point3D, b: Point3D, point: Point3D) -> float:
    """Absolute signed-plane residual, normalized by the great-circle normal."""
    normal = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    norm = math.hypot(*normal)
    if norm <= 1e-12:
        raise ValueError("great-circle endpoints are coincident or antipodal")
    return abs(sum(x * y for x, y in zip(normal, point, strict=True))) / norm


@dataclass(frozen=True)
class RaoGreatCircleComplex:
    derived: RaoSphericalDerived
    # Index order agrees with Chiodo: descending base latitude, t1 through t9.
    root_triangles: tuple[Triangle3D, ...]
    projected: ChamberComplex
    spherical_nodes: tuple[Point3D, ...]
    printed_x16_line_residual: float
    corrected_x16_line_residual: float


def derive_rao_great_circle_complex() -> RaoGreatCircleComplex:
    derived = refine_rao_reference()
    p = derived.parameters
    axis = (
        -p.r,
        -(p.b + p.c),
        -(p.c + derived.v9),
        -p.c,
        -p.g,
        p.d - derived.u7,
        p.d - derived.v12,
        p.d,
        p.d + derived.v8,
        p.d + p.e,
        p.r,
    )
    specifications = (
        (9, 4, corrected_x16(derived)),
        (8, 1, derived.x18),
        (7, 0, derived.x2),
        (6, 2, derived.x13),
        (5, 3, derived.x14),
        (4, 8, derived.x10),
        (3, 10, derived.x1),
        (2, 9, derived.x19),
        (1, 7, derived.x17),
    )
    triangles = tuple(
        (
            spherical_axis_point(axis[apex]),
            spherical_axis_point(axis[base], width),
            spherical_axis_point(axis[base], -width),
        )
        for base, apex, width in specifications
    )
    projected = extract_chambers(tuple(tuple(gnomonic_project(v) for v in t) for t in triangles))
    p4 = spherical_axis_point(axis[4])
    point6 = spherical_axis_point(axis[7], derived.x6)
    printed = great_circle_residual(p4, point6, spherical_axis_point(axis[9], derived.x16))
    corrected = great_circle_residual(p4, point6, triangles[0][1])
    if corrected > 1e-12:
        raise RuntimeError("corrected point 16 does not lie on its defining great circle")
    return RaoGreatCircleComplex(
        derived,
        triangles,
        projected,
        tuple(gnomonic_lift(v) for v in projected.vertices),
        printed,
        corrected,
    )


def parent_edge_signatures(triangles, geometry: ChamberComplex, tolerance: float = 1e-9):
    """Label each arrangement vertex by all original finite edges containing it.

    Matching these signatures provides a correspondence independent of vertex
    numbering, Euclidean distances between unrelated realizations, and counts.
    """
    segments = tuple(
        (index, edge, a, b)
        for index, triangle in enumerate(triangles)
        for edge, (a, b) in enumerate(zip(triangle, triangle[1:] + triangle[:1], strict=True))
    )
    result = []
    for x, y in geometry.vertices:
        incident = set()
        for index, edge, a, b in segments:
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            distance = abs(dx * (y - a[1]) - dy * (x - a[0])) / length
            parameter = ((x - a[0]) * dx + (y - a[1]) * dy) / length**2
            if distance <= tolerance and -tolerance / length <= parameter <= 1 + tolerance / length:
                incident.add((index, edge))
        result.append(frozenset(incident))
    return tuple(result)


def huet_vertex_correspondence(result: RaoGreatCircleComplex) -> tuple[int, ...]:
    """Verify and return the parent-edge-labelled isomorphism to the Huet graph."""
    from .sri_yantra_huet_planar import HUET_PLANAR_SOLUTION

    huet = extract_chambers()
    reference_signatures = parent_edge_signatures(
        tuple(t.vertices for t in HUET_PLANAR_SOLUTION.triangles), huet
    )
    spherical_signatures = parent_edge_signatures(
        tuple(tuple(gnomonic_project(v) for v in t) for t in result.root_triangles),
        result.projected,
    )
    lookup = {signature: i for i, signature in enumerate(reference_signatures)}
    if (
        len(lookup) != len(reference_signatures)
        or len(set(spherical_signatures)) != len(spherical_signatures)
        or set(spherical_signatures) != set(reference_signatures)
    ):
        raise ValueError("parent-edge incidence signatures do not define a bijection")
    mapping = tuple(lookup[signature] for signature in spherical_signatures)
    mapped_edges = {tuple(sorted((mapping[a], mapping[b]))) for a, b in result.projected.edges}
    mapped_faces = {frozenset(mapping[v] for v in f.boundary) for f in result.projected.faces}
    if mapped_edges != set(huet.edges) or mapped_faces != {
        frozenset(f.boundary) for f in huet.faces
    }:
        raise ValueError("atomic edge or face incidence differs from the Huet complex")
    mapped_rings = tuple(
        {frozenset(mapping[v] for v in result.projected.faces[i].corners) for i in ring}
        for ring in result.projected.rings
    )
    huet_rings = tuple({frozenset(huet.faces[i].corners) for i in ring} for ring in huet.rings)
    if mapped_rings != huet_rings:
        raise ValueError("selected chamber circuits differ from the Huet complex")
    return mapping


if __name__ == "__main__":
    result = derive_rao_great_circle_complex()
    print(
        "Refined constraint residual:",
        selected_constraint_residuals(result.derived).maximum_absolute,
    )
    print(
        "Point 16 line residual, printed/corrected:",
        result.printed_x16_line_residual,
        result.corrected_x16_line_residual,
    )
    print("Chamber count:", len(result.projected.chamber_ids))
    print(
        "Outer-to-inner circuits:",
        tuple(len(result.projected.ring_cycle(r)) for r in result.projected.rings),
    )
    print("Huet incidence correspondence:", len(huet_vertex_correspondence(result)), "vertices")
