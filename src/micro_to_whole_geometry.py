"""Exact micro-to-whole construction graph for the finite geometry engine.

The graph begins with the shared center and six axial boundary gates.  From
those gates it builds the stella octangula and the 4D 16-cell, lifts the
16-cell into the tesseract, and joins the radius-matched 16-cell and tesseract
as the 24-cell.  A projection branch recovers the seven Seed centers.

"Micro-to-whole" describes exact construction dependencies, not measured
physical size.  The module does not identify any layer with a literal
cosmological universe or assign a physical meaning to the fourth coordinate.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product

from .canonical_kernel import BOUNDARY_GATES
from .four_dimensional_polytope_bridge import (
    CROSS_POLYTOPE_VERTICES,
    TESSERACT_VERTICES,
    drop_w,
    seed_projection_centers_4d,
    sixteen_cell_vertices_from_gates,
    tesseract_vertices_from_gates,
)
from .stella_octangula_register_bridge import STELLA_VERTICES, gate_coordinate
from .twenty_four_cell_bridge import (
    TWENTY_FOUR_CELL_VERTICES,
    projected_xyz_multiplicities,
    twenty_four_cell_vertices_from_tetrahedron,
)

Scalar = int | float
Coordinate = tuple[Scalar, ...]
Coordinate3D = tuple[int, int, int]


@dataclass(frozen=True)
class GeometryLayer:
    """One finite coordinate layer in the construction graph."""

    name: str
    ambient_dimension: int
    coordinates: tuple[Coordinate, ...]


@dataclass(frozen=True)
class ConstructionRoute:
    """One exact directed construction between named geometry layers."""

    sources: tuple[str, ...]
    target: str
    operation: str


CONSTRUCTION_ROUTES = (
    ConstructionRoute(("boundary_gates",), "stella_octangula", "one signed gate per axis"),
    ConstructionRoute(("boundary_gates",), "sixteen_cell", "ordered Clifford gate products"),
    ConstructionRoute(("sixteen_cell",), "seed_centers", "XYZ and body-diagonal projection"),
    ConstructionRoute(("sixteen_cell",), "tesseract", "both parity lifts"),
    ConstructionRoute(("stella_octangula",), "twenty_four_cell", "edge-root spinor products"),
    ConstructionRoute(
        ("sixteen_cell", "tesseract"),
        "twenty_four_cell",
        "common-radius union",
    ),
)


def boundary_gate_coordinates() -> tuple[Coordinate3D, ...]:
    """Return the six axial gate vectors in canonical sorted order."""
    return tuple(sorted(gate_coordinate(label) for label in BOUNDARY_GATES))


def stella_vertices_from_gates() -> tuple[Coordinate3D, ...]:
    """Build the eight stella vertices by choosing one gate on every axis."""
    gates = boundary_gate_coordinates()
    axis_pairs = tuple(tuple(gate for gate in gates if gate[axis] != 0) for axis in range(3))
    vertices = {
        tuple(sum(gate[component] for gate in selection) for component in range(3))
        for selection in product(*axis_pairs)
    }
    return tuple(sorted(vertices))


def micro_to_whole_layers() -> tuple[GeometryLayer, ...]:
    """Build every exact layer used by the finite micro-to-whole graph."""
    seed_centers = seed_projection_centers_4d()
    return (
        GeometryLayer("port_center", 2, (seed_centers[0],)),
        GeometryLayer("boundary_gates", 3, boundary_gate_coordinates()),
        GeometryLayer("seed_centers", 2, seed_centers),
        GeometryLayer("stella_octangula", 3, stella_vertices_from_gates()),
        GeometryLayer("sixteen_cell", 4, sixteen_cell_vertices_from_gates()),
        GeometryLayer("tesseract", 4, tesseract_vertices_from_gates()),
        GeometryLayer(
            "twenty_four_cell",
            4,
            twenty_four_cell_vertices_from_tetrahedron(1),
        ),
    )


def layer_by_name(name: str) -> GeometryLayer:
    """Return one named layer from a newly verified construction graph."""
    try:
        return next(layer for layer in micro_to_whole_layers() if layer.name == name)
    except StopIteration as error:
        raise ValueError(f"unknown geometry layer: {name}") from error


def central_mirror(coordinate: Coordinate) -> Coordinate:
    """Reflect a coordinate of any supported dimension through its origin."""
    return tuple(-component for component in coordinate)


def centrally_symmetric_layer_names() -> tuple[str, ...]:
    """Return the layers whose coordinate sets are closed under point mirror."""
    return tuple(
        layer.name
        for layer in micro_to_whole_layers()
        if {central_mirror(point) for point in layer.coordinates} == set(layer.coordinates)
    )


def downward_xyz_multiplicities() -> tuple[tuple[str, tuple[tuple[Coordinate3D, int], ...]], ...]:
    """Recover exact XYZ shadows of all three 4D vertex layers."""
    sixteen_counts = Counter(drop_w(vertex) for vertex in CROSS_POLYTOPE_VERTICES)
    tesseract_counts = Counter(drop_w(vertex) for vertex in TESSERACT_VERTICES)
    return (
        ("sixteen_cell", tuple(sorted(sixteen_counts.items()))),
        ("tesseract", tuple(sorted(tesseract_counts.items()))),
        ("twenty_four_cell", projected_xyz_multiplicities()),
    )


if stella_vertices_from_gates() != tuple(sorted(STELLA_VERTICES)):
    raise RuntimeError("the six gates must generate the complete stella vertex set")
if set(sixteen_cell_vertices_from_gates()) != set(CROSS_POLYTOPE_VERTICES):
    raise RuntimeError("the six gates must generate the complete 16-cell")
if set(tesseract_vertices_from_gates()) != set(TESSERACT_VERTICES):
    raise RuntimeError("the two parity lifts must generate the complete tesseract")
if set(twenty_four_cell_vertices_from_tetrahedron(1)) != set(TWENTY_FOUR_CELL_VERTICES):
    raise RuntimeError("the stella edge roots must generate the complete 24-cell")
