"""Embedding-independent and multidimensional Sri Yantra candidate contract.

The familiar planar Sri Yantra is treated here as one realization of an
abstract, ordered relational complex rather than as the complete object.  The
canonical source-derived inventory has nine generator triangles, nine
``avaranas`` (enclosures), forty-three triangular cells, twenty-four lotus
petals, four boundary gates, and one bindu.  Those counts are kept separate
from any particular coordinate drawing.

Three historically documented realization families are represented by typed
metadata: plane, spherical, and three-dimensional Meru.  The module also
defines two explicit engine candidates: an oriented-simplex lift to arbitrary
dimension and a spiral-cone chart.  The candidates are deliberately named as
such; neither is claimed to be a traditional construction or a physical
description of the universe.

The local Yantra coordinate is attached as a fibre over the existing product
address

    (recursive universe, named plane, possibility path).

Changing the drawing or ambient dimension therefore does not silently change
universe scale, plane, possibility, enclosure, or phase.  Projection and lift
operations preserve this abstract address.  Inward and outward shell currents
use a dimensionless cut flux and satisfy the same finite-graph continuity
convention as the existing Vesica and Tree circulation model.

All exact statements in this module are software, combinatorial, or elementary
geometric identities under the declared model.  They do not establish that a
Sri Yantra is a literal higher-dimensional physical object, that the candidate
phase is time, or that the graph flux is energy, Ether, Consciousness, or any
other measured quantity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import IntEnum, StrEnum
from fractions import Fraction

from .transitive_plane_branching import PlaneAddress, mirror_plane_address

_TOLERANCE = 1e-12


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _positive_dimension(value: int, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value < 1:
        raise ValueError(f"{name} must be positive")
    return value


class ComponentKind(StrEnum):
    """Primary component counted in one canonical enclosure."""

    BOUNDARY_GATE = "boundary_gate"
    LOTUS_PETAL = "lotus_petal"
    TRIANGULAR_CELL = "triangular_cell"
    BINDU = "bindu"


class AvaranaId(StrEnum):
    """Canonical enclosure identifiers ordered from outside to inside."""

    BHUPURA = "bhupura"
    LOTUS_SIXTEEN = "lotus_sixteen"
    LOTUS_EIGHT = "lotus_eight"
    TRIANGLES_FOURTEEN = "triangles_fourteen"
    TRIANGLES_TEN_OUTER = "triangles_ten_outer"
    TRIANGLES_TEN_INNER = "triangles_ten_inner"
    TRIANGLES_EIGHT = "triangles_eight"
    INNER_TRIANGLE = "inner_triangle"
    BINDU = "bindu"


@dataclass(frozen=True, order=True)
class AvaranaSpec:
    """One source-derived enclosure in the canonical outer-to-inner order."""

    ordinal: int
    identifier: AvaranaId
    component_kind: ComponentKind
    component_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.ordinal, int) or isinstance(self.ordinal, bool):
            raise TypeError("avarana ordinal must be an integer")
        if self.ordinal < 1:
            raise ValueError("avarana ordinal must be positive")
        if not isinstance(self.identifier, AvaranaId):
            raise TypeError("identifier must be an AvaranaId")
        if not isinstance(self.component_kind, ComponentKind):
            raise TypeError("component_kind must be a ComponentKind")
        if not isinstance(self.component_count, int) or isinstance(self.component_count, bool):
            raise TypeError("component_count must be an integer")
        if self.component_count < 1:
            raise ValueError("component_count must be positive")


CANONICAL_AVARANAS = (
    AvaranaSpec(1, AvaranaId.BHUPURA, ComponentKind.BOUNDARY_GATE, 4),
    AvaranaSpec(2, AvaranaId.LOTUS_SIXTEEN, ComponentKind.LOTUS_PETAL, 16),
    AvaranaSpec(3, AvaranaId.LOTUS_EIGHT, ComponentKind.LOTUS_PETAL, 8),
    AvaranaSpec(4, AvaranaId.TRIANGLES_FOURTEEN, ComponentKind.TRIANGULAR_CELL, 14),
    AvaranaSpec(5, AvaranaId.TRIANGLES_TEN_OUTER, ComponentKind.TRIANGULAR_CELL, 10),
    AvaranaSpec(6, AvaranaId.TRIANGLES_TEN_INNER, ComponentKind.TRIANGULAR_CELL, 10),
    AvaranaSpec(7, AvaranaId.TRIANGLES_EIGHT, ComponentKind.TRIANGULAR_CELL, 8),
    AvaranaSpec(8, AvaranaId.INNER_TRIANGLE, ComponentKind.TRIANGULAR_CELL, 1),
    AvaranaSpec(9, AvaranaId.BINDU, ComponentKind.BINDU, 1),
)


class GeneratorOrientation(IntEnum):
    """Signed orientation of a generator simplex."""

    DOWNWARD = -1
    UPWARD = 1


@dataclass(frozen=True, order=True)
class YantraGenerator:
    """One of the four upward or five downward source triangles."""

    orientation: GeneratorOrientation
    family_index: int

    def __post_init__(self) -> None:
        if not isinstance(self.orientation, GeneratorOrientation):
            raise TypeError("orientation must be a GeneratorOrientation")
        if not isinstance(self.family_index, int) or isinstance(self.family_index, bool):
            raise TypeError("family_index must be an integer")
        if self.family_index < 1:
            raise ValueError("family_index must be positive")

    @property
    def key(self) -> str:
        prefix = "up" if self.orientation is GeneratorOrientation.UPWARD else "down"
        return f"{prefix}_{self.family_index}"


CANONICAL_GENERATORS = tuple(
    YantraGenerator(GeneratorOrientation.UPWARD, index) for index in range(1, 5)
) + tuple(YantraGenerator(GeneratorOrientation.DOWNWARD, index) for index in range(1, 6))


@dataclass(frozen=True)
class SriYantraComplex:
    """Abstract inventory retained independently of every geometric embedding."""

    avaranas: tuple[AvaranaSpec, ...]
    generators: tuple[YantraGenerator, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.avaranas, tuple) or not self.avaranas:
            raise TypeError("avaranas must be a nonempty tuple")
        if not isinstance(self.generators, tuple) or not self.generators:
            raise TypeError("generators must be a nonempty tuple")
        if any(not isinstance(spec, AvaranaSpec) for spec in self.avaranas):
            raise TypeError("every avarana must be an AvaranaSpec")
        if any(not isinstance(generator, YantraGenerator) for generator in self.generators):
            raise TypeError("every generator must be a YantraGenerator")

        ordinals = tuple(spec.ordinal for spec in self.avaranas)
        if ordinals != tuple(range(1, len(self.avaranas) + 1)):
            raise ValueError("avaranas must use contiguous outer-to-inner ordinals")
        if len({spec.identifier for spec in self.avaranas}) != len(self.avaranas):
            raise ValueError("avarana identifiers must be unique")
        if len(set(self.generators)) != len(self.generators):
            raise ValueError("generators must be unique")

        for orientation in GeneratorOrientation:
            indices = sorted(
                generator.family_index
                for generator in self.generators
                if generator.orientation is orientation
            )
            if indices and indices != list(range(1, len(indices) + 1)):
                raise ValueError("generator family indices must be contiguous")

    @property
    def triangular_cell_count(self) -> int:
        return sum(
            spec.component_count
            for spec in self.avaranas
            if spec.component_kind is ComponentKind.TRIANGULAR_CELL
        )

    @property
    def lotus_petal_count(self) -> int:
        return sum(
            spec.component_count
            for spec in self.avaranas
            if spec.component_kind is ComponentKind.LOTUS_PETAL
        )

    @property
    def boundary_gate_count(self) -> int:
        return sum(
            spec.component_count
            for spec in self.avaranas
            if spec.component_kind is ComponentKind.BOUNDARY_GATE
        )

    def generator_count(self, orientation: GeneratorOrientation) -> int:
        if not isinstance(orientation, GeneratorOrientation):
            raise TypeError("orientation must be a GeneratorOrientation")
        return sum(generator.orientation is orientation for generator in self.generators)

    @property
    def signature(self) -> tuple[object, ...]:
        """Return an embedding-independent signature for regression checks."""
        return (
            tuple(
                (
                    spec.ordinal,
                    spec.identifier.value,
                    spec.component_kind.value,
                    spec.component_count,
                )
                for spec in self.avaranas
            ),
            tuple((generator.key, int(generator.orientation)) for generator in self.generators),
        )


CANONICAL_SRI_YANTRA = SriYantraComplex(CANONICAL_AVARANAS, CANONICAL_GENERATORS)

if len(CANONICAL_SRI_YANTRA.avaranas) != 9:
    raise RuntimeError("the canonical Sri Yantra inventory must have nine avaranas")
if CANONICAL_SRI_YANTRA.triangular_cell_count != 43:
    raise RuntimeError("the canonical Sri Yantra inventory must have 43 triangular cells")
if CANONICAL_SRI_YANTRA.lotus_petal_count != 24:
    raise RuntimeError("the canonical Sri Yantra inventory must have 24 lotus petals")
if CANONICAL_SRI_YANTRA.generator_count(GeneratorOrientation.UPWARD) != 4:
    raise RuntimeError("the canonical Sri Yantra inventory must have four upward generators")
if CANONICAL_SRI_YANTRA.generator_count(GeneratorOrientation.DOWNWARD) != 5:
    raise RuntimeError("the canonical Sri Yantra inventory must have five downward generators")

_AVARANA_BY_ID = {spec.identifier: spec for spec in CANONICAL_AVARANAS}


def avarana_spec(identifier: AvaranaId) -> AvaranaSpec:
    """Return one canonical enclosure specification."""
    if not isinstance(identifier, AvaranaId):
        raise TypeError("identifier must be an AvaranaId")
    return _AVARANA_BY_ID[identifier]


@dataclass(frozen=True, order=True)
class YantraLocation:
    """One cyclically indexed component inside a canonical enclosure."""

    avarana: AvaranaId
    member: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.avarana, AvaranaId):
            raise TypeError("avarana must be an AvaranaId")
        if not isinstance(self.member, int) or isinstance(self.member, bool):
            raise TypeError("member must be an integer")
        count = avarana_spec(self.avarana).component_count
        if self.member not in range(count):
            raise ValueError(f"member must be in 0..{count - 1} for {self.avarana.value}")

    @property
    def ordinal(self) -> int:
        return avarana_spec(self.avarana).ordinal

    @property
    def member_count(self) -> int:
        return avarana_spec(self.avarana).component_count


def cyclic_mirror_location(location: YantraLocation) -> YantraLocation:
    """Reflect one enclosure's chosen cyclic labelling through member zero."""
    if not isinstance(location, YantraLocation):
        raise TypeError("location must be a YantraLocation")
    return YantraLocation(location.avarana, (-location.member) % location.member_count)


