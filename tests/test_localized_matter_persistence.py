import math
import numpy as np
import pytest
from types import SimpleNamespace

from src.classical_matter_dynamics import ClassicalMatterDynamics
from src.localized_matter_persistence import (
    cartesian_radius_grid,
    evolve_persistence,
    interpolate_radial_profile,
    rms_radius,
    radial_solution_to_dynamics,
)
from src.localized_matter_variational import MatterPotential


def test_cartesian_radius_grid_is_zero_at_center_for_odd_shape():
    radii = cartesian_radius_grid((5, 5, 5), spacing=1.0)
    assert radii[2, 2, 2] == 0.0


def test_radial_interpolation_maps_center_and_exterior():
    r = np.array([0.0, 1.0, 2.0])
    f = np.array([2.0, 1.0, 0.0])
    grid = np.array([[[0.0, 0.5, 3.0]]])
    mapped = interpolate_radial_profile(r, f, grid)
    assert mapped[0, 0, 0] == 2.0
    assert mapped[0, 0, 1] == 1.5
    assert mapped[0, 0, 2] == 0.0


def test_rms_radius_is_finite_for_localized_profile():
    shape = (7, 7, 7)
    radii = cartesian_radius_grid(shape, spacing=0.5)
    phi = np.exp(-radii*radii).astype(complex)
    value = rms_radius(phi, spacing=0.5)
    assert 0.0 < value < 2.0


def test_controlled_free_mode_persistence_preserves_charge():
    shape = (5, 5, 5)
    amplitude = 1e-3
    phi = np.full(shape, amplitude + 0j, dtype=complex)
    momentum = 1j * phi
    links = np.zeros((3,) + shape)
    state = ClassicalMatterDynamics(
        phi=phi,
        momentum=momentum,
        links=links,
        potential=MatterPotential(
            mass2=1.0,
            lambda4=0.0,
            lambda6=1e-12,
        ),
    )

    report = evolve_persistence(
        state,
        steps=500,
        dt=0.002,
        spacing=1.0,
    )

    assert abs(report.relative_charge_drift) < 1e-10
    assert abs(report.relative_energy_drift) < 1e-5
    assert math.isfinite(report.radius_ratio)



def test_radial_mapper_propagates_spacing_into_dynamics():
    potential = MatterPotential(
        mass2=1.0,
        lambda4=-2.0,
        lambda6=1.0,
    )
    solution = SimpleNamespace(
        radius=np.array([0.0, 1.0, 2.0, 3.0]),
        profile=np.array([1.0, 0.7, 0.2, 0.0]),
        omega=0.8,
        potential=potential,
    )

    state = radial_solution_to_dynamics(
        solution,
        shape=(9, 9, 9),
        spacing=0.5,
    )

    assert state.lattice_spacing == pytest.approx(0.5)
    assert state.phi[4, 4, 4].real == pytest.approx(1.0)
    assert np.allclose(state.momentum, 1j * 0.8 * state.phi)


def test_persistence_rejects_diagnostic_spacing_mismatch():
    shape = (5, 5, 5)
    state = ClassicalMatterDynamics(
        phi=np.full(shape, 1e-3 + 0j, dtype=complex),
        momentum=np.full(shape, 1j * 1e-3, dtype=complex),
        links=np.zeros((3,) + shape),
        potential=MatterPotential(
            mass2=1.0,
            lambda4=0.0,
            lambda6=1e-12,
        ),
        lattice_spacing=0.5,
    )

    with pytest.raises(ValueError):
        evolve_persistence(
            state,
            steps=1,
            dt=0.001,
            spacing=1.0,
        )


def test_persistence_uses_state_spacing_when_not_repeated_explicitly():
    shape = (5, 5, 5)
    state = ClassicalMatterDynamics(
        phi=np.full(shape, 1e-3 + 0j, dtype=complex),
        momentum=np.full(shape, 1j * 1e-3, dtype=complex),
        links=np.zeros((3,) + shape),
        potential=MatterPotential(
            mass2=1.0,
            lambda4=0.0,
            lambda6=1e-12,
        ),
        lattice_spacing=0.5,
    )

    report = evolve_persistence(
        state,
        steps=10,
        dt=0.001,
    )

    assert math.isfinite(report.initial_rms_radius)
    assert abs(report.relative_charge_drift) < 1e-12
