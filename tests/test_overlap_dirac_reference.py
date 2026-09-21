import math
import numpy as np

from src.overlap_dirac_reference import (
    GAMMA,
    GAMMA5,
    I4,
    brillouin_corners,
    gamma5_hermiticity_residual,
    ginsparg_wilson_residual,
    modified_chiral_matrix,
    overlap_dirac,
    zero_corners,
)


def test_euclidean_gamma_clifford_algebra():
    for mu in range(4):
        for nu in range(4):
            anti=GAMMA[mu]@GAMMA[nu]+GAMMA[nu]@GAMMA[mu]
            expected=2.0*I4 if mu==nu else np.zeros((4,4),complex)
            assert np.allclose(anti,expected,atol=1e-14,rtol=0)


def test_gamma5_is_hermitian_and_squares_to_identity():
    assert np.allclose(GAMMA5,GAMMA5.conj().T,atol=1e-14,rtol=0)
    assert np.allclose(GAMMA5@GAMMA5,I4,atol=1e-14,rtol=0)


def test_overlap_operator_satisfies_ginsparg_wilson_relation():
    p=(0.2,-0.4,0.7,0.3)
    residual=ginsparg_wilson_residual(p,rho=1.1,wilson_r=1.0)
    assert np.linalg.norm(residual)<1e-12


def test_overlap_operator_has_gamma5_hermiticity():
    p=(0.3,0.1,-0.5,0.9)
    residual=gamma5_hermiticity_residual(p,rho=1.0,wilson_r=1.0)
    assert np.linalg.norm(residual)<1e-12


def test_only_origin_is_zero_among_brillouin_corners():
    zeros=zero_corners(rho=1.0,wilson_r=1.0)
    assert zeros==[(0.0,0.0,0.0,0.0)]
    assert len(brillouin_corners())==16


def test_nonzero_doubler_corners_are_lifted_to_two_rho():
    rho=1.0
    for p in brillouin_corners()[1:]:
        d=overlap_dirac(p,rho=rho,wilson_r=1.0)
        assert np.allclose(d,2.0*rho*I4,atol=1e-12,rtol=0)


def test_modified_chiral_matrix_squares_to_identity_free_case():
    p=(0.21,-0.33,0.17,0.44)
    gh=modified_chiral_matrix(p,rho=1.0,wilson_r=1.0)
    assert np.allclose(gh@gh,I4,atol=1e-12,rtol=0)


def test_overlap_zero_at_origin():
    d=overlap_dirac((0.0,0.0,0.0,0.0),rho=1.0,wilson_r=1.0)
    assert np.allclose(d,0.0,atol=1e-14,rtol=0)