class RealizationKind(StrEnum):
    """Documented forms and explicitly labelled engine candidates."""

    PLANE = "plane"
    SPHERICAL = "spherical"
    MERU = "meru"
    SIMPLEX_FIELD_CANDIDATE = "simplex_field_candidate"
    SPIRAL_CONE_CANDIDATE = "spiral_cone_candidate"


class CurvatureKind(StrEnum):
    """Coarse intrinsic-curvature classification used by the contract."""

    FLAT = "flat"
    POSITIVE = "positive"
    MIXED_OR_PIECEWISE = "mixed_or_piecewise"


@dataclass(frozen=True, order=True)
class YantraRealization:
    """A typed realization without conflating ambient and intrinsic dimension."""

    kind: RealizationKind
    intrinsic_dimension: int
    ambient_dimension: int
    curvature: CurvatureKind

    def __post_init__(self) -> None:
        if not isinstance(self.kind, RealizationKind):
            raise TypeError("kind must be a RealizationKind")
        intrinsic = _positive_dimension(self.intrinsic_dimension, "intrinsic_dimension")
        ambient = _positive_dimension(self.ambient_dimension, "ambient_dimension")
        if intrinsic > ambient:
            raise ValueError("intrinsic dimension cannot exceed ambient dimension")
        if not isinstance(self.curvature, CurvatureKind):
            raise TypeError("curvature must be a CurvatureKind")

        expected = {
            RealizationKind.PLANE: (2, 2, CurvatureKind.FLAT),
            RealizationKind.SPHERICAL: (2, 3, CurvatureKind.POSITIVE),
            RealizationKind.MERU: (3, 3, CurvatureKind.MIXED_OR_PIECEWISE),
            RealizationKind.SPIRAL_CONE_CANDIDATE: (
                3,
                3,
                CurvatureKind.MIXED_OR_PIECEWISE,
            ),
        }
        if self.kind in expected and (intrinsic, ambient, self.curvature) != expected[self.kind]:
            raise ValueError(f"{self.kind.value} realization has a fixed dimension signature")
        if self.kind is RealizationKind.SIMPLEX_FIELD_CANDIDATE:
            if intrinsic < 2 or ambient != intrinsic + 1:
                raise ValueError(
                    "a simplex-field candidate uses intrinsic dimension d >= 2 "
                    "in d + 1 barycentric coordinates"
                )
            if self.curvature is not CurvatureKind.FLAT:
                raise ValueError("a centered simplex template uses a flat carrier hyperplane")


