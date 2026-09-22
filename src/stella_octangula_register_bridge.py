"""Exact stella-octangula bridge for the 64-address projection register.

The regular star tetrahedron is represented by the eight vertices of a cube,
partitioned by coordinate-product parity into two regular tetrahedra.  Their
edge midpoints are the six vertices of the central octahedron and therefore
provide an exact coordinate model for the six canonical boundary gates.

Ordered pairs of the eight outer vertices provide 8 x 8 = 64 register
addresses.  These identities are geometric and combinatorial.  They do not by
themselves establish light, sound, elemental, nuclear, or cosmological claims.
"""

from __future__ import annotations

from itertools import combinations
from math import atan2, sqrt

from .canonical_kernel import BOUNDARY_GATES, N_CORE, REGISTER_SIZE, register_address
from .seed_matrix_bridge import SPATIAL_AXES, assignment_gate_ids

Coordinate = tuple[int, int, int]
Frame = tuple[str, ...]
ProjectionCoordinate = tuple[float, float]

VERTEX_COUNT = 8
CENTRAL_MIRROR_FRAME: Frame = (
    "X_NEG",
    "Y_NEG",
    "Z_NEG",
    "X_POS",
    "Y_POS",
    "Z_POS",
)


def vertex_from_index(index: int) -> Coordinate:
    """Decode a three-bit index as a cube vertex with coordinates in {-1, +1}."""
    if index not in range(VERTEX_COUNT):
        raise ValueError("vertex index must be in 0..7")
    return tuple(1 if index & (1 << (2 - axis)) else -1 for axis in range(3))


STELLA_VERTICES = tuple(vertex_from_index(index) for index in range(VERTEX_COUNT))

if REGISTER_SIZE != VERTEX_COUNT**2:
    raise RuntimeError("the stella bridge requires an 8 x 8 register")


def vertex_index(vertex: Coordinate) -> int:
    """Encode one cube vertex as its canonical three-bit index."""
    if len(vertex) != 3 or any(component not in (-1, 1) for component in vertex):
        raise ValueError("a stella vertex must have three coordinates in {-1, +1}")
    return sum((component == 1) << (2 - axis) for axis, component in enumerate(vertex))


def tetrahedron_parity(vertex: Coordinate) -> int:
    """Return the coordinate-product parity selecting one of the two tetrahedra."""
    vertex_index(vertex)
    return vertex[0] * vertex[1] * vertex[2]


def tetrahedron_vertices(parity: int) -> tuple[Coordinate, ...]:
    """Return the four vertices of one regular tetrahedron in the compound."""
    if parity not in (-1, 1):
        raise ValueError("tetrahedron parity must be -1 or +1")
    return tuple(vertex for vertex in STELLA_VERTICES if tetrahedron_parity(vertex) == parity)


def tetrahedron_edges(parity: int) -> tuple[tuple[Coordinate, Coordinate], ...]:
    """Return the six undirected edges of one regular tetrahedron."""
    return tuple(combinations(tetrahedron_vertices(parity), 2))


