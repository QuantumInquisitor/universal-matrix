import math

import numpy as np

from src.u1_weyl_gauge_orbit import (
    gauge_endpoint_subspace_residual,
    gauge_orbit_holonomy,
    gauge_orbit_holonomy_from_bases,
    gauge_orbit_measure_phase,
    gauge_orbit_weyl_bases,
    holonomy_unitarity_residual,
    infinitesimal_gauge_measure_response,
)


def _background(seed=2601):
    shape = (2, 2, 1, 1)
    rng = np.random.default_rng(seed)
    links = rng.normal(
        scale=0.012,
        size=(4,) + shape,
    )
    alpha = rng.normal(
        scale=0.08,
        size=shape,
    )
    return links, alpha


def _random_unitary(n, seed):
    rng = np.random.default_rng(seed)
    z = (
        rng.normal(size=(n, n))
        + 1j * rng.normal(size=(n, n))
    )
    q, r = np.linalg.qr(z)
    diagonal = np.diag(r)
    phases = np.ones_like(diagonal, dtype=complex)
    mask = np.abs(diagonal) > 0
    phases[mask] = diagonal[mask] / np.abs(diagonal[mask])
    return q @ np.diag(np.conj(phases))


def test_charge_q_endpoint_subspace_is_exact_gauge_transform():
    links, alpha = _background(2602)

    residual = gauge_endpoint_subspace_residual(
        links,
        alpha,
        charge=2.0,
        chirality=-1,
    )
    assert residual < 1e-8


def test_gauge_orbit_holonomy_is_unitary():
    links, alpha = _background(2603)

    holonomy = gauge_orbit_holonomy(
        links,
        alpha,
        charge=1.0,
        chirality=-1,
        steps=6,
    )
    assert holonomy_unitarity_residual(holonomy) < 1e-9


def test_zero_gauge_parameter_has_zero_measure_phase():
    links, alpha = _background(2604)

    phase = gauge_orbit_measure_phase(
        links,
        np.zeros_like(alpha),
        charge=1.0,
        chirality=-1,
        steps=4,
    )
    assert abs(phase) < 1e-10


def test_neutral_fermion_has_zero_gauge_orbit_phase():
    links, alpha = _background(2605)

    phase = gauge_orbit_measure_phase(
        links,
        alpha,
        charge=0.0,
        chirality=-1,
        steps=5,
    )
    assert abs(phase) < 1e-10


def test_gauge_orbit_phase_is_internal_basis_invariant():
    links, alpha = _background(2606)

    bases = gauge_orbit_weyl_bases(
        links,
        alpha,
        charge=1.0,
        chirality=-1,
        steps=5,
    )
    reference = gauge_orbit_holonomy_from_bases(
        bases,
        alpha,
        charge=1.0,
    )
    reference_phase = np.angle(np.linalg.det(reference))

    rotated = []
    for i, basis in enumerate(bases):
        rotated.append(
            basis
            @ _random_unitary(
                basis.shape[1],
                seed=2700 + i,
            )
        )

    transformed = gauge_orbit_holonomy_from_bases(
        rotated,
        alpha,
        charge=1.0,
    )
    transformed_phase = np.angle(
        np.linalg.det(transformed)
    )

    wrapped = (
        transformed_phase
        - reference_phase
        + math.pi
    ) % (2.0 * math.pi) - math.pi
    assert abs(wrapped) < 1e-8


def test_path_refinement_gives_stable_small_gauge_phase():
    links, alpha = _background(2607)
    alpha = 0.2 * alpha

    phase4 = gauge_orbit_measure_phase(
        links,
        alpha,
        charge=1.0,
        chirality=-1,
        steps=4,
    )
    phase8 = gauge_orbit_measure_phase(
        links,
        alpha,
        charge=1.0,
        chirality=-1,
        steps=8,
    )

    wrapped = (
        phase8 - phase4 + math.pi
    ) % (2.0 * math.pi) - math.pi
    assert abs(wrapped) < 2e-5


def test_infinitesimal_measure_response_is_finite():
    links, alpha = _background(2608)

    response = infinitesimal_gauge_measure_response(
        links,
        alpha,
        charge=1.0,
        chirality=-1,
        epsilon=5e-4,
        steps=5,
    )
    assert math.isfinite(response)
