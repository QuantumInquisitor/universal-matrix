"""Prescribed common similarity of the fixed assembly, not relative folding.

The scale law is the existing PR119 BreathingCycle law. Phase is dimensionless;
rates and lab currents below are per unit phase, not measured SI quantities.
"""

import math
from dataclasses import dataclass

import numpy as np

from .toroidal_aperture_attachment import build_aperture_attachment
from .toroidal_aperture_fanout import SecondAperture
from .toroidal_bore_downstream import _field
from .toroidal_combined_aperture import audit_combined_aperture, combined_components
from .toroidal_shared_return_connectors import (
    PlacedAnnularTransition,
    _connect_edge,
    _piece_contains,
)
from .toroidal_shared_return_route import RoutedTubePiece


def _scalar(value, name):
    if isinstance(value, (bool, complex)):
        raise ValueError(f"{name} must be finite and real")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be finite and real") from error
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite and real")
    return value


def _vector(value):
    array = np.asarray(value)
    if (
        array.shape != (3,)
        or not np.issubdtype(array.dtype, np.number)
        or np.iscomplexobj(array)
        or not np.all(np.isfinite(array))
    ):
        raise ValueError("finite real three-vector required")
    return array.astype(float)


@dataclass(frozen=True)
class AssemblyBreathing:
    amplitude: float = 0.1

    def __post_init__(self):
        amplitude = _scalar(self.amplitude, "amplitude")
        # This implementation is intentionally restricted to the recovered
        # specimen's strain envelope, not nearly collapsed arithmetic.
        if not 0 <= amplitude <= 0.1:
            raise ValueError("reviewed amplitude range is [0,0.1]")
        object.__setattr__(self, "amplitude", amplitude)

    def state(self, phase):
        phase = _scalar(phase, "phase")
        if not 0 <= phase <= 1:
            raise ValueError("phase must lie in [0,1]")
        sine, cosine = math.sin(2 * math.pi * phase), math.cos(2 * math.pi * phase)
        landmarks = {0.0: (0, 1), 0.25: (1, 0), 0.5: (0, -1), 0.75: (-1, 0), 1.0: (0, 1)}
        if phase in landmarks:
            sine, cosine = landmarks[phase]
        scale = 1 + self.amplitude * sine
        return {
            "scale": scale,
            "scale_rate_per_phase": 2 * math.pi * self.amplitude * cosine,
            "determinant": scale**3,
            "minimum_cycle_scale": 1 - self.amplitude,
        }

    def forward(self, point, phase):
        return self.state(phase)["scale"] * _vector(point)

    def inverse(self, point, phase):
        return _vector(point) / self.state(phase)["scale"]

    def velocity(self, point, phase):
        state = self.state(phase)
        return _vector(point) * state["scale_rate_per_phase"] / state["scale"]

    def relative_current(self, reference_current, phase):
        return _vector(reference_current) / self.state(phase)["scale"] ** 2

    def density(self, reference_density, phase):
        rho = _scalar(reference_density, "reference density")
        if rho < 0:
            raise ValueError("reference density must be nonnegative")
        return rho / self.state(phase)["determinant"]

    def lab_current(self, point, reference_current, reference_density, phase):
        return self.relative_current(reference_current, phase) + self.density(
            reference_density, phase
        ) * self.velocity(point, phase)


class BreathingAssembly:
    """Component-scoped field adapter applying both actual host cuts.

    No summation across touching component charts or global density law is
    inferred. Callers explicitly select a named component and reference density.
    """

    def __init__(self, current=1.0, amplitude=0.1):
        self.cycle = AssemblyBreathing(amplitude)
        self.reference = build_aperture_attachment(current)
        self.second = SecondAperture(self.reference)
        self.audit = audit_combined_aperture(self.reference.downstream.current)
        if not self.audit["static_pair_clearance_complete"]:
            raise ValueError("complete reference pair audit required")
        self.components = {c.name: c.geometry for c in combined_components(self.reference)}
        self.flux = {}
        for edge, names in self.audit["routes"].items():
            flux = _connect_edge(self.reference.downstream.routing.edges[int(edge)]).flux
            self.flux.update({name: flux for name in names})

    def contains(self, name, point, phase):
        p = self.cycle.inverse(point, phase)
        obj = self.components[name]
        if name == self.reference.host_name:
            return self.reference.modified_host_contains(p)
        if name == self.second.host.name:
            return self.second.contains(p)
        if isinstance(obj, PlacedAnnularTransition):
            return obj.contains(p)
        if isinstance(obj, RoutedTubePiece):
            return _piece_contains(obj, p)
        local = p - obj.center
        radius = math.hypot(*local[:2])
        return (
            obj.junction.inner_radius <= radius <= obj.junction.outer_radius
            and abs(local[2]) <= obj.junction.length / 2
        )

    def relative_current(self, name, point, phase):
        if not self.contains(name, point, phase):
            return None
        p = self.cycle.inverse(point, phase)
        if name == self.reference.host_name:
            current = self.reference.modified_host_current(p)
        elif name == self.second.host.name:
            current = self.second.current(p)
        else:
            current = _field(self.components[name], p, self.flux.get(name, 0.0))
        return self.cycle.relative_current(current, phase)