PLANE_REALIZATION = YantraRealization(
    RealizationKind.PLANE,
    intrinsic_dimension=2,
    ambient_dimension=2,
    curvature=CurvatureKind.FLAT,
)
SPHERICAL_REALIZATION = YantraRealization(
    RealizationKind.SPHERICAL,
    intrinsic_dimension=2,
    ambient_dimension=3,
    curvature=CurvatureKind.POSITIVE,
)
MERU_REALIZATION = YantraRealization(
    RealizationKind.MERU,
    intrinsic_dimension=3,
    ambient_dimension=3,
    curvature=CurvatureKind.MIXED_OR_PIECEWISE,
)
SPIRAL_CONE_REALIZATION = YantraRealization(
    RealizationKind.SPIRAL_CONE_CANDIDATE,
    intrinsic_dimension=3,
    ambient_dimension=3,
    curvature=CurvatureKind.MIXED_OR_PIECEWISE,
)


def simplex_field_realization(dimension: int) -> YantraRealization:
    """Return the candidate d-simplex realization in barycentric coordinates."""
    dimension = _positive_dimension(dimension, "dimension")
    if dimension < 2:
        raise ValueError("simplex-field dimension must be at least two")
    return YantraRealization(
        RealizationKind.SIMPLEX_FIELD_CANDIDATE,
        intrinsic_dimension=dimension,
        ambient_dimension=dimension + 1,
        curvature=CurvatureKind.FLAT,
    )


