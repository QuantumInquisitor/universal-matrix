import math

import numpy as np
from hypothesis import given, settings, strategies as st

from src import canonical_kernel as ck
from src.open_boundary_solver import GateFieldFlux, solve_open_gauss
from src.open_gauge_dynamics import curl, gradient


@given(
    n=st.integers(min_value=-10_000, max_value=10_000),
    power=st.integers(min_value=-500, max_value=500),
)
def test_route_inverse_property(n, power):
    routed = ck.route(n, power)
    assert ck.route(routed, -power) == n % ck.N_CORE


@given(n=st.integers(min_value=-10_000, max_value=10_000))
def test_polarity_is_involution_property(n):
    assert ck.polarity(ck.polarity(n)) == n % ck.N_CORE


@given(
    n=st.integers(min_value=0, max_value=ck.N_CORE - 1),
    d=st.integers(min_value=0, max_value=ck.N_CORE - 1),
)
def test_projection_delta_theorem_property(n, d):
    actual = (ck.register_address(n + d) - ck.register_address(n)) % ck.REGISTER_SIZE
    predicted = ck.projection_delta_theorem(n, d)
    assert actual == predicted


@settings(max_examples=30, deadline=None)
@given(
    nx=st.integers(min_value=2, max_value=5),
    ny=st.integers(min_value=2, max_value=5),
    nz=st.integers(min_value=2, max_value=5),
)
def test_open_dec_exactness_property(nx, ny, nz):
    rng = np.random.default_rng(nx * 100 + ny * 10 + nz)
    phi = rng.normal(size=(nx, ny, nz))
    faces = curl(gradient(phi))
    assert max(float(np.max(np.abs(v))) for v in faces.values()) < 1e-11


@settings(max_examples=20, deadline=None)
@given(
    nx=st.integers(min_value=2, max_value=5),
    ny=st.integers(min_value=2, max_value=5),
    nz=st.integers(min_value=2, max_value=5),
    q=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
)
def test_open_gauss_compatible_nonzero_charge_property(nx, ny, nz, q):
    rho = np.zeros((nx, ny, nz), dtype=float)
    rho[nx // 2, ny // 2, nz // 2] = q
    flux = GateFieldFlux(x_pos=q)
    solution = solve_open_gauss(rho, flux, tolerance=1e-10)
    assert abs(solution.compatibility_residual) < 1e-9
    assert solution.max_abs_gauss_residual(rho) < 1e-7