def audit_assembly_breathing(current=1.0, amplitude=0.1):
    assembly = BreathingAssembly(current, amplitude)
    baseline, cycle = assembly.audit, assembly.cycle
    # Port fields are evaluated on the source chart before its exact mapped
    # face; inverse-floating-point roundoff must not move a face outside a cap.
    nodes, weights = np.polynomial.legendre.leggauss(8)
    cuts = []
    for phase in (0.0, 0.125, 0.25, 0.5, 0.75, 1.0):
        s = cycle.state(phase)["scale"]
        for port in baseline["ports"]:
            junction = assembly.reference.downstream.routing.global_routing.junction(
                port["junction"]
            )
            descriptor = junction.junction.port_by_edge(port["edge"])
            normal = np.asarray(port["outward_normal"])
            terms = []
            for q, weight in zip(nodes, weights, strict=True):
                radius = descriptor.inner_radius + (q + 1) * descriptor.width / 2
                for theta in np.arange(16) * math.tau / 16:
                    p = np.asarray(port["center"]) + radius * np.array(
                        (math.cos(theta), math.sin(theta), 0)
                    )
                    j0 = _field(assembly.components[port["component"]], p, 0.0)
                    x = cycle.forward(p, phase)
                    # Use a diagnostic density proportional to current to keep
                    # advection subtraction resolved for the tiny-current case.
                    rho0 = abs(baseline["current"]) / 1000
                    lab = cycle.lab_current(x, j0, rho0, phase)
                    relative = lab - cycle.density(rho0, phase) * cycle.velocity(x, phase)
                    area = s**2 * radius * weight * descriptor.width / 2 * math.tau / 16
                    terms.append(float(np.dot(relative, normal)) * area)
            measured = math.fsum(terms)
            error = abs(measured - port["outward_flux"]) / abs(baseline["current"])
            if not math.isfinite(error) or error > 1e-10:
                raise ValueError("moving-cut flux diagnostic failed")
            cuts.append(
                {
                    "phase": phase,
                    "junction": port["junction"],
                    "edge": port["edge"],
                    "relative_error": error,
                }
            )
    return {
        "current": baseline["current"],
        "amplitude": amplitude,
        "component_count": baseline["component_count"],
        "pair_count": baseline["pair_count"],
        "interface_count": len(baseline["interfaces"]),
        "port_count": len(baseline["ports"]),
        "phase_interval": [0.0, 1.0],
        "minimum_scale": 1 - cycle.amplitude,
        "minimum_deformation_determinant": (1 - cycle.amplitude) ** 3,
        "continuous_common_similarity_clearance": True,
        "argument": "For every pair of actual cut domains A,B: dist(sA,sB)=s dist(A,B), s>=1-amplitude>0. Intersections and declared interfaces map bijectively. F=sI has det(F)=s^3; relative Piola current J0/s^2 times mapped area s^2 preserves flux.",
        "modified_hosts": baseline["modified_hosts"],
        "moving_cut_diagnostics": cuts,
        "maximum_relative_cut_error": max(r["relative_error"] for r in cuts),
        "relative_folding_validated": False,
        "emergent_motion_validated": False,
        "material_energy_validated": False,
        "scope": "Prescribed common similarity in dimensionless phase; inherits floating-point static bounds, not physical or interval validation",
        "breathing_source": "PR119 60a7fd60f57d73b89ea5397db58a3ff5d291556c src/lynchpin_breathing_control.py",
    }
