"""Exact four-dimensional extension of the Seed, stella, and register geometry.

The 4-cube (tesseract) is represented by ``{-1, +1}^4``.  Product parity
partitions its 16 vertices into two demitesseracts, each a uniformly scaled
copy of a regular 16-cell.  Fixed-W slices recover the existing cube/stella
vertex set.

The canonical 16-cell has vertices ``(+/-1, 0, 0, 0)`` and permutations.
Dropping its W coordinate projects six vertices to the six boundary gates and
two opposite vertices to the shared center.  This is an exact geometric
extension; W has no physical interpretation in this contract.
"""

from __future__ import annotations

from functools import cache
from itertools import permutations, product
from math import atan2, prod, sqrt

from .canonical_kernel import BOUNDARY_GATES, REGISTER_SIZE
from .seed_matrix_bridge import SPATIAL_AXES, assignment_gate_ids
from .stella_octangula_register_bridge import (
    STELLA_VERTICES,
    Frame,
    body_diagonal_projection,
    gate_coordinate,
    register_vertex_pair,
    vertex_pair_address,
)

Coordinate3D = tuple[int, int, int]
Coordinate4D = tuple[int, int, int, int]
Frame4D = tuple[int, int, int, int]
ProjectionCoordinate = tuple[float, float]

TESSERACT_VERTEX_COUNT = 16
HYPER_REGISTER_SIZE = TESSERACT_VERTEX_COUNT**2
W_LAYERS = (-1, 1)

_HADAMARD_4 = (
    (1, 1, 1, 1),
    (1, 1, -1, -1),
    (1, -1, 1, -1),
    (1, -1, -1, 1),
)


def tesseract_vertex_from_index(index: int) -> Coordinate4D:
    """Decode a four-bit index as one vertex of ``{-1, +1}^4``."""
    if index not in range(TESSERACT_VERTEX_COUNT):
        raise ValueError("tesseract vertex index must be in 0..15")
    return tuple(1 if index & (1 << (3 - axis)) else -1 for axis in range(4))


TESSERACT_VERTICES = tuple(
    tesseract_vertex_from_index(index) for index in range(TESSERACT_VERTEX_COUNT)
)

CROSS_POLYTOPE_VERTICES = tuple(
    tuple(sign if coordinate_axis == vertex_axis else 0 for coordinate_axis in range(4))
    for vertex_axis in range(4)
    for sign in W_LAYERS
)


def tesseract_vertex_index(vertex: Coordinate4D) -> int:
    """Encode one tesseract vertex as its canonical four-bit index."""
    if len(vertex) != 4 or any(component not in W_LAYERS for component in vertex):
        raise ValueError("a tesseract vertex must have four coordinates in {-1, +1}")
    return sum((component == 1) << (3 - axis) for axis, component in enumerate(vertex))


def tesseract_parity(vertex: Coordinate4D) -> int:
    """Return the coordinate-product parity selecting one demitesseract."""
    tesseract_vertex_index(vertex)
    return vertex[0] * vertex[1] * vertex[2] * vertex[3]


def demitesseract_vertices(parity: int) -> tuple[Coordinate4D, ...]:
    """Return one eight-vertex parity half of the tesseract."""
    if parity not in W_LAYERS:
        raise ValueError("demitesseract parity must be -1 or +1")
    return tuple(vertex for vertex in TESSERACT_VERTICES if tesseract_parity(vertex) == parity)


def _validate_cross_polytope_vertex(vertex: Coordinate4D) -> None:
    if vertex not in CROSS_POLYTOPE_VERTICES:
        raise ValueError("a 16-cell vertex must be one signed 4D basis vector")


def demitesseract_to_cross_polytope(vertex: Coordinate4D) -> Coordinate4D:
    """Map either parity half by a uniform similarity onto the canonical 16-cell.

    A normalized order-four Hadamard transform maps the positive parity half
    to signed basis vectors.  Flipping W first supplies the same map for the
    negative parity half.
    """
    parity = tesseract_parity(vertex)
    working = vertex if parity == 1 else (*vertex[:3], -vertex[3])
    transformed = tuple(
        sum(coefficient * component for coefficient, component in zip(row, working, strict=True))
        // 4
        for row in _HADAMARD_4
    )
    _validate_cross_polytope_vertex(transformed)
    return transformed


