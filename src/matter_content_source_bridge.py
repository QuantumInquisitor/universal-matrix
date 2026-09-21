"""Bridge from localized classical matter to scalar content source charge.

From the unified static variational energy,

    E_chi = |grad chi|^2/(2*kappa_chi)
    E_int = -g_chi chi |Phi|^2,

variation gives

    -laplacian chi = kappa_chi * g_chi * |Phi|^2.

Therefore define the integrated scalar-content source charge

    Q_C = kappa_chi * g_chi * integral |Phi|^2 d^3x.

For the Gaussian time-harmonic matter candidate,

    integral |Phi|^2 = I2.

This module compares Q_C with the candidate total energy E.

A gravity-like universal coupling would require Q_C/E (or the appropriate
relativistic source analogue) to approach a composition/state-independent
constant.

The current matter ansatz does not guarantee that. This module exposes the
ratio instead of assuming universality.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

try:
    from .localized_matter_variational import GaussianMatterCandidate
except ImportError:
    from localized_matter_variational import GaussianMatterCandidate


def content_source_charge(
    integrated_matter_density: float,
    scalar_field_kappa: float,
    matter_content_coupling: float,
) -> float:
    if integrated_matter_density < 0:
        raise ValueError("integrated_matter_density must be non-negative")
    if scalar_field_kappa <= 0:
        raise ValueError("scalar_field_kappa must be positive")
    if matter_content_coupling < 0:
        raise ValueError("matter_content_coupling must be non-negative")

    return (
        scalar_field_kappa
        * matter_content_coupling
        * integrated_matter_density
    )


def gaussian_candidate_content_charge(
    candidate: GaussianMatterCandidate,
    scalar_field_kappa: float,
    matter_content_coupling: float,
) -> float:
    return content_source_charge(
        candidate.i2,
        scalar_field_kappa,
        matter_content_coupling,
    )


def source_charge_per_energy(
    candidate: GaussianMatterCandidate,
    scalar_field_kappa: float,
    matter_content_coupling: float,
) -> float:
    if candidate.energy <= 0:
        raise ValueError("candidate energy must be positive")
    return gaussian_candidate_content_charge(
        candidate,
        scalar_field_kappa,
        matter_content_coupling,
    ) / candidate.energy


def relative_source_per_energy_mismatch(
    candidate_a: GaussianMatterCandidate,
    candidate_b: GaussianMatterCandidate,
    scalar_field_kappa: float,
    matter_content_coupling: float,
) -> float:
    qa = source_charge_per_energy(
        candidate_a,
        scalar_field_kappa,
        matter_content_coupling,
    )
    qb = source_charge_per_energy(
        candidate_b,
        scalar_field_kappa,
        matter_content_coupling,
    )
    mean = 0.5 * (qa + qb)
    if mean == 0:
        return 0.0
    return (qa - qb) / mean


@dataclass(frozen=True)
class MatterSourceDiagnostic:
    candidate: GaussianMatterCandidate
    scalar_field_kappa: float
    matter_content_coupling: float

    @property
    def source_charge(self) -> float:
        return gaussian_candidate_content_charge(
            self.candidate,
            self.scalar_field_kappa,
            self.matter_content_coupling,
        )

    @property
    def source_charge_per_energy(self) -> float:
        return source_charge_per_energy(
            self.candidate,
            self.scalar_field_kappa,
            self.matter_content_coupling,
        )

    def snapshot(self) -> dict[str, float | bool | str]:
        return {
            "energy": self.candidate.energy,
            "u1_charge": self.candidate.charge,
            "content_source_charge": self.source_charge,
            "content_source_charge_per_energy": self.source_charge_per_energy,
            "below_free_mass_threshold": self.candidate.below_free_mass_threshold,
            "model_status": "experimental_matter_to_content_source_diagnostic",
        }
