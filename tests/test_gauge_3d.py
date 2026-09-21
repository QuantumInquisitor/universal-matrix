import math

from src.gauge_3d import (
    AXES,
    U13DField,
    U13DHamiltonian,
    divergence,
    forward_divergence,
    max_abs_scalar,
)


def test_3d_local_gauge_invariance_of_plaquettes():
    field = U13DField.zeros((3, 3, 3), beta=1.2)
    field.links["x"][0][0][0] = 0.2
    field.links["y"][1][0][0] = -0.17
    field.links["z"][1][1][0] = 0.11

    alpha = [
        [[0.03 * (1 + i + 2*j + 3*k) for k in range(3)] for j in range(3)]
        for i in range(3)
    ]
    transformed = field.gauge_transform(alpha)

    for plane in (("x","y"),("y","z"),("z","x")):
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    assert abs(
                        field.plaquette(plane,(i,j,k))
                        - transformed.plaquette(plane,(i,j,k))
                    ) < 1e-12

    assert abs(field.wilson_energy() - transformed.wilson_energy()) < 1e-12


def test_discrete_divergence_of_magnetic_curvature_vanishes():
    field = U13DField.zeros((4,4,4))
    field.links["x"][0][0][0] = 0.1
    field.links["y"][1][2][3] = -0.07
    field.links["z"][3][1][2] = 0.05
    b = field.magnetic_components()
    divb = forward_divergence(b, field.shape)
    assert max_abs_scalar(divb) < 1e-12


def test_gauss_constraint_preserved_under_weak_evolution():
    state = U13DHamiltonian.zeros((4,4,4), beta=1.0)
    state.field.links["x"][0][0][0] = 1e-3
    state.field.links["y"][0][0][0] = -8e-4
    state.field.links["z"][1][0][0] = 4e-4

    before = max_abs_scalar(state.gauss())
    for _ in range(100):
        state.leapfrog_weak(0.01)
    after = max_abs_scalar(state.gauss())

    assert before < 1e-14
    assert after < 1e-10


def test_transverse_plane_wave_has_expected_lattice_acceleration():
    n = 12
    beta = 1.7
    state = U13DHamiltonian.zeros((n, 2, 2), beta=beta)
    mode = 2
    q = 2.0 * math.pi * mode / n
    amp = 1e-7

    # A_y varies only along x: transverse plane wave.
    for x in range(n):
        state.field.links["y"][x][0][0] = amp * math.cos(q*x)
        state.field.links["y"][x][0][1] = amp * math.cos(q*x)
        state.field.links["y"][x][1][0] = amp * math.cos(q*x)
        state.field.links["y"][x][1][1] = amp * math.cos(q*x)

    force = state.weak_force()
    omega2 = 4.0 * beta * math.sin(q/2.0)**2

    for x in range(n):
        expected = -omega2 * amp * math.cos(q*x)
        assert math.isclose(
            force["y"][x][0][0],
            expected,
            rel_tol=0,
            abs_tol=1e-16,
        )


def test_weak_magnetic_energy_matches_wilson_for_small_fields():
    field = U13DField.zeros((3,3,3), beta=0.8)
    field.links["x"][0][0][0] = 1e-5
    exact = field.wilson_energy()
    weak = field.weak_magnetic_energy()
    assert abs(exact-weak) / exact < 1e-8
