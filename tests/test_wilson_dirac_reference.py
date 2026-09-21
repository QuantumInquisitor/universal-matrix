import math
import numpy as np

from src.wilson_dirac_reference import (
    ALPHA,
    BETA,
    analytic_positive_energy,
    brillouin_corners,
    doubler_corner_mass,
    eigenvalues,
    hamiltonian,
    zero_energy_corners,
)


def test_dirac_hamiltonian_is_hermitian():
    h = hamiltonian((0.2, -0.4, 0.7), mass=0.3, wilson_r=1.0)
    assert np.allclose(h, h.conj().T, atol=1e-14, rtol=0)


def test_dirac_matrices_square_to_identity():
    identity = np.eye(4)
    assert np.allclose(BETA @ BETA, identity, atol=1e-14, rtol=0)
    for alpha in ALPHA:
        assert np.allclose(alpha @ alpha, identity, atol=1e-14, rtol=0)


def test_numeric_spectrum_matches_analytic_energy():
    p = (0.2, 0.5, -0.7)
    energy = analytic_positive_energy(p, mass=0.4, wilson_r=0.8)
    values = eigenvalues(p, mass=0.4, wilson_r=0.8)

    assert np.allclose(
        values,
        [-energy, -energy, energy, energy],
        atol=1e-12,
        rtol=0,
    )


def test_naive_massless_spatial_lattice_has_eight_doublers():
    zeros = zero_energy_corners(mass=0.0, wilson_r=0.0)
    assert len(zeros) == 8
    assert set(zeros) == set(brillouin_corners())


def test_wilson_term_leaves_only_origin_massless():
    zeros = zero_energy_corners(mass=0.0, wilson_r=1.0)
    assert zeros == [(0.0, 0.0, 0.0)]


def test_wilson_corner_masses_increase_with_number_of_pi_components():
    assert doubler_corner_mass(0, mass=0.0, wilson_r=1.0) == 0.0
    assert doubler_corner_mass(1, mass=0.0, wilson_r=1.0) == 2.0
    assert doubler_corner_mass(2, mass=0.0, wilson_r=1.0) == 4.0
    assert doubler_corner_mass(3, mass=0.0, wilson_r=1.0) == 6.0


def test_small_momentum_recovers_continuum_massless_dispersion():
    eps = 1e-5
    p = (eps, 2*eps, -eps)
    lattice = analytic_positive_energy(p, mass=0.0, wilson_r=0.0)
    continuum = math.sqrt(sum(x*x for x in p))
    assert abs(lattice - continuum) / continuum < 1e-9
