"""Map localized radial matter profiles into 3D and test persistence.

This module bridges radial boundary-value matter solutions and 3D real-time
classical matter dynamics.

The Cartesian mapping spacing is also the dynamical lattice spacing.  This is
required so the radial coordinate, lattice Laplacian, energy, charge, and RMS
radius all refer to the same spatial scale.

The persistence diagnostic does not by itself prove nonlinear stability. It is
a controlled numerical survival test.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

try:
    from .classical_matter_dynamics import ClassicalMatterDynamics
    from .radial_matter_solver import RadialMatterSolution
except ImportError:
    from classical_matter_dynamics import ClassicalMatterDynamics
    from radial_matter_solver import RadialMatterSolution


def cartesian_radius_grid(
    shape: tuple[int, int, int],
    spacing: float,
) -> np.ndarray:
    if len(shape) != 3 or min(shape) < 3:
        raise ValueError("shape must be a 3D grid with each dimension >=3")
    if not math.isfinite(spacing) or spacing <= 0:
        raise ValueError("spacing must be finite and positive")

    axes = [
        (np.arange(n, dtype=float) - 0.5 * (n - 1)) * spacing
        for n in shape
    ]
    x, y, z = np.meshgrid(*axes, indexing="ij")
    return np.sqrt(x*x + y*y + z*z)


def interpolate_radial_profile(
    radial_radius: np.ndarray,
    radial_profile: np.ndarray,
    radius_grid: np.ndarray,
) -> np.ndarray:
    r = np.asarray(radial_radius, dtype=float)
    f = np.asarray(radial_profile, dtype=float)
    if r.ndim != 1 or f.ndim != 1 or r.shape != f.shape:
        raise ValueError("radial arrays must be equal-length 1D arrays")
    if np.any(np.diff(r) <= 0):
        raise ValueError("radial_radius must be strictly increasing")

    return np.interp(
        radius_grid,
        r,
        f,
        left=float(f[0]),
        right=0.0,
    )


def rms_radius(
    phi: np.ndarray,
    spacing: float,
) -> float:
    rho = np.abs(np.asarray(phi, dtype=complex)) ** 2
    shape = rho.shape
    radii = cartesian_radius_grid(shape, spacing)
    norm = float(np.sum(rho))
    if norm <= 0:
        return 0.0
    return math.sqrt(float(np.sum(radii*radii*rho)) / norm)


def radial_solution_to_dynamics(
    solution: RadialMatterSolution,
    shape: tuple[int, int, int] = (25, 25, 25),
    spacing: float = 0.5,
) -> ClassicalMatterDynamics:
    radii = cartesian_radius_grid(shape, spacing)
    profile = interpolate_radial_profile(
        solution.radius,
        solution.profile,
        radii,
    )
    phi = profile.astype(complex)
    momentum = 1j * solution.omega * phi
    links = np.zeros((3,) + shape, dtype=float)

    return ClassicalMatterDynamics(
        phi=phi,
        momentum=momentum,
        links=links,
        potential=solution.potential,
        lattice_spacing=spacing,
    )


@dataclass(frozen=True)
class PersistenceReport:
    steps: int
    dt: float
    initial_energy: float
    final_energy: float
    initial_charge: float
    final_charge: float
    initial_peak: float
    final_peak: float
    initial_rms_radius: float
    final_rms_radius: float

    @property
    def relative_energy_drift(self) -> float:
        if self.initial_energy == 0:
            return 0.0
        return (self.final_energy - self.initial_energy) / self.initial_energy

    @property
    def relative_charge_drift(self) -> float:
        if self.initial_charge == 0:
            return 0.0
        return (self.final_charge - self.initial_charge) / self.initial_charge

    @property
    def radius_ratio(self) -> float:
        if self.initial_rms_radius == 0:
            return math.inf if self.final_rms_radius > 0 else 1.0
        return self.final_rms_radius / self.initial_rms_radius

    @property
    def peak_ratio(self) -> float:
        if self.initial_peak == 0:
            return math.inf if self.final_peak > 0 else 1.0
        return self.final_peak / self.initial_peak


def evolve_persistence(
    state: ClassicalMatterDynamics,
    *,
    steps: int,
    dt: float,
    spacing: float | None = None,
) -> PersistenceReport:
    if steps < 0:
        raise ValueError("steps must be non-negative")
    if not math.isfinite(dt) or dt <= 0:
        raise ValueError("dt must be finite and positive")

    diagnostic_spacing = (
        state.lattice_spacing
        if spacing is None
        else float(spacing)
    )
    if not math.isfinite(diagnostic_spacing) or diagnostic_spacing <= 0:
        raise ValueError("spacing must be finite and positive")
    if not math.isclose(
        diagnostic_spacing,
        state.lattice_spacing,
        rel_tol=0.0,
        abs_tol=1e-15,
    ):
        raise ValueError(
            "diagnostic spacing must match state.lattice_spacing"
        )

    e0 = state.energy
    q0 = state.charge
    p0 = float(np.max(np.abs(state.phi)))
    r0 = rms_radius(state.phi, diagnostic_spacing)

    for _ in range(steps):
        state.step(dt)

    return PersistenceReport(
        steps=steps,
        dt=dt,
        initial_energy=e0,
        final_energy=state.energy,
        initial_charge=q0,
        final_charge=state.charge,
        initial_peak=p0,
        final_peak=float(np.max(np.abs(state.phi))),
        initial_rms_radius=r0,
        final_rms_radius=rms_radius(state.phi, diagnostic_spacing),
    )
