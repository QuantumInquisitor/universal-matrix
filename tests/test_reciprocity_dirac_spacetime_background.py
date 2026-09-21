import math
import numpy as np

from src.reciprocity_dirac_spacetime_background import (
    SpacetimeReciprocityDirac,
    curved_norm,
    flat_norm,
    from_rescaled,
    hermiticity_residual,
    to_rescaled,
)


def test_local_rescaling_matches_curved_norm():
    rng = np.random.default_rng(1401)
    shape = (3,3,3)
    spinor = (
        rng.normal(size=shape+(4,))
        + 1j*rng.normal(size=shape+(4,))
    )
    psi = rng.normal(scale=0.2, size=shape)
    chi = to_rescaled(spinor, psi)

    assert math.isclose(
        curved_norm(spinor, psi),
        flat_norm(chi),
        rel_tol=0,
        abs_tol=1e-10,
    )
    assert np.allclose(
        from_rescaled(chi, psi),
        spinor,
        atol=1e-12,
        rtol=0,
    )


def test_instantaneous_operator_is_hermitian_for_spatially_varying_geometry():
    rng = np.random.default_rng(1402)
    shape = (3,3,3)
    a = (
        rng.normal(size=shape+(4,))
        + 1j*rng.normal(size=shape+(4,))
    )
    b = (
        rng.normal(size=shape+(4,))
        + 1j*rng.normal(size=shape+(4,))
    )
    psi = rng.normal(scale=0.15, size=shape)

    residual = hermiticity_residual(
        a,b,psi,mass=0.7,spacing=1.0
    )
    assert abs(residual) < 1e-10


def test_time_and_space_dependent_evolution_conserves_rescaled_norm():
    shape = (3,3,3)
    coords = np.indices(shape, dtype=float)
    spatial = 0.04 * (
        np.cos(2*np.pi*coords[0]/shape[0])
        + 0.5*np.sin(2*np.pi*coords[1]/shape[1])
    )

    def geometry(t):
        return spatial + 0.03*np.sin(0.6*t)

    rng = np.random.default_rng(1403)
    chi = (
        rng.normal(scale=0.02, size=shape+(4,))
        + 1j*rng.normal(scale=0.02, size=shape+(4,))
    )

    state = SpacetimeReciprocityDirac(
        chi=chi,
        geometry_function=geometry,
        mass=0.5,
    )

    n0 = state.norm
    for _ in range(400):
        state.step(0.001)

    assert abs(state.norm-n0)/n0 < 2e-10
    assert math.isclose(
        state.curved_norm,
        state.norm,
        rel_tol=0,
        abs_tol=1e-10,
    )


def test_static_geometry_is_valid_special_case():
    shape = (3,3,3)
    psi = np.zeros(shape)
    geometry = lambda t: psi
    chi = np.zeros(shape+(4,), dtype=complex)
    chi[1,1,1,0] = 1.0

    state = SpacetimeReciprocityDirac(
        chi=chi,
        geometry_function=geometry,
        mass=1.0,
    )
    n0=state.norm
    state.step(1e-4)
    assert abs(state.norm-n0) < 1e-12
