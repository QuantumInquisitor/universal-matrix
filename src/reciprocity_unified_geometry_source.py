"""Unified reciprocity-geometry source accounting.

The reciprocity scalar psi couples to every classical sector through the same
metric dependence. For a total action

    S_total
      = S_psi
        + S_scalar_matter
        + S_U1
        + S_YangMills
        + ...

the matter/gauge source entering the psi variation is additive:

    S_active(x)
      = sqrt(-g) [
          T^00_total
          + T^11_total
          + T^22_total
          + T^33_total
        ].

For a stationary localized isolated composite with conserved stress-energy, the
von Laue condition gives

    int T^ij d^3x = 0.

Therefore

    M_active
      = int [T^00 + sum_i T^ii] d^3x
      = E_total.

This means universality is a property of the COMPLETE stationary composite,
including field and binding stresses, not of each constituent density by
itself.

This module combines already-derived scalar, U(1), and generic Yang-Mills
geometry sources into one explicit ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping
import math
import numpy as np

try:
    from .localized_matter_variational import MatterPotential
    from .self_consistent_reciprocity_action import (
        active_source_density_canonical as scalar_active_source_density,
        local_matter_energy_density,
    )
    from .reciprocity_u1_geometry_action import (
        geometry_source_density_canonical as u1_active_source_density,
        hamiltonian_density as u1_energy_density,
    )
    from .reciprocity_yang_mills_geometry import (
        geometry_source_density as ym_active_source_density,
        hamiltonian_density as ym_energy_density,
    )
except ImportError:
    from localized_matter_variational import MatterPotential
    from self_consistent_reciprocity_action import (
        active_source_density_canonical as scalar_active_source_density,
        local_matter_energy_density,
    )
    from reciprocity_u1_geometry_action import (
        geometry_source_density_canonical as u1_active_source_density,
        hamiltonian_density as u1_energy_density,
    )
    from reciprocity_yang_mills_geometry import (
        geometry_source_density as ym_active_source_density,
        hamiltonian_density as ym_energy_density,
    )


@dataclass(frozen=True)
class SectorContribution:
    name: str
    energy: float
    active_source: float

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("sector name must be non-empty")
        if not math.isfinite(self.energy):
            raise ValueError("energy must be finite")
        if not math.isfinite(self.active_source):
            raise ValueError("active_source must be finite")

    @property
    def source_energy_difference(self) -> float:
        return self.active_source - self.energy

    @property
    def source_energy_ratio(self) -> float:
        if self.energy == 0.0:
            return math.inf if self.active_source != 0.0 else 1.0
        return self.active_source / self.energy


@dataclass(frozen=True)
class UnifiedSourceLedger:
    sectors: tuple[SectorContribution, ...]

    @property
    def total_energy(self) -> float:
        return sum(sector.energy for sector in self.sectors)

    @property
    def total_active_source(self) -> float:
        return sum(sector.active_source for sector in self.sectors)

    @property
    def source_energy_difference(self) -> float:
        return self.total_active_source - self.total_energy

    @property
    def source_energy_ratio(self) -> float:
        if self.total_energy == 0.0:
            return (
                math.inf
                if self.total_active_source != 0.0
                else 1.0
            )
        return self.total_active_source / self.total_energy

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {
            sector.name: {
                "energy": sector.energy,
                "active_source": sector.active_source,
                "difference": sector.source_energy_difference,
                "ratio": sector.source_energy_ratio,
            }
            for sector in self.sectors
        }


def scalar_sector_from_canonical_fields(
    phi: np.ndarray,
    momentum: np.ndarray,
    psi: np.ndarray,
    potential: MatterPotential,
    phi_velocity: np.ndarray | None = None,
    spatial_gradient_squared: np.ndarray | float = 0.0,
    name: str = "scalar_matter",
) -> SectorContribution:
    """Integrate scalar-matter energy and active source over the lattice."""
    phi = np.asarray(phi, dtype=complex)
    momentum = np.asarray(momentum, dtype=complex)
    psi = np.asarray(psi, dtype=float)

    source = float(
        np.sum(
            scalar_active_source_density(
                phi,
                momentum,
                psi,
                potential,
            )
        )
    )

    if phi_velocity is None:
        phi_velocity = np.exp(-4.0 * psi) * momentum

    energy_density = local_matter_energy_density(
        phi,
        np.asarray(phi_velocity, dtype=complex),
        psi,
        potential,
        spatial_gradient_squared=spatial_gradient_squared,
    )
    energy = float(np.sum(energy_density))

    return SectorContribution(
        name=name,
        energy=energy,
        active_source=source,
    )


def u1_sector(
    displacement: np.ndarray,
    magnetic: np.ndarray,
    psi: float,
    name: str = "u1_gauge",
) -> SectorContribution:
    energy = u1_energy_density(displacement, magnetic, psi)
    source = u1_active_source_density(displacement, magnetic, psi)
    return SectorContribution(name, energy, source)


def yang_mills_sector(
    displacement_components: np.ndarray,
    magnetic_components: np.ndarray,
    psi: float,
    name: str = "yang_mills",
) -> SectorContribution:
    energy = ym_energy_density(
        displacement_components,
        magnetic_components,
        psi,
    )
    source = ym_active_source_density(
        displacement_components,
        magnetic_components,
        psi,
    )
    return SectorContribution(name, energy, source)


def make_ledger(
    *sectors: SectorContribution,
) -> UnifiedSourceLedger:
    names = [sector.name for sector in sectors]
    if len(set(names)) != len(names):
        raise ValueError("sector names must be unique")
    return UnifiedSourceLedger(tuple(sectors))


def active_source_from_energy_and_integrated_stress(
    total_energy: float,
    integrated_spatial_stress: np.ndarray,
) -> float:
    stress = np.asarray(integrated_spatial_stress, dtype=float)
    if stress.shape != (3, 3):
        raise ValueError("integrated_spatial_stress must be 3x3")
    return float(total_energy + np.trace(stress))


def stationary_universal_source(
    total_energy: float,
    integrated_spatial_stress: np.ndarray,
    tolerance: float = 1e-12,
) -> float:
    """Return E if the total composite satisfies the von Laue condition."""
    stress = np.asarray(integrated_spatial_stress, dtype=float)
    if stress.shape != (3, 3):
        raise ValueError("integrated_spatial_stress must be 3x3")
    if np.max(np.abs(stress)) > tolerance:
        raise ValueError(
            "stationary universality requires the total von Laue condition"
        )
    return float(total_energy)


def binding_completion(
    constituent_energy: float,
    constituent_active_source: float,
    binding_energy: float,
    binding_integrated_stress_trace: float,
) -> SectorContribution:
    """Construct a binding sector contribution.

    The complete stationary composite can satisfy source=energy even when
    isolated constituent sectors do not, because binding stresses contribute
    through trace(T^ij).
    """
    active = binding_energy + binding_integrated_stress_trace
    return SectorContribution(
        name="binding",
        energy=binding_energy,
        active_source=active,
    )


def required_binding_stress_trace_for_universality(
    constituent_energy: float,
    constituent_active_source: float,
    binding_energy: float,
) -> float:
    """Trace of integrated binding stress required for total M_active=E."""
    return (
        constituent_energy
        - constituent_active_source
    )


def ledger_from_mapping(
    values: Mapping[str, tuple[float, float]],
) -> UnifiedSourceLedger:
    return make_ledger(
        *[
            SectorContribution(
                name=name,
                energy=pair[0],
                active_source=pair[1],
            )
            for name, pair in values.items()
        ]
    )