def central_octahedron_vertices(parity: int) -> tuple[Coordinate, ...]:
    """Return the six edge midpoints forming the compound's central octahedron."""
    midpoints = {
        tuple((left[axis] + right[axis]) // 2 for axis in range(3))
        for left, right in tetrahedron_edges(parity)
    }
    return tuple(sorted(midpoints))


def gate_coordinate(label: str) -> Coordinate:
    """Return the axial central-octahedron vertex for one boundary gate."""
    if label not in BOUNDARY_GATES:
        raise ValueError(f"unknown boundary gate: {label}")
    axis_name, direction = label.split("_", maxsplit=1)
    coordinate = [0, 0, 0]
    coordinate[SPATIAL_AXES.index(axis_name)] = 1 if direction == "POS" else -1
    return tuple(coordinate)


def central_mirror_coordinate(coordinate: Coordinate) -> Coordinate:
    """Apply the point reflection through the shared center of the compound."""
    if len(coordinate) != 3:
        raise ValueError("coordinate must have exactly three components")
    return tuple(-component for component in coordinate)


def central_mirror_vertex(vertex: Coordinate) -> Coordinate:
    """Return the antipodal stella vertex under the central mirror."""
    vertex_index(vertex)
    mirrored = central_mirror_coordinate(vertex)
    vertex_index(mirrored)
    return mirrored


def central_mirror_gate(label: str) -> str:
    """Return the boundary gate opposite ``label`` through the center."""
    mirrored = central_mirror_coordinate(gate_coordinate(label))
    return next(candidate for candidate in BOUNDARY_GATES if gate_coordinate(candidate) == mirrored)


def transform_coordinate(coordinate: Coordinate, assignment: Frame) -> Coordinate:
    """Apply one validated signed axis frame to an integer coordinate."""
    if len(coordinate) != 3:
        raise ValueError("coordinate must have exactly three components")
    assignment_gate_ids(assignment)
    transformed = [0, 0, 0]
    for local_axis, label in enumerate(assignment[:3]):
        axis_name, direction = label.split("_", maxsplit=1)
        world_axis = SPATIAL_AXES.index(axis_name)
        sign = 1 if direction == "POS" else -1
        transformed[world_axis] = sign * coordinate[local_axis]
    return tuple(transformed)


def transform_vertex(vertex: Coordinate, assignment: Frame) -> Coordinate:
    """Apply a signed frame to a stella vertex and return another stella vertex."""
    vertex_index(vertex)
    transformed = transform_coordinate(vertex, assignment)
    vertex_index(transformed)
    return transformed


def register_vertex_pair(address: int) -> tuple[Coordinate, Coordinate]:
    """Decode one 64-register address as an ordered pair of eight-state vertices."""
    if address not in range(REGISTER_SIZE):
        raise ValueError(f"register address must be in 0..{REGISTER_SIZE - 1}")
    first, second = divmod(address, VERTEX_COUNT)
    return vertex_from_index(first), vertex_from_index(second)


def vertex_pair_address(first: Coordinate, second: Coordinate) -> int:
    """Encode an ordered pair of stella vertices as one 64-register address."""
    return VERTEX_COUNT * vertex_index(first) + vertex_index(second)


def central_mirror_register_address(address: int) -> int:
    """Mirror both stella vertices carried by one register address."""
    first, second = register_vertex_pair(address)
    return vertex_pair_address(
        central_mirror_vertex(first),
        central_mirror_vertex(second),
    )


def relative_signature(address: int) -> Coordinate:
    """Return component agreement (+1) or disagreement (-1) for a vertex pair."""
    first, second = register_vertex_pair(address)
    return tuple(first[axis] * second[axis] for axis in range(3))


def pair_hamming_distance(address: int) -> int:
    """Count the axes on which the ordered vertex pair differs."""
    return relative_signature(address).count(-1)


def register_distance_shell_counts() -> tuple[int, int, int, int]:
    """Count the 64 ordered pairs by cube-vertex Hamming distance 0 through 3."""
    counts = [0, 0, 0, 0]
    for address in range(REGISTER_SIZE):
        counts[pair_hamming_distance(address)] += 1
    return tuple(counts)


def register_frame_permutation(assignment: Frame) -> tuple[int, ...]:
    """Return the 64-address permutation induced by one signed spatial frame."""
    assignment_gate_ids(assignment)
    transformed = []
    for address in range(REGISTER_SIZE):
        first, second = register_vertex_pair(address)
        transformed.append(
            vertex_pair_address(
                transform_vertex(first, assignment),
                transform_vertex(second, assignment),
            )
        )
    return tuple(transformed)


def body_diagonal_projection(coordinate: Coordinate) -> ProjectionCoordinate:
    """Orthographically project onto the plane normal to the (1, 1, 1) axis.

    The returned coordinates use the orthonormal in-plane basis
    ``(1, -1, 0) / sqrt(2)`` and ``(1, 1, -2) / sqrt(6)``.
    """
    if len(coordinate) != 3:
        raise ValueError("coordinate must have exactly three components")
    x, y, z = coordinate
    return (x - y) / sqrt(2), (x + y - 2 * z) / sqrt(6)


def seed_shadow_centers() -> tuple[ProjectionCoordinate, ...]:
    """Return the normalized center-plus-hexagon projection of the stella tips.

    The two tips on the body diagonal project to the same center.  The other
    six tips form a regular hexagon; its radius is normalized to one.
    """
    axial_tips = {(-1, -1, -1), (1, 1, 1)}
    outer_radius = sqrt(8 / 3)
    ring = [
        tuple(component / outer_radius for component in body_diagonal_projection(vertex))
        for vertex in STELLA_VERTICES
        if vertex not in axial_tips
    ]
    ring.sort(key=lambda point: atan2(point[1], point[0]))
    return ((0.0, 0.0), *ring)


def core_state_vertex_pair(state: int) -> tuple[Coordinate, Coordinate]:
    """Project a canonical core state into its ordered stella-register pair."""
    if not isinstance(state, int):
        raise TypeError("state must be an integer")
    return register_vertex_pair(register_address(state % N_CORE))