def cross_polytope_to_demitesseract(
    vertex: Coordinate4D,
    parity: int,
) -> Coordinate4D:
    """Invert the Hadamard map into the requested tesseract parity half."""
    _validate_cross_polytope_vertex(vertex)
    if parity not in W_LAYERS:
        raise ValueError("demitesseract parity must be -1 or +1")

    signed_axis = next(index for index, component in enumerate(vertex) if component)
    sign = vertex[signed_axis]
    tesseract_vertex = tuple(sign * component for component in _HADAMARD_4[signed_axis])
    if parity == -1:
        tesseract_vertex = (*tesseract_vertex[:3], -tesseract_vertex[3])
    return tesseract_vertex


def embed_stella_vertex(vertex: Coordinate3D, w_layer: int) -> Coordinate4D:
    """Embed one existing stella vertex in a fixed-W tesseract cell."""
    if vertex not in STELLA_VERTICES:
        raise ValueError("vertex must belong to the existing stella vertex set")
    if w_layer not in W_LAYERS:
        raise ValueError("w_layer must be -1 or +1")
    return (*vertex, w_layer)


def fixed_w_slice(w_layer: int) -> tuple[Coordinate4D, ...]:
    """Return one of the two opposite cubic tesseract cells selected by W."""
    if w_layer not in W_LAYERS:
        raise ValueError("w_layer must be -1 or +1")
    return tuple(embed_stella_vertex(vertex, w_layer) for vertex in STELLA_VERTICES)


def drop_w(coordinate: Coordinate4D) -> Coordinate3D:
    """Orthographically project a 4D coordinate into the existing XYZ space."""
    if len(coordinate) != 4:
        raise ValueError("coordinate must have exactly four components")
    return coordinate[:3]


def gate_spinor_product(left_gate: str, right_gate: str) -> Coordinate4D:
    """Return the even Clifford product of two axial gate roots.

    In three dimensions the product separates into scalar and oriented
    bivector parts. Hodge-dualizing the bivector and placing the scalar on W
    gives ``(cross_xyz, dot)``, one of the eight signed 4D basis vectors.
    """
    left = gate_coordinate(left_gate)
    right = gate_coordinate(right_gate)
    scalar = sum(a * b for a, b in zip(left, right, strict=True))
    cross = (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )
    spinor = (*cross, scalar)
    _validate_cross_polytope_vertex(spinor)
    return spinor


def sixteen_cell_vertices_from_gates() -> tuple[Coordinate4D, ...]:
    """Generate the complete 16-cell vertex set from all ordered gate pairs."""
    return tuple(
        sorted(
            {
                gate_spinor_product(left, right)
                for left in BOUNDARY_GATES
                for right in BOUNDARY_GATES
            }
        )
    )


def tesseract_vertices_from_gates() -> tuple[Coordinate4D, ...]:
    """Lift the gate-generated 16-cell into both tesseract parity halves."""
    return tuple(
        sorted(
            {
                cross_polytope_to_demitesseract(vertex, parity)
                for vertex in sixteen_cell_vertices_from_gates()
                for parity in W_LAYERS
            }
        )
    )


def central_mirror_4d(coordinate: Coordinate4D) -> Coordinate4D:
    """Apply point inversion through the shared four-dimensional origin."""
    if len(coordinate) != 4:
        raise ValueError("coordinate must have exactly four components")
    return tuple(-component for component in coordinate)


def hyper_register_vertex_pair(address: int) -> tuple[Coordinate4D, Coordinate4D]:
    """Decode one 256-state hyper-register address as two tesseract vertices."""
    if address not in range(HYPER_REGISTER_SIZE):
        raise ValueError(f"hyper-register address must be in 0..{HYPER_REGISTER_SIZE - 1}")
    first, second = divmod(address, TESSERACT_VERTEX_COUNT)
    return tesseract_vertex_from_index(first), tesseract_vertex_from_index(second)


def hyper_vertex_pair_address(first: Coordinate4D, second: Coordinate4D) -> int:
    """Encode an ordered pair of tesseract vertices as one hyper-register address."""
    return TESSERACT_VERTEX_COUNT * tesseract_vertex_index(first) + tesseract_vertex_index(second)


