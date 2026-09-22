import math

import numpy as np
import pytest

from src.matrix_polarity_rotor_transition import (
    MatrixPolarityRotorTransition,
    effective_phase_field,
)


def test_independent_phase_encodes_branch_as_exact_pi_offset():
    phase = np.array([[[0.2, 0.2]]])
    bits = np.array([[[0, 1]]])

    eff = effective_phase_field(phase, bits, "independent")

    assert math.cos(eff[0, 0, 1]) == pytest.approx(-math.cos(eff[0, 0, 0]))
    assert math.sin(eff[0, 0, 1]) == pytest.approx(-math.sin(eff[0, 0, 0]))


def test_clock_representation_does_not_apply_branch_offset_again():
    phase = np.array([[[0.2, 0.2]]])
    bits = np.array([[[0, 1]]])

    eff = effective_phase_field(phase, bits, "canonical_clock")

    assert np.allclose(eff, phase)


def test_opposite_branch_equal_base_phase_is_pi_frustrated_link():
    model = MatrixPolarityRotorTransition.zeros((2, 2, 2), coupling=3.0)
    model.polarity_bits[1, 0, 0] = 1

    deltas = model.link_deltas()
    assert abs(abs(deltas["x"][0, 0, 0]) - math.pi) < 1e-12
    assert model.interaction_energy() == pytest.approx(6.0)


def test_like_branch_uniform_phase_has_zero_interaction_energy():
    model = MatrixPolarityRotorTransition.zeros((3, 2, 2), coupling=2.0)
    model.phase.fill(0.31)
    model.polarity_bits.fill(1)

    assert model.interaction_energy() == pytest.approx(0.0, abs=1e-12)
    assert np.allclose(model.force(), 0.0, atol=1e-12)


def test_global_branch_flip_is_exact_energy_symmetry():
    rng = np.random.default_rng(5)
    model = MatrixPolarityRotorTransition.zeros((3, 3, 3), coupling=1.7)
    model.phase[:] = rng.normal(scale=0.4, size=model.shape)
    model.momentum[:] = rng.normal(scale=0.2, size=model.shape)
    model.polarity_bits[:] = rng.integers(0, 2, size=model.shape)

    before_energy = model.energy()
    before_force = model.force().copy()

    model.flip_polarity()

    assert model.energy() == pytest.approx(before_energy, abs=1e-12)
    assert np.allclose(model.force(), before_force, atol=1e-12)


def test_local_branch_flip_changes_only_incident_link_response():
    model = MatrixPolarityRotorTransition.zeros((5, 5, 5))
    center = (2, 2, 2)
    mask = np.zeros(model.shape, dtype=bool)
    mask[center] = True
    model.flip_polarity(mask)

    support = set(map(tuple, np.argwhere(np.abs(model.force()) > 1e-12)))
    assert support == set()

    model.phase[center] = 0.1
    support = set(map(tuple, np.argwhere(np.abs(model.force()) > 1e-12)))
    assert support == {
        center,
        (1, 2, 2),
        (3, 2, 2),
        (2, 1, 2),
        (2, 3, 2),
        (2, 2, 1),
        (2, 2, 3),
    }


def test_gauge_transform_preserves_polarity_rotor_energy_and_force():
    rng = np.random.default_rng(12)
    model = MatrixPolarityRotorTransition.zeros((3, 4, 3), coupling=1.3)
    model.phase[:] = rng.normal(scale=0.5, size=model.shape)
    model.momentum[:] = rng.normal(scale=0.2, size=model.shape)
    model.polarity_bits[:] = rng.integers(0, 2, size=model.shape)
    for axis in model.links:
        model.links[axis][:] = rng.normal(scale=0.3, size=model.links[axis].shape)

    transformed = model.gauge_transform(
        rng.normal(scale=0.4, size=model.shape)
    )

    assert transformed.energy() == pytest.approx(model.energy(), abs=1e-12)
    assert np.allclose(transformed.force(), model.force(), atol=1e-12)
    assert np.array_equal(transformed.polarity_bits, model.polarity_bits)


def test_clock_mode_prevents_branch_double_counting_in_hamiltonian():
    independent = MatrixPolarityRotorTransition.zeros(
        (2, 2, 2),
        coupling=2.0,
        phase_representation="independent",
    )
    clock = MatrixPolarityRotorTransition.zeros(
        (2, 2, 2),
        coupling=2.0,
        phase_representation="canonical_clock",
    )
    independent.polarity_bits[1, 0, 0] = 1
    clock.polarity_bits[1, 0, 0] = 1

    assert independent.interaction_energy() == pytest.approx(4.0)
    assert clock.interaction_energy() == pytest.approx(0.0)


def test_leapfrog_conserves_total_momentum_and_has_bounded_energy_error():
    model = MatrixPolarityRotorTransition.zeros((4, 4, 4))
    model.phase[2, 2, 2] = 0.15
    model.polarity_bits[1, 2, 2] = 1
    model.momentum[1, 2, 2] = 0.05

    p0 = model.total_momentum()
    e0 = model.energy()
    model.leapfrog(0.005, steps=1000)

    assert model.total_momentum() == pytest.approx(p0, abs=1e-10)
    assert abs(model.energy() - e0) / e0 < 5e-4


def test_invalid_polarity_and_representation_are_rejected():
    phase = np.zeros((2, 2, 2))

    with pytest.raises(ValueError):
        effective_phase_field(
            phase,
            np.full((2, 2, 2), 2),
            "independent",
        )

    with pytest.raises(ValueError):
        MatrixPolarityRotorTransition.zeros(
            (2, 2, 2),
            phase_representation="unknown",
        )