@dataclass(frozen=True)
class YantraFiberAddress:
    """A local Yantra coordinate carried over the existing three-factor address."""

    base: PlaneAddress
    location: YantraLocation
    phase: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        if not isinstance(self.base, PlaneAddress):
            raise TypeError("base must be a PlaneAddress")
        if not isinstance(self.location, YantraLocation):
            raise TypeError("location must be a YantraLocation")
        if not isinstance(self.phase, (int, Fraction)) or isinstance(self.phase, bool):
            raise TypeError("phase must be an integer or Fraction measured in turns")
        object.__setattr__(self, "phase", Fraction(self.phase) % 1)

    def over(self, base: PlaneAddress) -> YantraFiberAddress:
        """Move the fibre unchanged to an explicitly supplied base address."""
        if not isinstance(base, PlaneAddress):
            raise TypeError("base must be a PlaneAddress")
        return replace(self, base=base)

    def advanced(self, phase_delta: int | Fraction) -> YantraFiberAddress:
        """Advance the independent circular phase coordinate."""
        if not isinstance(phase_delta, (int, Fraction)) or isinstance(phase_delta, bool):
            raise TypeError("phase_delta must be an integer or Fraction")
        return replace(self, phase=self.phase + Fraction(phase_delta))


def mirror_yantra_address(address: YantraFiberAddress) -> YantraFiberAddress:
    """Mirror base, cyclic member, and phase while retaining enclosure depth."""
    if not isinstance(address, YantraFiberAddress):
        raise TypeError("address must be a YantraFiberAddress")
    return YantraFiberAddress(
        mirror_plane_address(address.base),
        cyclic_mirror_location(address.location),
        -address.phase,
    )


