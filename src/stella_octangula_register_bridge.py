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

from .canonical_kernel import BOUNDARY_GATES, N_CORE, REGISTER_SIZE, register_address
from .seed_matrix_bridge import SPATIAL_AXES, assignment_gate_ids

Coordinate = tuple[int, int, int]
Frame = tuple[str, ...]

VERTEX_COUNT = 8


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


def core_state_vertex_pair(state: int) -> tuple[Coordinate, Coordinate]:
    """Project a canonical core state into its ordered stella-register pair."""
    if not isinstance(state, int):
        raise TypeError("state must be an integer")
    return register_vertex_pair(register_address(state % N_CORE))
