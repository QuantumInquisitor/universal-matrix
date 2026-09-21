import math

from src.localized_matter_variational import (
    GaussianMatterCandidate,
    MatterPotential,
)
from src.matter_content_source_bridge import (
    gaussian_candidate_content_charge,
    relative_source_per_energy_mismatch,
    source_charge_per_energy,
)


POTENTIAL = MatterPotential(
    mass2=1.0,
    lambda4=-2.0,
    lambda6=1.0,
)


def test_content_source_charge_is_proportional_to_i2():
    candidate = GaussianMatterCandidate(
        amplitude=1.2,
        radius=3.0,
        omega=0.6,
        potential=POTENTIAL,
    )
    q = gaussian_candidate_content_charge(
        candidate,
        scalar_field_kappa=0.8,
        matter_content_coupling=0.4,
    )
    assert math.isclose(q, 0.32 * candidate.i2, abs_tol=1e-14)


def test_source_charge_per_energy_is_positive():
    candidate = GaussianMatterCandidate(
        amplitude=1.3,
        radius=4.0,
        omega=0.6,
        potential=POTENTIAL,
    )
    ratio = source_charge_per_energy(candidate, 1.0, 0.2)
    assert ratio > 0


def test_source_per_energy_is_not_automatically_universal_across_profiles():
    a = GaussianMatterCandidate(
        amplitude=1.0,
        radius=2.0,
        omega=0.5,
        potential=POTENTIAL,
    )
    b = GaussianMatterCandidate(
        amplitude=1.4,
        radius=5.0,
        omega=0.7,
        potential=POTENTIAL,
    )
    mismatch = relative_source_per_energy_mismatch(
        a,
        b,
        scalar_field_kappa=1.0,
        matter_content_coupling=0.3,
    )
    assert abs(mismatch) > 1e-3


def test_same_candidate_has_zero_source_per_energy_mismatch():
    a = GaussianMatterCandidate(
        amplitude=1.2,
        radius=3.0,
        omega=0.6,
        potential=POTENTIAL,
    )
    mismatch = relative_source_per_energy_mismatch(
        a,
        a,
        scalar_field_kappa=1.0,
        matter_content_coupling=0.3,
    )
    assert mismatch == 0.0