class FlowSense(IntEnum):
    """Orientation of motion through the outer-to-inner enclosure order."""

    INWARD = -1
    STATIONARY = 0
    OUTWARD = 1


@dataclass(frozen=True)
class RealizedYantraState:
    """One fibre address together with a chosen view and flow orientation."""

    address: YantraFiberAddress
    realization: YantraRealization
    flow: FlowSense = FlowSense.STATIONARY
    handedness: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.address, YantraFiberAddress):
            raise TypeError("address must be a YantraFiberAddress")
        if not isinstance(self.realization, YantraRealization):
            raise TypeError("realization must be a YantraRealization")
        if not isinstance(self.flow, FlowSense):
            raise TypeError("flow must be a FlowSense")
        if self.handedness not in (-1, 1) or isinstance(self.handedness, bool):
            raise ValueError("handedness must be -1 or +1")


def mirror_realized_state(state: RealizedYantraState) -> RealizedYantraState:
    """Apply the address mirror without changing the selected realization."""
    if not isinstance(state, RealizedYantraState):
        raise TypeError("state must be a RealizedYantraState")
    return replace(state, address=mirror_yantra_address(state.address))


def reverse_flow(state: RealizedYantraState) -> RealizedYantraState:
    """Exchange inward and outward flow while preserving every coordinate."""
    if not isinstance(state, RealizedYantraState):
        raise TypeError("state must be a RealizedYantraState")
    return replace(state, flow=FlowSense(-int(state.flow)))


def reverse_handedness(state: RealizedYantraState) -> RealizedYantraState:
    """Exchange the two spiral chiralities without changing flow or address."""
    if not isinstance(state, RealizedYantraState):
        raise TypeError("state must be a RealizedYantraState")
    return replace(state, handedness=-state.handedness)


def project_realized_state(
    state: RealizedYantraState,
    target: YantraRealization,
) -> RealizedYantraState:
    """Lower or retain ambient dimension while preserving the abstract state."""
    if not isinstance(state, RealizedYantraState):
        raise TypeError("state must be a RealizedYantraState")
    if not isinstance(target, YantraRealization):
        raise TypeError("target must be a YantraRealization")
    if target.ambient_dimension > state.realization.ambient_dimension:
        raise ValueError("projection cannot increase ambient dimension")
    return replace(state, realization=target)


def lift_realized_state(
    state: RealizedYantraState,
    target: YantraRealization,
) -> RealizedYantraState:
    """Raise or retain ambient dimension while preserving the abstract state."""
    if not isinstance(state, RealizedYantraState):
        raise TypeError("state must be a RealizedYantraState")
    if not isinstance(target, YantraRealization):
        raise TypeError("target must be a YantraRealization")
    if target.ambient_dimension < state.realization.ambient_dimension:
        raise ValueError("lift cannot decrease ambient dimension")
    return replace(state, realization=target)


@dataclass(frozen=True)
class ShellCurrent:
    """Dimensionless current across one adjacent-enclosure interface."""

    source: AvaranaId
    target: AvaranaId
    magnitude: float

    def __post_init__(self) -> None:
        if not isinstance(self.source, AvaranaId) or not isinstance(self.target, AvaranaId):
            raise TypeError("shell-current endpoints must be AvaranaId values")
        if self.source == self.target:
            raise ValueError("a shell current must join distinct enclosures")
        source_ordinal = avarana_spec(self.source).ordinal
        target_ordinal = avarana_spec(self.target).ordinal
        if abs(source_ordinal - target_ordinal) != 1:
            raise ValueError("a shell current must join adjacent enclosures")
        magnitude = _finite(self.magnitude, "magnitude")
        if magnitude < 0:
            raise ValueError("magnitude must be nonnegative")
        object.__setattr__(self, "magnitude", magnitude)

    def reversed(self) -> ShellCurrent:
        return ShellCurrent(self.target, self.source, self.magnitude)


