import math

from src.gauge_dynamics import ROUTING_PERIOD
from src.gauge_hamiltonian import (
    U1HamiltonianState,
    energy_relative_drift,
    gauss_sum,
    weak_field_hamiltonian,
)


def test_zero_state_is_stationary():
    state = U1HamiltonianState.zeros(3, beta=1.0)
    state.evolve(0.05, 20)
    assert state.total_energy() == 0.0
    assert state.max_abs_gauss_residual() == 0.0


def test_total_divergence_vanishes_identically():
    state = U1HamiltonianState.zeros(4)
    state.routing_momenta[0][0] = 0.7
    state.routing_momenta[0][1] = -0.2
    state.scale_momenta[0][3] = 0.4
    state.scale_momenta[2][9] = -0.8
    assert abs(gauss_sum(state.gauss_divergence())) < 1e-12


def test_source_free_gauss_constraint_is_preserved():
    state = U1HamiltonianState.zeros(3, beta=1.2)

    # Start with a nontrivial gauge field but exactly zero conjugate momenta.
    state.field.routing_links[0][2] = 0.12
    state.field.routing_links[1][2] = -0.08
    state.field.scale_links[0][3] = 0.05
    state.field.scale_links[1][7] = -0.04

    before = state.max_abs_gauss_residual()
    state.evolve(0.01, 200)
    after = state.max_abs_gauss_residual()

    assert before < 1e-14
    assert after < 1e-10


def test_leapfrog_has_small_energy_drift_for_small_step():
    state = U1HamiltonianState.zeros(3, beta=0.9)
    state.field.routing_links[0][0] = 0.08
    state.field.routing_links[1][0] = -0.05
    state.scale_momenta[0][1] = 0.03

    initial = state.total_energy()
    state.evolve(0.002, 1000)
    final = state.total_energy()

    assert energy_relative_drift(initial, final) < 2e-4


def test_weak_field_hamiltonian_matches_compact_energy():
    state = U1HamiltonianState.zeros(2, beta=1.0)
    state.field.routing_links[0][0] = 1e-4
    state.field.routing_links[1][0] = -2e-4
    state.routing_momenta[0][1] = 3e-4

    exact = state.total_energy()
    weak = weak_field_hamiltonian(state)
    assert abs(exact - weak) / exact < 1e-7


def test_charge_residual_is_divergence_minus_charge():
    state = U1HamiltonianState.zeros(2)
    state.scale_momenta[0][5] = 0.25
    rho = [[0.0] * ROUTING_PERIOD for _ in range(2)]
    rho[0][5] = 0.25
    rho[1][5] = -0.25
    assert state.max_abs_gauss_residual(rho) < 1e-12


def test_magnetic_like_field_is_plaquette_curvature():
    state = U1HamiltonianState.zeros(2)
    state.field.routing_links[0][4] = 0.2
    curvature = state.magnetic_like_curvature()
    assert math.isclose(curvature[0][4], 0.2, rel_tol=0, abs_tol=1e-12)
