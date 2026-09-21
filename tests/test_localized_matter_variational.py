import math

from src.localized_matter_variational import (
    GaussianMatterCandidate,
    MatterPotential,
    scan_gaussian_candidates,
)


def test_gaussian_integrals_are_positive():
    candidate = GaussianMatterCandidate(
        amplitude=1.2,
        radius=3.0,
        omega=0.6,
    )
    assert candidate.i2 > 0
    assert candidate.gradient_integral > 0
    assert candidate.i4 > 0
    assert candidate.i6 > 0
    assert candidate.charge > 0
    assert candidate.energy > 0


def test_representative_candidate_lies_below_free_mass_threshold():
    candidate = GaussianMatterCandidate(
        amplitude=1.3,
        radius=4.0,
        omega=0.6,
        potential=MatterPotential(
            mass2=1.0,
            lambda4=-2.0,
            lambda6=1.0,
        ),
    )
    assert candidate.energy_per_charge < 1.0
    assert candidate.below_free_mass_threshold


def test_scan_finds_candidate_below_free_mass_threshold():
    best = scan_gaussian_candidates(
        amplitudes=[0.8, 1.0, 1.2, 1.3, 1.4],
        radii=[2.0, 3.0, 4.0, 5.0],
        omegas=[0.4, 0.5, 0.6, 0.7, 0.8],
        potential=MatterPotential(
            mass2=1.0,
            lambda4=-2.0,
            lambda6=1.0,
        ),
    )
    assert best.below_free_mass_threshold
    assert best.energy_per_charge < best.potential.free_mass


def test_charge_scales_linearly_with_omega_at_fixed_profile():
    a = GaussianMatterCandidate(1.1, 2.5, 0.4)
    b = GaussianMatterCandidate(1.1, 2.5, 0.8)
    assert math.isclose(b.charge / a.charge, 2.0, abs_tol=1e-15)


def test_positive_sextic_keeps_large_amplitude_energy_positive():
    candidate = GaussianMatterCandidate(
        amplitude=20.0,
        radius=1.0,
        omega=0.5,
        potential=MatterPotential(
            mass2=1.0,
            lambda4=-2.0,
            lambda6=1.0,
        ),
    )
    assert candidate.energy > 0