def shell_currents(total_flux: float, sense: FlowSense) -> tuple[ShellCurrent, ...]:
    """Carry one conserved cut flux through every adjacent enclosure pair."""
    total_flux = _finite(total_flux, "total_flux")
    if total_flux < 0:
        raise ValueError("total_flux must be nonnegative")
    if not isinstance(sense, FlowSense):
        raise TypeError("sense must be a FlowSense")
    if sense is FlowSense.STATIONARY:
        if total_flux > _TOLERANCE:
            raise ValueError("stationary shell flow requires zero total flux")
        return ()

    identifiers = tuple(spec.identifier for spec in CANONICAL_AVARANAS)
    inward = tuple(
        ShellCurrent(source, target, total_flux)
        for source, target in zip(identifiers, identifiers[1:], strict=False)
    )
    if sense is FlowSense.INWARD:
        return inward
    return tuple(current.reversed() for current in reversed(inward))


def shell_divergence(currents: tuple[ShellCurrent, ...]) -> dict[AvaranaId, float]:
    """Return outgoing-minus-incoming divergence on all nine enclosures."""
    if not isinstance(currents, tuple):
        raise TypeError("currents must be a tuple")
    divergence = {spec.identifier: 0.0 for spec in CANONICAL_AVARANAS}
    for current in currents:
        if not isinstance(current, ShellCurrent):
            raise TypeError("every current must be a ShellCurrent")
        divergence[current.source] += current.magnitude
        divergence[current.target] -= current.magnitude
    return divergence


def closed_shell_circulation(total_flux: float) -> tuple[ShellCurrent, ...]:
    """Superpose exact inward and outward routes to make zero divergence."""
    inward = shell_currents(total_flux, FlowSense.INWARD)
    outward = shell_currents(total_flux, FlowSense.OUTWARD)
    return inward + outward


def uniform_component_flux(total_flux: float, avarana: AvaranaId) -> tuple[float, ...]:
    """Distribute a shell-cut flux uniformly without equating component counts."""
    total_flux = _finite(total_flux, "total_flux")
    if total_flux < 0:
        raise ValueError("total_flux must be nonnegative")
    count = avarana_spec(avarana).component_count
    return (total_flux / count,) * count


SimplexCoordinate = tuple[Fraction, ...]


def centered_simplex_vertices(
    dimension: int,
    orientation: GeneratorOrientation = GeneratorOrientation.UPWARD,
) -> tuple[SimplexCoordinate, ...]:
    """Return a regular d-simplex centered in a zero-sum d+1 coordinate plane.

    The vertices are ``e_i - 1/(d+1)``.  Negating all coordinates supplies the
    oppositely oriented compound.  This is the candidate lift that turns a
    triangle into a tetrahedron, 4-simplex, and so on; it is not asserted to be
    the unique higher-dimensional Sri Yantra construction.
    """
    dimension = _positive_dimension(dimension, "dimension")
    if dimension < 2:
        raise ValueError("simplex dimension must be at least two")
    if not isinstance(orientation, GeneratorOrientation):
        raise TypeError("orientation must be a GeneratorOrientation")

    coordinate_count = dimension + 1
    offset = Fraction(1, coordinate_count)
    sign = int(orientation)
    vertices = []
    for vertex_index in range(coordinate_count):
        vertex = tuple(
            sign * (Fraction(int(axis == vertex_index)) - offset)
            for axis in range(coordinate_count)
        )
        vertices.append(vertex)
    return tuple(vertices)


