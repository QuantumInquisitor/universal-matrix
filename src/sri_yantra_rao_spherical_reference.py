"""Sourced spherical Sri Yantra reference equations from C. S. Rao (1998).

Rao constructs a spherical triangular complex from great-circle arcs. The
geometry is controlled by six basic angular variables b, c, d, e, g, h in
radians. The remaining arc lengths and intersection quantities are derived by
spherical trigonometry, and selected groups of six nonlinear constraint
functions are solved simultaneously.

This module implements one published checkpoint rather than attempting to
infer a spherical Sri Yantra from the planar Huet coordinates.

The reference row is Rao Table 1 for constraints F1, F2, F4, F5, F10, F19,
with printed values:

    b = 0.231687
    c = 0.120012
    d = 0.146680
    e = 0.230471
    g = 0.053009
    h = 1.076084

Using only those rounded published values, all six implemented residuals close
at approximately 1e-7.

The equations implemented here correspond to Rao equations 2.1a, 2.2-2.14,
2.15-2.24, 2.25-2.33, 2.34-2.44, and constraints 3.1, 3.2, 3.4, 3.5, 3.10,
and 3.19.

This is a metric spherical reference checkpoint. It does not yet derive the
complete spherical 43-chamber incidence complex.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

_TOLERANCE = 1e-12


@dataclass(frozen=True)
class RaoSphericalParameters:
    """Six independent angular variables in Rao's spherical formulation."""

    b: float
    c: float
    d: float
    e: float
    g: float
    h: float

    def __post_init__(self) -> None:
        for name in ("b", "c", "d", "e", "g", "h"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)

        if self.h >= math.pi / 2:
            raise ValueError("h must be less than pi/2 so the spherical radius arc is positive")

    @property
    def r(self) -> float:
        """Angular radius of the spherical triangular-complex base circle."""
        return math.pi / 2 - self.h

    @property
    def a(self) -> float:
        """Lower symmetry-axis intercept from Rao equation 2.2."""
        return self.r - self.b - self.c

    @property
    def f(self) -> float:
        """Upper symmetry-axis intercept from Rao equation 2.2."""
        return self.r - self.d - self.e

    def validate_partition(self) -> None:
        if self.a <= 0.0 or self.f <= 0.0:
            raise ValueError("published spherical partition requires positive a and f")
        if abs(self.a + self.b + self.c - self.r) > _TOLERANCE:
            raise RuntimeError("a+b+c must equal r")
        if abs(self.d + self.e + self.f - self.r) > _TOLERANCE:
            raise RuntimeError("d+e+f must equal r")


@dataclass(frozen=True)
class RaoSphericalDerived:
    """Derived arc/intersection quantities used by the reference constraints."""

    parameters: RaoSphericalParameters

    x1: float
    x2: float
    x3: float
    x4: float
    x5: float
    x6: float

    u7: float
    v7: float
    x7: float

    u8: float
    capital_v8: float
    x8: float
    v8: float

    x16: float
    x11: float
    x17: float

    u9: float
    capital_v9: float
    x9: float
    v9: float

    x10: float
    x18: float

    u12: float
    capital_v12: float
    x12: float
    v12: float

    x14: float
    x13: float
    x19: float
    x11a: float

    tangent_bisector_angle: float
    inscribed_radius: float
    r17: float
    r19: float


@dataclass(frozen=True)
class RaoConstraintResiduals:
    """Six selected Table-1 constraint residuals for the reference row."""

    f1: float
    f2: float
    f4: float
    f5: float
    f10: float
    f19: float

    @property
    def selected_indices(self) -> tuple[int, int, int, int, int, int]:
        return (1, 2, 4, 5, 10, 19)

    @property
    def values(self) -> tuple[float, ...]:
        return (self.f1, self.f2, self.f4, self.f5, self.f10, self.f19)

    @property
    def maximum_absolute(self) -> float:
        return max(abs(value) for value in self.values)


