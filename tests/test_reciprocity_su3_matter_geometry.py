import math
import numpy as np

from src.reciprocity_su3_matter_geometry import (
    SU3MatterReciprocityDynamics,
    matter_geometry_source,
    non_geometry_energy,
    total_geometry_source,
    total_energy,
)
from src.su3_lattice_gauge import (
    identity_links,
    random_site_gauge_transform,
)
from src.su3_matter_gauge_dynamics import (
    SU3ScalarMatterParameters,
    gauge_transform_state,
)


def _small_state(seed=1301):
    rng = np.random.default_rng(seed)
    shape = (1,1,1)
    geometry = np.array([[[0.07]]], dtype=float)
    geometry_momentum = np.array([[[0.01]]], dtype=float)
    matter = (
        rng.normal(scale=0.03, size=shape + (3,))
        + 1j*rng.normal(scale=0.03, size=shape + (3,))
    )
    matter_momentum = (
        rng.normal(scale=0.02, size=shape + (3,))
        + 1j*rng.normal(scale=0.02, size=shape + (3,))
    )
    links = identity_links(shape)
    electric = rng.normal(
        scale=0.01,
        size=(3,) + shape + (8,),
    )
    return (
        geometry,
        geometry_momentum,
        matter,
        matter_momentum,
        links,
        electric,
    )


def test_total_geometry_source_matches_negative_energy_derivative():
    (
        geometry,
        _,
        matter,
        matter_momentum,
        links,
        electric,
    ) = _small_state()

    params = SU3ScalarMatterParameters(
        mass2=0.8,
        lambda4=0.15,
    )
    beta = 0.4

    source = total_geometry_source(
        geometry,
        matter,
        matter_momentum,
        links,
        electric,
        beta,
        params,
    )

    eps = 1e-7
    plus = geometry.copy()
    minus = geometry.copy()
    plus[0,0,0] += eps
    minus[0,0,0] -= eps

    derivative = (
        non_geometry_energy(
            plus,
            matter,
            matter_momentum,
            links,
            electric,
            beta,
            params,
        )
        - non_geometry_energy(
            minus,
            matter,
            matter_momentum,
            links,
            electric,
            beta,
            params,
        )
    ) / (2.0*eps)

    assert math.isclose(
        source[0,0,0],
        -derivative,
        rel_tol=2e-6,
        abs_tol=2e-6,
    )


def test_full_energy_is_locally_su3_gauge_invariant():
    (
        geometry,
        geometry_momentum,
        matter,
        matter_momentum,
        links,
        electric,
    ) = _small_state(1302)

    params = SU3ScalarMatterParameters(
        mass2=0.7,
        lambda4=0.1,
    )
    beta = 0.5
    kappa = 0.9

    e0 = total_energy(
        geometry,
        geometry_momentum,
        matter,
        matter_momentum,
        links,
        electric,
        kappa,
        beta,
        params,
    )

    transforms = random_site_gauge_transform(
        geometry.shape,
        np.random.default_rng(1303),
    )
    m2,p2,l2,e2 = gauge_transform_state(
        matter,
        matter_momentum,
        links,
        electric,
        transforms,
    )

    e1 = total_energy(
        geometry,
        geometry_momentum,
        m2,p2,l2,e2,
        kappa,beta,params,
    )

    assert math.isclose(e0,e1,rel_tol=0,abs_tol=1e-10)


def test_small_step_has_controlled_energy_drift():
    state = SU3MatterReciprocityDynamics(
        *_small_state(1304),
        kappa=0.8,
        beta=0.3,
        matter_params=SU3ScalarMatterParameters(
            mass2=0.6,
            lambda4=0.05,
        ),
    )

    e0 = state.energy
    for _ in range(20):
        state.step(1e-5)

    assert abs(state.energy-e0)/abs(e0) < 2e-5


def test_gauss_residual_remains_finite_under_coupled_step():
    state = SU3MatterReciprocityDynamics(
        *_small_state(1305),
        kappa=1.0,
        beta=0.2,
    )

    before = state.max_gauss
    state.step(1e-5)
    after = state.max_gauss

    assert math.isfinite(before)
    assert math.isfinite(after)


def test_matter_source_reduces_to_rest_energy_for_free_rest_mode():
    shape=(1,1,1)
    amplitude=0.2
    mass=1.3
    matter=np.zeros(shape+(3,),dtype=complex)
    matter[0,0,0,0]=amplitude
    momentum=np.zeros_like(matter)
    momentum[0,0,0,0]=1j*mass*amplitude
    geometry=np.zeros(shape)
    params=SU3ScalarMatterParameters(
        mass2=mass**2,
        lambda4=0.0,
    )

    source=matter_geometry_source(
        matter,
        momentum,
        geometry,
        params,
    )[0,0,0]

    energy=(
        abs(momentum[0,0,0,0])**2
        + mass**2*amplitude**2
    )

    assert math.isclose(source,energy,rel_tol=0,abs_tol=1e-15)