@dataclass(frozen=True)
class LiftedGenerator:
    """One source triangle replaced by an oriented regular d-simplex template."""

    generator: YantraGenerator
    dimension: int
    vertices: tuple[SimplexCoordinate, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.generator, YantraGenerator):
            raise TypeError("generator must be a YantraGenerator")
        dimension = _positive_dimension(self.dimension, "dimension")
        expected = centered_simplex_vertices(dimension, self.generator.orientation)
        if self.vertices != expected:
            raise ValueError("vertices must be the canonical centered simplex template")


def lift_generator(generator: YantraGenerator, dimension: int) -> LiftedGenerator:
    """Lift one oriented source triangle to the candidate simplex family."""
    if not isinstance(generator, YantraGenerator):
        raise TypeError("generator must be a YantraGenerator")
    return LiftedGenerator(
        generator,
        dimension,
        centered_simplex_vertices(dimension, generator.orientation),
    )


def lift_all_generators(
    dimension: int,
    complex_: SriYantraComplex = CANONICAL_SRI_YANTRA,
) -> tuple[LiftedGenerator, ...]:
    """Lift all generator orientations without inventing placement constraints."""
    if not isinstance(complex_, SriYantraComplex):
        raise TypeError("complex_ must be a SriYantraComplex")
    return tuple(lift_generator(generator, dimension) for generator in complex_.generators)


def candidate_spiral_cone_point(
    state: RealizedYantraState,
    radial_scale: float = 1.0,
    axial_height: float = 1.0,
) -> tuple[float, float, float]:
    """Place one abstract circuit coordinate on a rotating cone chart.

    This chart is an engine hypothesis inspired by the project's spiral-cone
    scale map.  It is not an exact construction of a historical Sri Meru.  The
    outer enclosure lies on the base radius and the bindu lies at the apex.
    Phase rotates every noncentral component; handedness chooses the direction.
    """
    if not isinstance(state, RealizedYantraState):
        raise TypeError("state must be a RealizedYantraState")
    if state.realization != SPIRAL_CONE_REALIZATION:
        raise ValueError("state must use the spiral-cone candidate realization")
    radial_scale = _finite(radial_scale, "radial_scale")
    axial_height = _finite(axial_height, "axial_height")
    if radial_scale <= 0 or axial_height <= 0:
        raise ValueError("radial_scale and axial_height must be positive")

    location = state.address.location
    depth = Fraction(location.ordinal - 1, len(CANONICAL_AVARANAS) - 1)
    radius = radial_scale * (1.0 - float(depth))
    angle_turns = Fraction(location.member, location.member_count) + (
        state.handedness * state.address.phase
    )
    angle = 2.0 * math.pi * float(angle_turns)
    return (
        radius * math.cos(angle),
        radius * math.sin(angle),
        axial_height * float(depth),
    )


def candidate_spherical_shell_point(
    address: YantraFiberAddress,
) -> tuple[float, float, float]:
    """Place an enclosure coordinate on a unit hemispherical circuit chart.

    This is a generic chart for the abstract inventory, not the historically
    constrained spherical triangular network.  Its purpose is to verify that
    the fibre address survives a curved embedding without being called a new
    universe, plane, or possibility branch.
    """
    if not isinstance(address, YantraFiberAddress):
        raise TypeError("address must be a YantraFiberAddress")
    location = address.location
    depth = Fraction(location.ordinal - 1, len(CANONICAL_AVARANAS) - 1)
    polar = (1.0 - float(depth)) * math.pi / 2.0
    azimuth_turns = Fraction(location.member, location.member_count) + address.phase
    azimuth = 2.0 * math.pi * float(azimuth_turns)
    sin_polar = math.sin(polar)
    return (
        sin_polar * math.cos(azimuth),
        sin_polar * math.sin(azimuth),
        math.cos(polar),
    )


STATE_SPACE_FACTORS = (
    "recursive_universe",
    "named_plane",
    "possibility_path",
    "avarana",
    "local_member",
    "phase",
    "realization",
    "flow",
    "handedness",
)