RAO_TABLE1_REFERENCE_PARAMETERS = RaoSphericalParameters(
    b=0.231687,
    c=0.120012,
    d=0.146680,
    e=0.230471,
    g=0.053009,
    h=1.076084,
)


def _acos_checked(value: float) -> float:
    if value < -1.0 - 1e-12 or value > 1.0 + 1e-12:
        raise ValueError("spherical cosine left the real domain")
    return math.acos(max(-1.0, min(1.0, value)))


def _acute_from_tangent(value: float) -> float:
    """Recover the acute arc used by Rao's published reference configuration."""
    if not math.isfinite(value):
        raise ValueError("derived tangent must be finite")
    if value <= 0.0:
        raise ValueError("reference branch expects a positive acute tangent")
    return math.atan(value)


def _u_from_partition(total: float, quotient: float) -> float:
    """Evaluate Rao equations 2.13, 2.19, 2.29, and 2.38."""
    tangent = math.sin(total) / (quotient + math.cos(total))
    return _acute_from_tangent(tangent)


def derive_rao_spherical(
    parameters: RaoSphericalParameters = RAO_TABLE1_REFERENCE_PARAMETERS,
) -> RaoSphericalDerived:
    """Evaluate the sourced spherical-trigonometric construction."""
    parameters.validate_partition()

    b = parameters.b
    c = parameters.c
    d = parameters.d
    e = parameters.e
    g = parameters.g
    r = parameters.r

    x1 = _acos_checked(math.cos(r) / math.cos(c))
    x2 = _acos_checked(math.cos(r) / math.cos(d))

    x3 = _acute_from_tangent(
        math.sin(r - c) / math.sin(r + d) * math.tan(x2)
    )
    x4 = _acute_from_tangent(
        math.sin(r - d) / math.sin(r + c) * math.tan(x1)
    )
    x5 = _acute_from_tangent(
        math.sin(b) / math.sin(b + c + d) * math.tan(x4)
    )
    x6 = _acute_from_tangent(
        math.sin(e) / math.sin(c + d + e) * math.tan(x3)
    )

    s7 = d + g
    q7 = (
        math.sin(d + g)
        * math.tan(x5)
        / (math.sin(c + d) * math.tan(x6))
    )
    u7 = _u_from_partition(s7, q7)
    v7 = s7 - u7
    x7 = _acute_from_tangent(
        math.sin(u7) / math.sin(c + d) * math.tan(x5)
    )

    s8 = r + g
    q8 = (
        math.sin(d + g)
        * math.tan(x1)
        / (math.sin(r + c) * math.tan(x6))
    )
    u8 = _u_from_partition(s8, q8)
    capital_v8 = s8 - u8
    x8 = _acute_from_tangent(
        math.sin(u8) / math.sin(r + c) * math.tan(x1)
    )
    v8 = r - u8 - d

    x16 = _acute_from_tangent(
        math.sin(d + e + g) / math.sin(r + c) * math.tan(x6)
    )
    x11 = _acute_from_tangent(
        math.sin(d + g) / math.sin(c + d) * math.tan(x5)
    )
    x17 = _acute_from_tangent(
        math.sin(b + c + d) / math.sin(c + d) * math.tan(x5)
    )

    s9 = r + d
    q9 = (
        math.sin(c + d)
        * math.tan(x2)
        / (math.sin(r + d) * math.tan(x5))
    )
    u9 = _u_from_partition(s9, q9)
    capital_v9 = s9 - u9
    x9 = _acute_from_tangent(
        math.sin(u9) / math.sin(r + d) * math.tan(x2)
    )
    v9 = r - u9 - c

    x10 = _acute_from_tangent(
        math.sin(b + c - g) / math.sin(b + c + d) * math.tan(x4)
    )
    x18 = _acute_from_tangent(
        math.sin(b + c + d + v8)
        / math.sin(b + c + d)
        * math.tan(x4)
    )

    s12 = d + g + v8
    q12 = (
        math.sin(d + g + v8)
        * math.tan(x6)
        / (math.sin(d + g) * math.tan(x10))
    )
    u12 = _u_from_partition(s12, q12)
    capital_v12 = s12 - u12
    x12 = _acute_from_tangent(
        math.sin(u12) / math.sin(d + g) * math.tan(x6)
    )
    v12 = d + g - u12

    x14 = _acute_from_tangent(
        math.sin(u7 + capital_v8)
        / math.sin(d + g + v8)
        * math.tan(x10)
    )
    x13 = _acute_from_tangent(
        math.sin(e + v12)
        / math.sin(c + d + e)
        * math.tan(x3)
    )
    x19 = _acute_from_tangent(
        math.sin(c + d + e + v9)
        / math.sin(c + d + e)
        * math.tan(x3)
    )
    x11a = _acute_from_tangent(
        math.sin(v9 + c - g)
        / math.sin(v9 + c + d - v12)
        * math.tan(x13)
    )

    tangent_bisector_angle = _acute_from_tangent(
        math.tan(d + g - u7) / math.sin(x7)
    )
    inscribed_radius = _acute_from_tangent(
        math.sin(x7) * math.tan(tangent_bisector_angle / 2.0)
    )

    r17 = _acos_checked(math.cos(b + c) * math.cos(x17))
    r19 = _acos_checked(math.cos(c + v9) * math.cos(x19))

    return RaoSphericalDerived(
        parameters=parameters,
        x1=x1,
        x2=x2,
        x3=x3,
        x4=x4,
        x5=x5,
        x6=x6,
        u7=u7,
        v7=v7,
        x7=x7,
        u8=u8,
        capital_v8=capital_v8,
        x8=x8,
        v8=v8,
        x16=x16,
        x11=x11,
        x17=x17,
        u9=u9,
        capital_v9=capital_v9,
        x9=x9,
        v9=v9,
        x10=x10,
        x18=x18,
        u12=u12,
        capital_v12=capital_v12,
        x12=x12,
        v12=v12,
        x14=x14,
        x13=x13,
        x19=x19,
        x11a=x11a,
        tangent_bisector_angle=tangent_bisector_angle,
        inscribed_radius=inscribed_radius,
        r17=r17,
        r19=r19,
    )


