import math
import numpy as np

from src.localized_matter_variational import MatterPotential
from src.reciprocity_unified_geometry_source import (
    SectorContribution,
    active_source_from_energy_and_integrated_stress,
    binding_completion,
    make_ledger,
    required_binding_stress_trace_for_universality,
    scalar_sector_from_canonical_fields,
    stationary_universal_source,
    u1_sector,
    yang_mills_sector,
)


def test_free_rest_scalar_has_unit_source_energy_ratio():
    shape = (2,2,2)
    amplitude = 0.3
    mass = 1.2
    phi = np.full(shape, amplitude + 0j, dtype=complex)
    psi = np.zeros(shape)
    momentum = 1j * mass * phi

    sector = scalar_sector_from_canonical_fields(
        phi,
        momentum,
        psi,
        MatterPotential(
            mass2=mass**2,
            lambda4=0.0,
            lambda6=0.0,
        ),
        spatial_gradient_squared=0.0,
    )

    assert math.isclose(
        sector.active_source,
        sector.energy,
        rel_tol=0,
        abs_tol=1e-12,
    )


def test_free_u1_and_yang_mills_sources_are_twice_local_energy():
    u1 = u1_sector(
        displacement=np.array([1.0, 2.0, 0.5]),
        magnetic=np.array([0.2, 0.3, 0.4]),
        psi=0.1,
    )
    ym = yang_mills_sector(
        displacement_components=np.ones((3,3)),
        magnetic_components=np.full((3,3), 0.5),
        psi=-0.2,
    )

    assert math.isclose(
        u1.active_source,
        2.0*u1.energy,
        rel_tol=0,
        abs_tol=1e-15,
    )
    assert math.isclose(
        ym.active_source,
        2.0*ym.energy,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_unified_ledger_adds_sector_sources_and_energies():
    ledger = make_ledger(
        SectorContribution("matter", 3.0, 3.0),
        SectorContribution("u1", 2.0, 4.0),
        SectorContribution("ym", 5.0, 10.0),
    )
    assert ledger.total_energy == 10.0
    assert ledger.total_active_source == 17.0
    assert ledger.source_energy_difference == 7.0


def test_von_laue_condition_restores_total_universality():
    stress = np.zeros((3,3))
    energy = 12.5
    source = active_source_from_energy_and_integrated_stress(
        energy, stress
    )
    universal = stationary_universal_source(energy, stress)
    assert source == energy
    assert universal == energy


def test_binding_stress_can_complete_nonuniversal_constituent_bookkeeping():
    constituent_energy = 10.0
    constituent_source = 14.0
    binding_energy = -2.0

    required_trace = required_binding_stress_trace_for_universality(
        constituent_energy,
        constituent_source,
        binding_energy,
    )
    binding = binding_completion(
        constituent_energy,
        constituent_source,
        binding_energy,
        required_trace,
    )
    ledger = make_ledger(
        SectorContribution(
            "constituents",
            constituent_energy,
            constituent_source,
        ),
        binding,
    )

    assert math.isclose(
        ledger.total_active_source,
        ledger.total_energy,
        rel_tol=0,
        abs_tol=1e-15,
    )


def test_stationary_universal_source_rejects_nonzero_total_stress():
    stress = np.diag([1e-3, 0.0, 0.0])
    try:
        stationary_universal_source(1.0, stress, tolerance=1e-6)
    except ValueError:
        pass
    else:
        raise AssertionError("nonzero Laue residual must be rejected")
