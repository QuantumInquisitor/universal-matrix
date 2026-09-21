"""Synchronized source-and-gauge evolution for the Universal Matrix extensions.

This module integrates polarization-induced electric charge/current, conserved
free electric charge/current, six-gate boundary injection, compact-U(1)
topological magnetic diagnostics, and 3D Hamiltonian gauge evolution.

The current 3D gauge adapter is periodic. Therefore sum div(E)=0 identically,
so a periodic Gauss equation cannot represent nonzero total electric zero mode.
Boundary injection is tracked exactly, while the periodic gauge field responds
to the mean-subtracted source. The removed zero mode is reported separately as
zero_mode_charge. This is equivalent to a uniform compensating reservoir for
the periodic field problem, not an open-boundary solution.

The Gauss projector adds only the minimum-energy longitudinal correction needed
to satisfy the periodic source, preserving transverse electric components.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from .gauge_3d import AXES, U13DHamiltonian, _zeros3
    from .gauge_matter import sourced_weak_step
    from .polarity_sources import (
        induced_charge_density,
        polarization_current,
        polarization_field,
    )
    from .source_channels import (
        BoundaryFlux,
        FreeChargeSector,
        add_scalar_fields,
        apply_boundary_flux,
        magnetic_monopole_density,
        total_scalar,
    )
    from .source_interaction import solve_minimum_energy_field
except ImportError:
    from gauge_3d import AXES, U13DHamiltonian, _zeros3
    from gauge_matter import sourced_weak_step
    from polarity_sources import (
        induced_charge_density,
        polarization_current,
        polarization_field,
    )
    from source_channels import (
        BoundaryFlux,
        FreeChargeSector,
        add_scalar_fields,
        apply_boundary_flux,
        magnetic_monopole_density,
        total_scalar,
    )
    from source_interaction import solve_minimum_energy_field


def copy_scalar(field):
    return [[row[:] for row in plane] for plane in field]


def add_vector_fields(*fields):
    if not fields:
        raise ValueError("at least one vector field is required")
    shape = (
        len(fields[0]["x"]),
        len(fields[0]["x"][0]),
        len(fields[0]["x"][0][0]),
    )
    out = {axis: _zeros3(shape) for axis in AXES}
    for field in fields:
        for axis in AXES:
            if (
                len(field[axis]),
                len(field[axis][0]),
                len(field[axis][0][0]),
            ) != shape:
                raise ValueError("vector field shape mismatch")
            for i in range(shape[0]):
                for j in range(shape[1]):
                    for k in range(shape[2]):
                        out[axis][i][j][k] += field[axis][i][j][k]
    return out


def neutralize_periodic_source(rho):
    """Return mean-subtracted source and removed total zero-mode charge."""
    shape = (len(rho), len(rho[0]), len(rho[0][0]))
    count = shape[0] * shape[1] * shape[2]
    total = total_scalar(rho)
    mean = total / count
    out = _zeros3(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                out[i][j][k] = rho[i][j][k] - mean
    return out, total


def gauss_residual_field(state: U13DHamiltonian, target_rho):
    div_e = state.gauss()
    shape = state.field.shape
    out = _zeros3(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                out[i][j][k] = div_e[i][j][k] - target_rho[i][j][k]
    return out


def max_abs_scalar(field) -> float:
    return max(abs(v) for plane in field for row in plane for v in row)


def gauss_project(state: U13DHamiltonian, target_rho) -> float:
    """Add minimum-energy longitudinal correction so div(E)=target_rho."""
    total = total_scalar(target_rho)
    if abs(total) > 1e-10:
        raise ValueError("periodic Gauss target must have zero total charge")

    residual = gauss_residual_field(state, target_rho)
    correction_rho = -np.asarray(residual, dtype=float)
    correction = solve_minimum_energy_field(correction_rho)

    for axis in AXES:
        arr = correction.electric[axis]
        for i in range(state.field.shape[0]):
            for j in range(state.field.shape[1]):
                for k in range(state.field.shape[2]):
                    state.electric[axis][i][j][k] += float(arr[i, j, k])

    return max_abs_scalar(gauss_residual_field(state, target_rho))


@dataclass
class UnifiedStepDiagnostics:
    time: float
    total_electric_charge: float
    zero_mode_charge: float
    field_source_total: float
    boundary_inflow_rate: float
    charge_balance_residual: float
    max_gauss_residual: float
    total_topological_magnetic_charge: int
    nonzero_topological_cubes: int


class UnifiedMatrixGaugeEngine:
    """One synchronized state for all current experimental source channels."""

    def __init__(
        self,
        polarity_sites,
        free_charge=None,
        shape=None,
        beta: float = 1.0,
    ):
        inferred_shape = (
            len(polarity_sites),
            len(polarity_sites[0]),
            len(polarity_sites[0][0]),
        )
        self.shape = shape or inferred_shape
        if self.shape != inferred_shape:
            raise ValueError("polarity site shape mismatch")

        self.gauge = U13DHamiltonian.zeros(self.shape, beta=beta)
        self.polarization = polarization_field(polarity_sites)
        self.polarization_charge = induced_charge_density(
            self.polarization, self.shape
        )
        if free_charge is None:
            free_charge = _zeros3(self.shape)
        self.free = FreeChargeSector(copy_scalar(free_charge))
        self.total_electric_source = add_scalar_fields(
            self.polarization_charge, self.free.rho
        )
        self.field_source, self.zero_mode_charge = neutralize_periodic_source(
            self.total_electric_source
        )
        gauss_project(self.gauge, self.field_source)
        self.topological_magnetic_charge = magnetic_monopole_density(
            self.gauge.field
        )

    def step(
        self,
        new_polarity_sites,
        free_current,
        boundary_flux: BoundaryFlux,
        dt: float,
    ) -> UnifiedStepDiagnostics:
        if dt <= 0:
            raise ValueError("dt must be positive")

        old_total_charge = total_scalar(self.total_electric_source)

        new_polarization = polarization_field(new_polarity_sites)
        p_current = polarization_current(
            self.polarization,
            new_polarization,
            dt,
            self.shape,
        )
        new_polarization_charge = induced_charge_density(
            new_polarization, self.shape
        )

        self.free.evolve(free_current, dt)
        self.free.rho = apply_boundary_flux(
            self.free.rho,
            boundary_flux,
            dt,
        )

        total_current = add_vector_fields(p_current, free_current)

        sourced_weak_step(
            self.gauge,
            self.field_source,
            total_current,
            dt,
        )

        self.polarization = new_polarization
        self.polarization_charge = new_polarization_charge
        self.total_electric_source = add_scalar_fields(
            self.polarization_charge,
            self.free.rho,
        )
        self.field_source, self.zero_mode_charge = neutralize_periodic_source(
            self.total_electric_source
        )

        max_gauss = gauss_project(self.gauge, self.field_source)

        self.topological_magnetic_charge = magnetic_monopole_density(
            self.gauge.field
        )
        topo_total = sum(
            int(v)
            for plane in self.topological_magnetic_charge
            for row in plane
            for v in row
        )
        topo_nonzero = sum(
            1
            for plane in self.topological_magnetic_charge
            for row in plane
            for v in row
            if v != 0
        )

        new_total_charge = total_scalar(self.total_electric_source)
        expected_delta = dt * boundary_flux.net_inflow_rate()
        balance_residual = (
            new_total_charge - old_total_charge - expected_delta
        )

        return UnifiedStepDiagnostics(
            time=self.gauge.time,
            total_electric_charge=new_total_charge,
            zero_mode_charge=self.zero_mode_charge,
            field_source_total=total_scalar(self.field_source),
            boundary_inflow_rate=boundary_flux.net_inflow_rate(),
            charge_balance_residual=balance_residual,
            max_gauss_residual=max_gauss,
            total_topological_magnetic_charge=topo_total,
            nonzero_topological_cubes=topo_nonzero,
        )
