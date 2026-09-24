"""Spherical inside/outside inversion as a toroidal geometry control.

The map is self-inverse away from its pole, reverses orientation, and preserves
intersections when applied to both volumes. It is not a collision repair or a
continuous nonsingular deformation from the identity. Piola current and area
transport use explicitly matched orientation conventions.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .toroidal_incident_bend_audit import (
    IncidentBendCollisionAudit,
    _endpoint_bend_and_straight,
    audit_incident_bend_collisions,
)
from .toroidal_separated_channels import build_separated_framed_edge_network
from .vesica_tree_circulation import PORT_NODES, vesica_circulation

Vector3D = tuple[float, float, float]


def _vector(values: Sequence[float], name: str) -> Vector3D:
    if len(values) != 3:
        raise ValueError(f"{name} must have three coordinates")
    result = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must be finite")
    return result


def _dot(left: Vector3D, right: Vector3D) -> float:
    return math.fsum(a * b for a, b in zip(left, right, strict=True))


def _distance(left: Vector3D, right: Vector3D) -> float:
    return math.dist(left, right)


@dataclass(frozen=True)
class SphereInversion:
    center: Vector3D = (0.0, 0.0, 0.0)
    radius: float = 100.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "center", _vector(self.center, "center"))
        radius = float(self.radius)
        if not math.isfinite(radius) or radius <= 0.0:
            raise ValueError("radius must be finite and positive")
        object.__setattr__(self, "radius", radius)

    def _metric(self, point: Sequence[float]) -> tuple[Vector3D, float, float]:
        point = _vector(point, "point")
        delta = _vector(tuple(a - b for a, b in zip(point, self.center, strict=True)), "offset")
        distance = math.hypot(*delta)
        if distance == 0.0:
            raise ValueError("inversion is singular at its center")
        ratio = self.radius / distance
        scale = ratio * ratio
        if not math.isfinite(scale) or scale <= 0.0:
            raise ValueError("inversion scale is not representable")
        return tuple(value / distance for value in delta), distance, scale

    def map_point(self, point: Sequence[float]) -> Vector3D:
        unit, distance, scale = self._metric(point)
        image = _vector(tuple(c + scale * distance * n for c, n in zip(self.center, unit, strict=True)), "image")
        if image == self.center:
            raise ValueError("image displacement is not representable at this center")
        return image

    def jacobian(self, point: Sequence[float]) -> tuple[Vector3D, ...]:
        unit, _, scale = self._metric(point)
        return tuple(
            tuple(scale * (float(i == j) - 2.0 * unit[i] * unit[j]) for j in range(3))
            for i in range(3)
        )

    def determinant(self, point: Sequence[float]) -> float:
        _, _, scale = self._metric(point)
        determinant = -scale * scale * scale
        if not math.isfinite(determinant) or determinant == 0.0:
            raise ValueError("Jacobian determinant is not representable")
        return determinant

    def _reflection(self, point: Sequence[float], vector: Sequence[float]) -> tuple[Vector3D, float]:
        unit, _, scale = self._metric(point)
        vector = _vector(vector, "vector")
        projection = _dot(unit, vector)
        return tuple(v - 2.0 * n * projection for v, n in zip(vector, unit, strict=True)), scale

    def piola_current(
        self, point: Sequence[float], current: Sequence[float], *, outward: bool = False
    ) -> Vector3D:
        """Return J*v/det(J), or J*v/abs(det(J)) for outward-normal flux."""
        reflected, scale = self._reflection(point, current)
        denominator = scale * scale * (1.0 if outward else -1.0)
        if not math.isfinite(denominator) or denominator == 0.0:
            raise ValueError("Piola scale is not representable")
        return _vector(tuple(value / denominator for value in reflected), "mapped current")

    def map_area(
        self, point: Sequence[float], area: Sequence[float], *, outward: bool = False
    ) -> Vector3D:
        """Transport parametrized area by cofactor(J), or outward area by its negative."""
        reflected, scale = self._reflection(point, area)
        factor = scale * scale * (1.0 if outward else -1.0)
        if not math.isfinite(factor) or factor == 0.0:
            raise ValueError("area scale is not representable")
        return _vector(tuple(factor * value for value in reflected), "mapped area")

    def singular_blend_fraction(self, point: Sequence[float]) -> float:
        """Where the straight blend (1-t)*point+t*F(point) loses radial rank."""
        _, _, scale = self._metric(point)
        return 1.0 / (1.0 + scale)


@dataclass(frozen=True)
class InversionWitnessControl:
    source_witness_count: int
    retained_witness_count: int
    minimum_pole_clearance_bound: float
    maximum_roundtrip_error: float
    maximum_flux_pairing_residual: float
    minimum_absolute_jacobian: float
    minimum_singular_blend_fraction: float
    maximum_singular_blend_fraction: float


def audit_inverted_collision_witnesses(
    audit: IncidentBendCollisionAudit,
    inversion: SphereInversion = SphereInversion(),
) -> InversionWitnessControl:
    """Transport existing witnesses, not resample or certify the full network.

    Conservative enclosing balls must exclude the pole for each witnessed
    bend/straight pair. This makes the control valid over those entire volumes.
    It is deliberately silent about other network volumes and untouched pairs.
    """
    if not audit.collisions:
        raise ValueError("at least one collision witness is required")
    edges = {edge.edge_index: edge for edge in audit.smooth_routing.edges}
    clearances, errors, residuals, determinants, fractions = [], [], [], [], []
    retained = 0
    for witness in audit.collisions:
        bend, _ = _endpoint_bend_and_straight(edges[witness.bending_edge_index], witness.node)
        _, straight = _endpoint_bend_and_straight(edges[witness.straight_edge_index], witness.node)
        midpoint = tuple((a + b) / 2 for a, b in zip(straight.start, straight.end, strict=True))
        clearance = min(
            _distance(inversion.center, bend.corner) - bend.bend_radius - bend.outer_radius,
            _distance(inversion.center, midpoint) - math.hypot(straight.length / 2, straight.outer_radius),
        )
        if clearance <= 0.0:
            raise ValueError("enclosing-ball bounds cannot exclude the inversion pole")
        clearances.append(clearance)
        source = witness.witness_point
        image = inversion.map_point(source)
        recovered = inversion.map_point(image)
        errors.append(_distance(source, recovered))
        # Membership in F(volume) is evaluated through F^{-1}=F. This is a
        # transported witness control, not an independent collision search.
        if bend.inverse_parameters(recovered) is not None and straight.penetration_margin(recovered) > 0:
            retained += 1
        determinants.append(abs(inversion.determinant(source)))
        fractions.append(inversion.singular_blend_fraction(source))
        current = bend.current(source)
        area = bend.tangent(witness.witness_phi)
        for outward in (False, True):
            residuals.append(abs(
                _dot(inversion.piola_current(source, current, outward=outward),
                     inversion.map_area(source, area, outward=outward))
                - _dot(current, area)
            ))
    return InversionWitnessControl(
        source_witness_count=len(audit.collisions),
        retained_witness_count=retained,
        minimum_pole_clearance_bound=min(clearances),
        maximum_roundtrip_error=max(errors),
        maximum_flux_pairing_residual=max(residuals),
        minimum_absolute_jacobian=min(determinants),
        minimum_singular_blend_fraction=min(fractions),
        maximum_singular_blend_fraction=max(fractions),
    )


def main() -> None:
    circulation = vesica_circulation(1.0, return_split=0.4)
    network = build_separated_framed_edge_network(circulation.edges, PORT_NODES, shell_gap=3.0)
    audit = audit_incident_bend_collisions(
        network, bend_margin=0.05, phi_samples=13, q_samples=5, theta_samples=24,
        phi_offset=0.5, q_offset=0.5, theta_offset=0.5,
    )
    control = audit_inverted_collision_witnesses(audit)
    print("TOROIDAL INSIDE-OUT INVERSION CONTROL")
    print("map=spherical_inversion; center=[0,0,0]; radius=100; orientation=reversing")
    print("scope=existing_witness_pairs; no_collision_repair_or_continuous_motion_claim")
    for name in control.__dataclass_fields__:
        print(f"{name}={getattr(control, name):.12g}")


if __name__ == "__main__":
    main()