def embed_register_address(
    address: int,
    first_w: int,
    second_w: int,
) -> int:
    """Embed one 64-address register into one of four fixed-W sheets."""
    first, second = register_vertex_pair(address)
    return hyper_vertex_pair_address(
        embed_stella_vertex(first, first_w),
        embed_stella_vertex(second, second_w),
    )


def hyper_address_components(address: int) -> tuple[int, int, int]:
    """Return ``(base_64_address, first_W, second_W)`` for a hyper address."""
    first, second = hyper_register_vertex_pair(address)
    base_address = vertex_pair_address(first[:3], second[:3])
    return base_address, first[3], second[3]


def hyper_relative_signature(address: int) -> Coordinate4D:
    """Return per-axis agreement or disagreement for a tesseract pair."""
    first, second = hyper_register_vertex_pair(address)
    return tuple(left * right for left, right in zip(first, second, strict=True))


def hyper_pair_hamming_distance(address: int) -> int:
    """Count differing axes in one ordered pair of tesseract vertices."""
    return hyper_relative_signature(address).count(-1)


def hyper_register_distance_shell_counts() -> tuple[int, int, int, int, int]:
    """Count all 256 ordered pairs by four-bit Hamming distance."""
    counts = [0, 0, 0, 0, 0]
    for address in range(HYPER_REGISTER_SIZE):
        counts[hyper_pair_hamming_distance(address)] += 1
    return tuple(counts)


def central_mirror_hyper_address(address: int) -> int:
    """Mirror both vertices of a hyper-register address through the origin."""
    first, second = hyper_register_vertex_pair(address)
    return hyper_vertex_pair_address(central_mirror_4d(first), central_mirror_4d(second))


@cache
def signed_frames_4d() -> tuple[Frame4D, ...]:
    """Return the 384 signed permutations of four orthogonal axes."""
    return tuple(
        tuple(sign * (world_axis + 1) for world_axis, sign in zip(order, signs, strict=True))
        for order in permutations(range(4))
        for signs in product(W_LAYERS, repeat=4)
    )


def transform_coordinate_4d(coordinate: Coordinate4D, frame: Frame4D) -> Coordinate4D:
    """Apply one validated signed 4D axis frame."""
    if len(coordinate) != 4:
        raise ValueError("coordinate must have exactly four components")
    if frame not in signed_frames_4d():
        raise ValueError("frame must be a signed permutation of four axes")

    transformed = [0, 0, 0, 0]
    for local_axis, signed_world_axis in enumerate(frame):
        world_axis = abs(signed_world_axis) - 1
        sign = 1 if signed_world_axis > 0 else -1
        transformed[world_axis] = sign * coordinate[local_axis]
    return tuple(transformed)


def embed_spatial_frame(assignment: Frame) -> Frame4D:
    """Embed one existing signed XYZ frame while fixing the W axis."""
    assignment_gate_ids(assignment)
    embedded = []
    for label in assignment[:3]:
        axis_name, direction = label.split("_", maxsplit=1)
        sign = 1 if direction == "POS" else -1
        embedded.append(sign * (SPATIAL_AXES.index(axis_name) + 1))
    return (*embedded, 4)


def frame_orientation_4d(frame: Frame4D) -> int:
    """Return +1 for a proper frame and -1 for an orientation reversal."""
    if frame not in signed_frames_4d():
        raise ValueError("frame must be a signed permutation of four axes")

    axes = [abs(value) for value in frame]
    inversions = sum(axes[left] > axes[right] for left in range(4) for right in range(left + 1, 4))
    permutation_sign = -1 if inversions % 2 else 1
    coordinate_sign = prod(1 if value > 0 else -1 for value in frame)
    return permutation_sign * coordinate_sign


def seed_projection_centers_4d() -> tuple[ProjectionCoordinate, ...]:
    """Project the 16-cell through XYZ into the normalized Seed center layout."""
    ring_radius = sqrt(2 / 3)
    projected = [body_diagonal_projection(drop_w(vertex)) for vertex in CROSS_POLYTOPE_VERTICES]
    ring = [
        tuple(component / ring_radius for component in point)
        for point in projected
        if point != (0.0, 0.0)
    ]
    ring.sort(key=lambda point: atan2(point[1], point[0]))
    return ((0.0, 0.0), *ring)


if REGISTER_SIZE * len(W_LAYERS) ** 2 != HYPER_REGISTER_SIZE:
    raise RuntimeError("the 4D register must decompose into four 64-address W sheets")
