import math

import numpy as np
import pytest

from src.matrix_local_transition import (
    MatrixLocalTransition,
    gauge_transform_links,
    zero_link_field,
)


def test_uniform_phase_is_static_without_momentum():
    model = MatrixLocalTransition.zeros((3, 3, 3))
    model.phase.fill(0.7)

    assert np.allclose(model.force(), 0.0)
    assert model.interaction_energy() == pytest.approx(0.0)


def test_force_is_strictly_nearest_neighbor_for_local_phase_defect():
    model = MatrixLocalTransition.zeros((5, 5, 5))
    center = (2, 2, 2)
    model.phase[center] = 0.2

    force = model.force()
    support = set(map(tuple, np.argwhere(np.abs(force) > 1e-14)))

    assert support == {
        center,
        (1, 2, 2),
        (3, 2, 2),
        (2, 1, 2),
        (2, 3, 2),
        (2, 2, 1),
        (2, 2, 3),
    }


def test_pairwise_exchange_conserves_total_momentum_rate():
    rng = np.random.default_rng(1234)
    model = MatrixLocalTransition.zeros((4, 3, 3))
    model.phase[:] = rng.normal(scale=0.4, size=model.shape)
    for axis in model.links:
        model.links[axis][:] = rng.normal(
            scale=0.2,
            size=model.links[axis].shape,
        )

    assert float(np.sum(model.force())) == pytest.approx(0.0, abs=1e-12)


def test_gauge_transform_preserves_link_deltas_energy_and_force():
    rng = np.random.default_rng(42)
    model = MatrixLocalTransition.zeros((3, 4, 3), coupling=1.7)
    model.phase[:] = rng.normal(scale=0.7, size=model.shape)
    model.momentum[:] = rng.normal(scale=0.2, size=model.shape)
    for axis in model.links:
        model.links[axis][:] = rng.normal(
            scale=0.4,
            size=model.links[axis].shape,
        )

    alpha = rng.normal(scale=0.5, size=model.shape)
    transformed = model.gauge_transform(alpha)

    original_delta = model.link_deltas()
    transformed_delta = transformed.link_deltas()

    for axis in original_delta:
        # Link angles are compact, so compare through exp(i delta).
        assert np.allclose(
            np.exp(1j * original_delta[axis]),
            np.exp(1j * transformed_delta[axis]),
            atol=1e-12,
        )

    assert transformed.energy() == pytest.approx(model.energy(), abs=1e-12)
    assert np.allclose(transformed.force(), model.force(), atol=1e-12)


def test_explicit_link_transform_matches_model_gauge_transform():
    model = MatrixLocalTransition.zeros((3, 3, 3))
    alpha = np.arange(27, dtype=float).reshape(3, 3, 3) * 0.01

    transformed_links = gauge_transform_links(
        model.links,
        alpha,
        boundary_mode="open",
    )
    transformed = model.gauge_transform(alpha)

    for axis in transformed_links:
        assert np.allclose(transformed.links[axis], transformed_links[axis])


def test_weak_field_force_matches_open_discrete_laplacian():
    model = MatrixLocalTransition.zeros((4, 4, 4), coupling=2.5)
    rng = np.random.default_rng(7)
    model.phase[:] = rng.normal(scale=1e-5, size=model.shape)

    expected = np.zeros(model.shape)

    # Open-boundary graph Laplacian with sign convention
    # force = kappa * sum_neighbors(phi_neighbor - phi_site).
    phi = model.phase
    expected[:-1, :, :] += phi[1:, :, :] - phi[:-1, :, :]
    expected[1:, :, :] += phi[:-1, :, :] - phi[1:, :, :]
    expected[:, :-1, :] += phi[:, 1:, :] - phi[:, :-1, :]
    expected[:, 1:, :] += phi[:, :-1, :] - phi[:, 1:, :]
    expected[:, :, :-1] += phi[:, :, 1:] - phi[:, :, :-1]
    expected[:, :, 1:] += phi[:, :, :-1] - phi[:, :, 1:]
    expected *= model.coupling

    assert np.allclose(model.linearized_force(), expected, atol=1e-14)
    assert np.allclose(model.force(), expected, atol=1e-12)


def test_periodic_model_conserves_total_force_and_is_gauge_invariant():
    rng = np.random.default_rng(99)
    model = MatrixLocalTransition.zeros(
        (3, 3, 4),
        boundary_mode="periodic",
    )
    model.phase[:] = rng.normal(scale=0.4, size=model.shape)
    for axis in model.links:
        model.links[axis][:] = rng.normal(
            scale=0.3,
            size=model.links[axis].shape,
        )

    assert np.sum(model.force()) == pytest.approx(0.0, abs=1e-12)

    transformed = model.gauge_transform(
        rng.normal(scale=0.5, size=model.shape)
    )
    assert transformed.energy() == pytest.approx(model.energy(), abs=1e-12)
    assert np.allclose(transformed.force(), model.force(), atol=1e-12)


def test_lattice_wave_speed_is_set_by_coupling_over_inertia():
    model = MatrixLocalTransition.zeros(
        (3, 3, 3),
        coupling=9.0,
        inertia=4.0,
    )
    assert model.lattice_wave_speed == pytest.approx(1.5)


def test_leapfrog_preserves_total_momentum():
    rng = np.random.default_rng(11)
    model = MatrixLocalTransition.zeros((4, 4, 4))
    model.phase[:] = rng.normal(scale=0.1, size=model.shape)
    model.momentum[:] = rng.normal(scale=0.05, size=model.shape)

    initial = model.total_momentum()
    model.leapfrog(0.01, steps=500)

    assert model.total_momentum() == pytest.approx(initial, abs=1e-11)


def test_leapfrog_has_small_bounded_energy_error():
    model = MatrixLocalTransition.zeros((4, 4, 4))
    model.phase[2, 2, 2] = 0.15
    model.momentum[1, 2, 2] = 0.05

    initial = model.energy()
    model.leapfrog(0.01, steps=1000)
    final = model.energy()

    relative_error = abs(final - initial) / initial
    assert relative_error < 2e-4


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        MatrixLocalTransition.zeros((1, 3, 3))
    with pytest.raises(ValueError):
        MatrixLocalTransition.zeros((3, 3, 3), coupling=0.0)
    with pytest.raises(ValueError):
        MatrixLocalTransition.zeros((3, 3, 3), inertia=-1.0)

    model = MatrixLocalTransition.zeros((3, 3, 3))
    with pytest.raises(ValueError):
        model.leapfrog(0.0)
    with pytest.raises(ValueError):
        model.leapfrog(0.1, steps=0)
