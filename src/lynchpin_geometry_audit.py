"""Reproducible geometry audit for the Howard Lynchpin and All-Shape corpus.

The patent disclosures define useful panel incidence, component counts, and
several assembly families.  They do not define unique coordinates, hinge
angles, material laws, or propulsion performance for every drawing.  This
module therefore separates exact combinatorics from dimensional feasibility,
underspecified embeddings, and untested physical claims.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from functools import cache
from itertools import combinations, permutations
from math import acos, degrees, sqrt

from .h3_600_cell_bridge import H3_ROOTS
from .platonic_solid_bridge import (
    ICOSAHEDRON_VERTICES,
    ONE,
    PHI,
    ZERO,
    PhiNumber,
    dot,
    solid_edges,
    solid_signature,
)

Panel = tuple[int, int]
Permutation = tuple[int, ...]


class AuditStatus(StrEnum):
    """Evidence class for one disclosed shape or claim."""

    EXACT = "exact"
    EXACT_TOPOLOGY = "exact-topology"
    PARAMETRIC = "parametric"
    UNDERSPECIFIED = "underspecified"
    INCONSISTENT_AS_WRITTEN = "inconsistent-as-written"
    UNTESTED_PHYSICAL = "untested-physical"
    ORNAMENTAL_REFERENCE = "ornamental-reference"


@dataclass(frozen=True)
class ShapeConfiguration:
    """One disclosed configuration and the strongest warranted status."""

    key: str
    publication: str
    figures: tuple[int, ...]
    description: str
    component_count: int | None
    status: AuditStatus
    unresolved: tuple[str, ...] = ()


# Six panels are indexed by the six edges of an abstract tetrahedron.  At each
# tetrahedron vertex, the three incident edge-panels share a hinge.  This is the
# incidence stated in Examples 1 and 19 of US9731215B2.
LYNCHPIN_PANELS: tuple[Panel, ...] = tuple(combinations(range(4), 2))
LYNCHPIN_TRIPLE_HINGES: tuple[tuple[int, int, int], ...] = tuple(
    tuple(index for index, panel in enumerate(LYNCHPIN_PANELS) if vertex in panel)
    for vertex in range(4)
)


def lynchpin_panel_adjacencies() -> tuple[tuple[int, int], ...]:
    """Return panel pairs that meet at one of the four triple hinges."""
    return tuple(
        (left, right)
        for left, right in combinations(range(len(LYNCHPIN_PANELS)), 2)
        if set(LYNCHPIN_PANELS[left]) & set(LYNCHPIN_PANELS[right])
    )


def lynchpin_opposite_panel_pairs() -> tuple[tuple[int, int], ...]:
    """Return the three panel pairs associated with opposite tetrahedron edges."""
    return tuple(
        (left, right)
        for left, right in combinations(range(len(LYNCHPIN_PANELS)), 2)
        if set(LYNCHPIN_PANELS[left]).isdisjoint(LYNCHPIN_PANELS[right])
    )


def lynchpin_panel_degrees() -> tuple[int, ...]:
    """Return the degree-four octahedral adjacency signature."""
    degree = Counter(panel for edge in lynchpin_panel_adjacencies() for panel in edge)
    return tuple(degree[index] for index in range(len(LYNCHPIN_PANELS)))


def tetrahedral_panel_symmetry_groups() -> tuple[tuple[Permutation, ...], tuple[Permutation, ...]]:
    """Return proper and full tetrahedral actions on the six Lynchpin panels."""

    def parity(vertex_permutation: tuple[int, ...]) -> int:
        inversions = sum(
            vertex_permutation[left] > vertex_permutation[right]
            for left, right in combinations(range(4), 2)
        )
        return -1 if inversions % 2 else 1

    panel_index = {panel: index for index, panel in enumerate(LYNCHPIN_PANELS)}
    actions = []
    proper = []
    for vertex_permutation in permutations(range(4)):
        action = tuple(
            panel_index[tuple(sorted((vertex_permutation[left], vertex_permutation[right])))]
            for left, right in LYNCHPIN_PANELS
        )
        actions.append(action)
        if parity(vertex_permutation) == 1:
            proper.append(action)
    return tuple(sorted(proper)), tuple(sorted(actions))


PENTAGON_INTERIOR_ANGLE_DEGREES = Fraction(108)
PENTAGON_INTERIOR_COSINE = (ONE - PHI) / 2
TETRAHEDRAL_RAY_COSINE = PhiNumber(Fraction(-1, 3))


def regular_polygon_interior_angle_degrees(sides: int) -> Fraction:
    """Return the Euclidean interior angle of a regular polygon."""
    if sides < 3:
        raise ValueError("a polygon must have at least three sides")
    return Fraction(180 * (sides - 2), sides)


def equiangular_gram_determinant(ray_count: int, cosine: PhiNumber) -> PhiNumber:
    """Return the determinant for equal unit-ray pairwise cosine ``cosine``."""
    if ray_count < 2:
        raise ValueError("at least two rays are required")
    repeated_eigenvalue = ONE - cosine
    determinant = ONE + (ray_count - 1) * cosine
    for _ in range(ray_count - 1):
        determinant *= repeated_eigenvalue
    return determinant


def equiangular_ray_rank(ray_count: int, cosine: PhiNumber) -> int:
    """Return the exact Gram rank when the equal-angle Gram matrix is valid."""
    if ray_count < 2:
        raise ValueError("at least two rays are required")
    simple_eigenvalue = ONE + (ray_count - 1) * cosine
    repeated_eigenvalue = ONE - cosine
    if float(simple_eigenvalue) < -1e-12 or float(repeated_eigenvalue) < -1e-12:
        raise ValueError("the requested equal-ray Gram matrix is not positive semidefinite")
    if repeated_eigenvalue == ZERO:
        return 1
    if simple_eigenvalue == ZERO:
        return ray_count - 1
    return ray_count


def equal_ray_angle_degrees(cosine: PhiNumber) -> float:
    """Convert an exact Q(phi) pairwise cosine to degrees."""
    return degrees(acos(float(cosine)))


def local_hinge_cosine(ray_cosine: PhiNumber) -> PhiNumber:
    """Return the cosine between two rays after projection normal to a third."""
    return ray_cosine / (ONE + ray_cosine)


def unit_square_split_areas() -> tuple[Fraction, Fraction]:
    """Return the two Euclidean triangle areas from a diagonal unit-square split."""
    return Fraction(1, 2), Fraction(1, 2)


def metric_area_scale(
    g_xx: int | Fraction,
    g_xy: int | Fraction,
    g_yy: int | Fraction,
) -> float:
    """Return ``sqrt(det(g))`` for a constant positive 2D metric."""
    xx = Fraction(g_xx)
    xy = Fraction(g_xy)
    yy = Fraction(g_yy)
    determinant = xx * yy - xy**2
    if xx <= 0 or determinant <= 0:
        raise ValueError("the metric must be positive definite")
    return sqrt(float(determinant))


@cache
def dodecahedral_face_adjacencies() -> tuple[tuple[int, int], ...]:
    """Return dodecahedral face adjacency through its dual icosahedron."""
    index = {vertex: position for position, vertex in enumerate(ICOSAHEDRON_VERTICES)}
    return tuple(
        sorted((min(index[left], index[right]), max(index[left], index[right])))
        for left, right in solid_edges("icosahedron")
    )


def _adjacency_map() -> tuple[frozenset[int], ...]:
    adjacency = [set() for _ in ICOSAHEDRON_VERTICES]
    for left, right in dodecahedral_face_adjacencies():
        adjacency[left].add(right)
        adjacency[right].add(left)
    return tuple(frozenset(neighbors) for neighbors in adjacency)


def _component_sizes(vertices: frozenset[int]) -> tuple[int, ...]:
    adjacency = _adjacency_map()
    remaining = set(vertices)
    sizes = []
    while remaining:
        start = min(remaining)
        seen = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current] & vertices:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        sizes.append(len(seen))
        remaining -= seen
    return tuple(sorted(sizes))


@cache
def connected_dodecahedral_six_face_subsets() -> tuple[frozenset[int], ...]:
    """Enumerate every connected six-face selection on a dodecahedron."""
    subsets = []
    for candidate in combinations(range(len(ICOSAHEDRON_VERTICES)), 6):
        selected = frozenset(candidate)
        if _component_sizes(selected) == (6,):
            subsets.append(selected)
    return tuple(subsets)


def _reflection_permutations() -> tuple[Permutation, ...]:
    index = {vertex: position for position, vertex in enumerate(ICOSAHEDRON_VERTICES)}
    reflections = []
    for root in H3_ROOTS:
        image = []
        for vertex in ICOSAHEDRON_VERTICES:
            scale = 2 * dot(vertex, root) / dot(root, root)
            reflected = tuple(vertex[axis] - scale * root[axis] for axis in range(3))
            image.append(index[reflected])
        reflections.append(tuple(image))
    return tuple(reflections)


@cache
def icosahedral_symmetry_groups() -> tuple[tuple[Permutation, ...], tuple[Permutation, ...]]:
    """Return the 60 proper and 120 full H3 actions on dodecahedral faces."""
    identity = tuple(range(len(ICOSAHEDRON_VERTICES)))
    orientation = {identity: 1}
    queue = deque((identity,))
    generators = _reflection_permutations()
    while queue:
        action = queue.popleft()
        for reflection in generators:
            composite = tuple(reflection[action[index]] for index in range(len(action)))
            sign = -orientation[action]
            if composite not in orientation:
                orientation[composite] = sign
                queue.append(composite)
            elif orientation[composite] != sign:
                raise RuntimeError("inconsistent H3 orientation parity")
    full = tuple(sorted(orientation))
    proper = tuple(action for action in full if orientation[action] == 1)
    return proper, full


@dataclass(frozen=True)
class SixFaceOrbit:
    """One symmetry class of connected six-face dodecahedral patches."""

    representative: tuple[int, ...]
    orbit_size: int
    internal_adjacencies: int
    degree_sequence: tuple[int, ...]
    boundary_edges: int
    complement_components: tuple[int, ...]
    proper_orbit_count: int

    @property
    def has_distinct_mirror_partner(self) -> bool:
        return self.proper_orbit_count == 2


def _subset_orbit(selected: frozenset[int], group: tuple[Permutation, ...]) -> set[frozenset[int]]:
    return {frozenset(action[index] for index in selected) for action in group}


@cache
def dodecahedral_six_face_orbits(include_reflections: bool = True) -> tuple[SixFaceOrbit, ...]:
    """Classify all connected six-face patches under H3 symmetry."""
    proper, full = icosahedral_symmetry_groups()
    group = full if include_reflections else proper
    universe = set(connected_dodecahedral_six_face_subsets())
    remaining = set(universe)
    adjacency = {frozenset(edge) for edge in dodecahedral_face_adjacencies()}
    results = []
    while remaining:
        selected = min(remaining, key=lambda subset: tuple(sorted(subset)))
        orbit = _subset_orbit(selected, group)
        if not orbit <= universe:
            raise RuntimeError("H3 action escaped the connected six-face universe")
        remaining -= orbit
        degrees_in_patch = tuple(
            sorted(
                sum(frozenset((vertex, other)) in adjacency for other in selected - {vertex})
                for vertex in selected
            )
        )
        internal = sum(degrees_in_patch) // 2
        complement = frozenset(range(len(ICOSAHEDRON_VERTICES))) - selected
        proper_count = len(_subset_orbit(selected, full)) // len(_subset_orbit(selected, proper))
        results.append(
            SixFaceOrbit(
                representative=tuple(sorted(selected)),
                orbit_size=len(orbit),
                internal_adjacencies=internal,
                degree_sequence=degrees_in_patch,
                boundary_edges=30 - 2 * internal,
                complement_components=_component_sizes(complement),
                proper_orbit_count=proper_count,
            )
        )
    return tuple(sorted(results, key=lambda result: result.representative))


def modified_dodecahedron_panel_ledger(lynchpin_count: int) -> tuple[int, int, int]:
    """Return total panels, shell faces, and panels not uniquely mapped to the shell."""
    if lynchpin_count < 1:
        raise ValueError("at least one Lynchpin is required")
    total_panels = 6 * lynchpin_count
    shell_faces = solid_signature("dodecahedron")[2]
    return total_panels, shell_faces, max(0, total_panels - shell_faces)


CORE_LYNCHPIN_CONFIGURATIONS = (
    ShapeConfiguration(
        "different_edge_triplet",
        "US11117065B2",
        (1,),
        "three hinged regular pentagons on different edges",
        3,
        AuditStatus.PARAMETRIC,
        ("hinge angles",),
    ),
    ShapeConfiguration(
        "common_edge_triplet",
        "US11117065B2",
        (2,),
        "three regular pentagons sharing one non-manifold hinge",
        3,
        AuditStatus.EXACT_TOPOLOGY,
        ("hinge angles",),
    ),
    ShapeConfiguration(
        "six_panel_lynchpin",
        "US11117065B2",
        (3,),
        "two pentagonal triplets combined into one six-panel module",
        6,
        AuditStatus.EXACT_TOPOLOGY,
        ("edge lengths", "unique 3D coordinates"),
    ),
    ShapeConfiguration(
        "four_unit_modified_dodecahedron",
        "US11117065B2",
        (4,),
        "four Lynchpins arranged around a dodecahedral shell",
        4,
        AuditStatus.UNDERSPECIFIED,
        ("panel-to-shell map",),
    ),
    ShapeConfiguration(
        "tetrahedral_building_block",
        "US11117065B2",
        (5,),
        "four circular or flanged faces around a tetrahedral inner space",
        4,
        AuditStatus.EXACT_TOPOLOGY,
        ("flange curvature",),
    ),
    ShapeConfiguration(
        "extended_tetrahedral_structure",
        "US11117065B2",
        (6,),
        "one base with four extendable tetrahedral branches",
        5,
        AuditStatus.PARAMETRIC,
        ("branch length",),
    ),
    ShapeConfiguration(
        "tetrahedrally_supported_lynchpin",
        "US11117065B2",
        (7,),
        "six-panel module on a tetrahedral edge scaffold",
        None,
        AuditStatus.UNDERSPECIFIED,
        ("support multiplicity",),
    ),
    ShapeConfiguration(
        "lateral_compound_pair",
        "US11117065B2",
        (8,),
        "two Lynchpins joined along three flange pairs",
        2,
        AuditStatus.EXACT_TOPOLOGY,
        ("relative pose",),
    ),
    ShapeConfiguration(
        "compound_propulsion_pair",
        "US11117065B2",
        (9,),
        "lateral pair with one or more propulsion devices",
        2,
        AuditStatus.UNTESTED_PHYSICAL,
        ("mass", "thrust", "power", "control law"),
    ),
    ShapeConfiguration(
        "reinforced_lateral_pair",
        "US11117065B2",
        (10,),
        "lateral pair with circular reinforcements and support arms",
        2,
        AuditStatus.UNDERSPECIFIED,
        ("dimensions",),
    ),
    ShapeConfiguration(
        "four_unit_variant_a",
        "US11117065B2",
        (11, 12),
        "first four-Lynchpin modified-dodecahedron orientation",
        4,
        AuditStatus.UNDERSPECIFIED,
        ("attachment map",),
    ),
    ShapeConfiguration(
        "four_unit_variant_b",
        "US11117065B2",
        (13, 14),
        "second four-Lynchpin modified-dodecahedron orientation",
        4,
        AuditStatus.UNDERSPECIFIED,
        ("attachment map",),
    ),
    ShapeConfiguration(
        "four_unit_variant_c",
        "US11117065B2",
        (15, 16),
        "third four-Lynchpin modified-dodecahedron orientation",
        4,
        AuditStatus.UNDERSPECIFIED,
        ("attachment map",),
    ),
    ShapeConfiguration(
        "five_unit_variant_a",
        "US11117065B2",
        (17, 18),
        "first five-Lynchpin modified-dodecahedron orientation",
        5,
        AuditStatus.UNDERSPECIFIED,
        ("attachment map",),
    ),
    ShapeConfiguration(
        "five_unit_variant_b",
        "US11117065B2",
        (19, 20),
        "second five-Lynchpin modified-dodecahedron orientation",
        5,
        AuditStatus.UNDERSPECIFIED,
        ("attachment map",),
    ),
    ShapeConfiguration(
        "five_unit_variant_c",
        "US11117065B2",
        (21, 22),
        "third five-Lynchpin modified-dodecahedron orientation",
        5,
        AuditStatus.UNDERSPECIFIED,
        ("attachment map",),
    ),
    ShapeConfiguration(
        "modified_compound_lynchpin",
        "US11117065B2",
        (23,),
        "four surface Lynchpins surrounding one internal Lynchpin",
        5,
        AuditStatus.UNDERSPECIFIED,
        ("internal contacts",),
    ),
    ShapeConfiguration(
        "supported_four_unit_dodecahedron",
        "US11117065B2",
        (24,),
        "four Lynchpins joined by a modified tetrahedral support",
        4,
        AuditStatus.UNDERSPECIFIED,
        ("support geometry",),
    ),
)


COLLAPSIBLE_ASSEMBLIES = (
    ShapeConfiguration(
        "dodecahedron_from_triplets",
        "US9731215B2",
        (5,),
        "four three-pentagon units forming twelve dodecahedral faces",
        4,
        AuditStatus.EXACT_TOPOLOGY,
    ),
    ShapeConfiguration(
        "nested_tetrahedral_pair",
        "US9731215B2",
        (8,),
        "two tetrahedral blocks nested through a removed or collapsed face",
        2,
        AuditStatus.PARAMETRIC,
        ("nest depth",),
    ),
    ShapeConfiguration(
        "tetrahedral_tripod",
        "US9731215B2",
        (9,),
        "four collapsed blocks on the four vertices of one base block",
        5,
        AuditStatus.EXACT_TOPOLOGY,
    ),
    ShapeConfiguration(
        "neutral_converter",
        "US9731215B2",
        (12,),
        "four tetrahedral blocks meeting at one vertex",
        4,
        AuditStatus.EXACT_TOPOLOGY,
    ),
    ShapeConfiguration(
        "positive_universal_joint",
        "US9731215B2",
        (13,),
        "two neutral converters enclosing an octahedral inner space",
        8,
        AuditStatus.EXACT_TOPOLOGY,
    ),
    ShapeConfiguration(
        "turbine_connector",
        "US9731215B2",
        (14,),
        "six consistently oriented tetrahedral blocks around a hexagonal void",
        6,
        AuditStatus.EXACT_TOPOLOGY,
    ),
    ShapeConfiguration(
        "negative_universal_joint",
        "US9731215B2",
        (15,),
        "two oppositely oriented neutral converters",
        8,
        AuditStatus.EXACT_TOPOLOGY,
    ),
    ShapeConfiguration(
        "phase_capacitor_coupling",
        "US9731215B2",
        (16,),
        "eight flexibly connected tetrahedral blocks",
        8,
        AuditStatus.PARAMETRIC,
        ("connection stiffness",),
    ),
)


_ENHANCED_COUNTS = (3, 6, None, 4, 4, 6, 4, 6, 4, 4, 3, 4, 4, 18, 3, 4, 8)
_ENHANCED_FIGURES = (2, 3, 6, 9, 11, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27)
_ENHANCED_DESCRIPTIONS = (
    "three warped elliptical panels",
    "six curved quadrilateral panels forming a cube analogue",
    "contracted tetrahedral inner volume with hinged flanges",
    "four curved six-pointed panels around a tetrahedral inner volume",
    "four sigmoid or reverse-sigmoid fan panels forming a curvilinear tetrahedral Whirl Maker",
    "six curved four-pointed panels forming a cube analogue",
    "four warped elliptical panels forming a football-like volume",
    "six three-pointed panels in three coplanar pairs",
    "four type-440 curved panels",
    "four type-420 curved panels",
    "three type-720 curved panels",
    "three type-140 panels plus an inserted elliptical cutout",
    "four type-450 curved panels",
    "opposed six-block three-dimensional stars plus six planar ellipses",
    "three reduced type-720 curved panels",
    "four contracted type-430 panels",
    "eight type-430 panels forming two square pyramids",
)
ENHANCED_BUILDING_CONFIGURATIONS = tuple(
    ShapeConfiguration(
        key=f"enhanced_example_{number:02d}",
        publication="US10556189B2",
        figures=(_ENHANCED_FIGURES[number - 1],),
        description=_ENHANCED_DESCRIPTIONS[number - 1],
        component_count=_ENHANCED_COUNTS[number - 1],
        status=AuditStatus.UNDERSPECIFIED,
        unresolved=("surface equations", "edge lengths", "assembled coordinates"),
    )
    for number in range(1, 18)
)


DESIGN_PATENT_SHAPES = (
    ("USD763970S1", "tetrahedral turbine block"),
    ("USD798391S1", "pentagonal building block"),
    ("USD798392S1", "tetrahedral positive universal joint block"),
    ("USD800227S1", "tetrahedral negative universal joint block"),
    ("USD802683S1", "tetrahedral neutral converter block"),
    ("USD837902S1", "octahedral block"),
    ("USD841872S1", "light unit modular block"),
    ("USD842385S1", "expanded octahedral block"),
    ("USD843494S1", "expanded tetrahedral block"),
    ("USD843495S1", "expanded triangular block"),
    ("USD843496S1", "contracted triangular block"),
    ("USD843497S1", "tetrahedral block"),
    ("USD849852S1", "pentagonal turbine block"),
    ("USD861080S1", "pentagonal tetrahedral block"),
    ("USD892392S1", "light unit cluster block"),
    ("USD896321S1", "standing wave block"),
    ("USD897450S1", "parabolic Lynchpin block"),
    ("USD898129S1", "mated block"),
    ("USD906438S1", "polyhedral lattice block"),
    ("USD906439S1", "tetrahedral icosahedron block"),
    ("USD939636S1", "mirrored sheet-formed tetrahedral pair"),
    ("USD968521S1", "separable tetrahedral icosahedron block"),
    ("USD1002750S1", "circular internal Lynchpin structure"),
    ("USD1121503S1", "aerial vehicle"),
)


if solid_signature("octahedron")[:2] != (
    len(LYNCHPIN_PANELS),
    len(lynchpin_panel_adjacencies()),
):
    raise RuntimeError("the Lynchpin panel graph must have octahedral V/E incidence")
if len(icosahedral_symmetry_groups()[0]) != 60 or len(icosahedral_symmetry_groups()[1]) != 120:
    raise RuntimeError("the dodecahedral classifier requires the complete H3 symmetry group")
