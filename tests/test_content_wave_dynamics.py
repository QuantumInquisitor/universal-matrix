import math
import numpy as np
import pytest

from src.content_wave_dynamics import (
    ContentWaveField,
    interior_laplacian,
    sponge_profile,
)


def test_static_manufactured_mode_satisfies_discrete_field_equation():
    shape = (9, 9, 9)
    kappa = 0.7
    field = ContentWaveField(
        shape=shape,
        wave_speed=1.0,
        source_coupling=kappa,
        spacing=1.0,
    )

    x = np.arange(shape[0])
    y = np.arange(shape[1])
    z = np.arange(shape[2])
    sx = np.sin(np.pi * x / (shape[0] - 1))
    sy = np.sin(np.pi * y / (shape[1] - 1))
    sz = np.sin(np.pi * z / (shape[2] - 1))
    chi = sx[:, None, None] * sy[None, :, None] * sz[None, None, :]

    lap = interior_laplacian(chi)
    rho = np.zeros(shape)
    rho[1:-1, 1:-1, 1:-1] = -lap[1:-1, 1:-1, 1:-1] / kappa

    assert np.min(rho) >= -1e-14
    rho = np.maximum(rho, 0.0)

    field.potential[...] = chi
    field.set_source_density(rho)

    assert field.max_static_residual() < 1e-12


def test_cfl_guard_rejects_unstable_step():
    field = ContentWaveField((7, 7, 7), wave_speed=2.0, spacing=0.5)
    with pytest.raises(ValueError):
        field.step(field.max_stable_dt() * 1.01)


def test_localized_initial_pulse_does_not_instantly_fill_domain():
    field = ContentWaveField((11, 11, 11), wave_speed=1.0)
    field.potential[5, 5, 5] = 1.0

    field.step(0.2)

    assert field.potential[5, 5, 5] != 0.0
    assert field.potential[1, 1, 1] == 0.0
    assert field.potential[9, 9, 9] == 0.0


def test_source_free_energy_is_nearly_conserved_without_sponge():
    field = ContentWaveField((15, 7, 7), wave_speed=1.0, sponge_width=0)
    x = np.arange(15)
    mode = np.sin(np.pi * x / 14.0)
    field.potential[:, 3, 3] = 1e-3 * mode
    field._enforce_boundary()

    e0 = field.energy()
    for _ in range(200):
        field.step(0.05)
    e1 = field.energy()

    assert abs(e1 - e0) / e0 < 0.03


def test_sponge_profile_is_largest_at_boundary():
    damping = sponge_profile((9, 9, 9), width=3, strength=2.0)
    assert damping[0, 4, 4] == 2.0
    assert damping[4, 4, 4] == 0.0
    assert damping[1, 4, 4] < damping[0, 4, 4]


def test_positive_source_initially_accelerates_potential_positive():
    field = ContentWaveField(
        (7, 7, 7),
        wave_speed=1.0,
        source_coupling=0.8,
    )
    rho = np.zeros((7, 7, 7))
    rho[3, 3, 3] = 1.0
    field.set_source_density(rho)

    a = field.acceleration()
    assert a[3, 3, 3] > 0
