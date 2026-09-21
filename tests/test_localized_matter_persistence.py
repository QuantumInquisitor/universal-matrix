import math
import numpy as np

from src.classical_matter_dynamics import ClassicalMatterDynamics
from src.localized_matter_persistence import (
    cartesian_radius_grid,
    evolve_persistence,
    interpolate_radial_profile,
    rms_radius,
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