def selected_constraint_residuals(
    derived: RaoSphericalDerived,
) -> RaoConstraintResiduals:
    """Evaluate Rao constraints 1, 2, 4, 5, 10, and 19."""
    p = derived.parameters
    c = p.c
    d = p.d
    g = p.g

    f1 = derived.x11 - derived.x11a
    f2 = d - derived.u7 - derived.inscribed_radius
    f4 = (
        math.cos(c + d + derived.v9 - derived.v12)
        - math.cos(2.0 * derived.x13) / math.cos(derived.x13)
    )
    f5 = derived.x10 - derived.x13
    f10 = p.b + c - d - 2.0 * g - derived.v8
    f19 = derived.r17 - derived.r19

    return RaoConstraintResiduals(
        f1=f1,
        f2=f2,
        f4=f4,
        f5=f5,
        f10=f10,
        f19=f19,
    )


RAO_TABLE1_REFERENCE_DERIVED = derive_rao_spherical()
RAO_TABLE1_REFERENCE_RESIDUALS = selected_constraint_residuals(
    RAO_TABLE1_REFERENCE_DERIVED
)

if RAO_TABLE1_REFERENCE_RESIDUALS.selected_indices != (1, 2, 4, 5, 10, 19):
    raise RuntimeError("the Rao reference row must use constraints 1,2,4,5,10,19")
if RAO_TABLE1_REFERENCE_RESIDUALS.maximum_absolute > 1e-6:
    raise RuntimeError(
        "the six-decimal Rao Table-1 reference row must close the selected "
        "spherical constraints to better than 1e-6"
    )
