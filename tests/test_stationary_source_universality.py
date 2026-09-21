import math
import numpy as np

from src.stationary_source_universality import (
    StationarySourceDiagnostic,
    integrated_active_source,
    isotropic_integrated_stress,
    source_energy_difference,
    source_energy_ratio,
)


def test_zero_integrated_stress_gives_exact_source_energy_universality():
    stress = np.zeros((3,3))
    energy = 7.5
    assert integrated_active_source(energy, stress) == energy
    assert source_energy_difference(stress) == 0.0
    assert source_energy_ratio(energy, stress) == 1.0


def test_nonzero_integrated_pressure_shifts_active_source():
    energy = 10.0
    stress = isotropic_integrated_stress(0.5)
    source = integrated_active_source(energy, stress)
    assert source == 11.5
    assert source_energy_difference(stress) == 1.5


def test_anisotropic_stresses_can_cancel_in_trace_but_fail_laue_condition():
    stress = np.diag([1.0, -1.0, 0.0])
    diagnostic = StationarySourceDiagnostic(
        energy=5.0,
        integrated_spatial_stress=stress,
    )

    assert diagnostic.active_source == 5.0
    assert diagnostic.ratio == 1.0
    assert diagnostic.laue_residual == 1.0
    assert not diagnostic.universal_on_stationary_shell


def test_laue_shell_is_composition_independent():
    energies = [1.0, 2.5, 100.0]
    for energy in energies:
        diagnostic = StationarySourceDiagnostic(
            energy=energy,
            integrated_spatial_stress=np.zeros((3,3)),
        )
        assert diagnostic.universal_on_stationary_shell
        assert math.isclose(
            diagnostic.ratio,
            1.0,
            rel_tol=0,
            abs_tol=0,
        )


def test_source_mismatch_is_trace_of_integrated_stress():
    stress = np.array(
        [
            [0.2, 0.1, 0.0],
            [0.1, -0.05, 0.0],
            [0.0, 0.0, 0.3],
        ]
    )
    expected = float(np.trace(stress))
    assert math.isclose(
        source_energy_difference(stress),
        expected,
        rel_tol=0,
        abs_tol=1e-15,
    )
