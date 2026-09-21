import numpy as np

from src.open_gauge_dynamics import (
    OpenU1Hamiltonian,
    curl,
    curl_adjoint,
    divergence,
    gradient,
    inner_faces,
    inner_links,
    zero_faces,
    zero_links,
)


def test_discrete_exactness_curl_gradient_is_zero():
    rng = np.random.default_rng(1)
    phi = rng.normal(size=(5,4,3))
    faces = curl(gradient(phi))
    assert max(float(np.max(np.abs(v))) for v in faces.values()) < 1e-12


def test_curl_adjoint_identity():
    shape = (5,4,3)
    rng = np.random.default_rng(2)
    a = zero_links(shape)
    f = zero_faces(shape)
    for key in a:
        a[key][...] = rng.normal(size=a[key].shape)
    for key in f:
        f[key][...] = rng.normal(size=f[key].shape)

    lhs = inner_faces(curl(a), f)
    rhs = inner_links(a, curl_adjoint(f, shape))
    assert abs(lhs-rhs) < 1e-11


def test_magnetic_force_has_zero_divergence():
    state = OpenU1Hamiltonian.zeros((5,4,3), beta=1.7)
    rng = np.random.default_rng(3)
    for axis in state.links:
        state.links[axis][...] = rng.normal(scale=0.1, size=state.links[axis].shape)
    force = state.weak_force()
    assert np.max(np.abs(divergence(force, state.shape))) < 1e-11


def test_source_free_gauss_is_preserved():
    state = OpenU1Hamiltonian.zeros((5,4,3), beta=1.0)
    rng = np.random.default_rng(4)
    for axis in state.links:
        state.links[axis][...] = rng.normal(scale=1e-3, size=state.links[axis].shape)

    before = np.max(np.abs(state.gauss()))
    for _ in range(100):
        state.leapfrog(0.01)
    after = np.max(np.abs(state.gauss()))

    assert before < 1e-14
    assert after < 1e-10


def test_transverse_mode_acceleration_is_lattice_wave():
    n = 16
    state = OpenU1Hamiltonian.zeros((n,3,3), beta=1.5)
    mode = 2
    q = np.pi * mode / (n - 1)
    amp = 1e-7

    # Open-domain cosine-like transverse test, inspect away from x boundaries.
    x = np.arange(n)
    profile = amp * np.cos(q*x)
    for j in range(state.links["y"].shape[1]):
        for k in range(state.links["y"].shape[2]):
            state.links["y"][:, j, k] = profile
    force = state.weak_force()

    # Interior second difference has eigenvalue -4 sin^2(q/2).
    omega2 = 4.0 * state.beta * np.sin(q/2.0)**2
    for i in range(2, n-2):
        assert abs(force["y"][i,0,1] + omega2*profile[i]) < 1e-15
