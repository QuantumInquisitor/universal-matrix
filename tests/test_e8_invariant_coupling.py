from __future__ import annotations

from fractions import Fraction

import numpy as np

from src.e8_invariant_coupling import (
    E8ScalarCoupling,
    invariant_scalar_coupling,
    scalar_coupling_is_weyl_invariant,
)
from src.e8_state_audit import E8CartanState
from src.higher_dimensional_geometry import e8_roots_scaled
from src.su2_matter_doublet import (
    gauge_invariant_norm as su2_norm,
    gauge_transform_matter as su2_transform,
)
from src.su3_matter_triplet import (
    gauge_invariant_norm as su3_norm,
    gauge_transform_matter as su3_transform,
)
from src.unified_variational_action import (
    gauge_transform as u1_transform,
    global_u1_charge,
)


def _cartan_state() -> E8CartanState:
    return E8CartanState(
        (
            Fraction(1, 2),
            Fraction(-1, 2),
            Fraction(1),
            Fraction(0),
            Fraction(3, 2),
            Fraction(-1),
            Fraction(2),
            Fraction(-2),
        )
    )


def test_quadratic_scalar_coupling_is_invariant_under_every_e8_root_reflection():
    state = _cartan_state()
    coupling = E8ScalarCoupling(0.125)
    for root in e8_roots_scaled():
        assert scalar_coupling_is_weyl_invariant(state, root, 3.5, coupling)


def test_u1_gauge_invariant_norm_leaves_e8_coupling_unchanged():
    phi = np.array([[[1.0 + 2.0j]]])
    links = np.zeros((3, 1, 1, 1), dtype=float)
    alpha = np.array([[[0.73]]])

    before_scalar = global_u1_charge(phi)
    phi2, _ = u1_transform(phi, links, alpha)
    after_scalar = global_u1_charge(phi2)

    coupling = E8ScalarCoupling(0.2)
    state = _cartan_state()
    assert np.isclose(before_scalar, after_scalar)
    assert np.isclose(
        invariant_scalar_coupling(state, before_scalar, coupling),
        invariant_scalar_coupling(state, after_scalar, coupling),
    )


def test_su2_gauge_invariant_norm_leaves_e8_coupling_unchanged():
    psi = np.array([[[[1.0 + 0.5j, -0.25 + 0.75j]]]])
    transform = np.zeros((1, 1, 1, 2, 2), dtype=complex)
    transform[0, 0, 0] = np.array([[0.0, 1.0], [-1.0, 0.0]])

    before_scalar = su2_norm(psi)
    after_scalar = su2_norm(su2_transform(psi, transform))

    coupling = E8ScalarCoupling(-0.3)
    state = _cartan_state()
    assert np.isclose(before_scalar, after_scalar)
    assert np.isclose(
        invariant_scalar_coupling(state, before_scalar, coupling),
        invariant_scalar_coupling(state, after_scalar, coupling),
    )


def test_su3_gauge_invariant_norm_leaves_e8_coupling_unchanged():
    psi = np.array([[[[1.0 + 0.5j, -0.25 + 0.75j, 0.4 - 0.1j]]]])
    transform = np.zeros((1, 1, 1, 3, 3), dtype=complex)
    phases = np.array([0.2, -0.7, 0.5])
    transform[0, 0, 0] = np.diag(np.exp(1j * phases))

    before_scalar = su3_norm(psi)
    after_scalar = su3_norm(su3_transform(psi, transform))

    coupling = E8ScalarCoupling(0.4)
    state = _cartan_state()
    assert np.isclose(before_scalar, after_scalar)
    assert np.isclose(
        invariant_scalar_coupling(state, before_scalar, coupling),
        invariant_scalar_coupling(state, after_scalar, coupling),
    )


def test_zero_strength_decouples_e8_layer_exactly():
    state = _cartan_state()
    coupling = E8ScalarCoupling(0.0)
    assert invariant_scalar_coupling(state, 123.0, coupling) == 0.0
