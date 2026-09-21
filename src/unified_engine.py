"""Synchronized Universal Matrix gauge/source engine.

Default mode is a true open cubical domain tied to the six canonical gates.
The open mode uses:
  * open finite-volume polarity sources,
  * open interior free-current continuity,
  * six-face charge injection,
  * discrete-exterior-calculus U(1) Hamiltonian dynamics,
  * open Neumann Gauss projection,
  * compact topological magnetic diagnostics on the same open complex.

A legacy periodic mode is retained for regression comparison only.
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
    from .open_polarity_sources import (
        induced_charge_density_open,
        polarization_current_open,
    )
    from .open_gauge_dynamics import (
        OpenU1Hamiltonian,
        divergence as open_divergence,
        restrict_full_current_to_open,
        topological_magnetic_charge as open_topological_magnetic_charge,
        zero_links,
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
    from .open_boundary_solver import (
        GateFieldFlux,
        balanced_gate_flux,
        boundary_flux_density,
        boundary_source_array,
        solve_open_gauss,
    )
except ImportError:
    from gauge_3d import AXES, U13DHamiltonian, _zeros3
    from gauge_matter import sourced_weak_step
    from polarity_sources import (
        induced_charge_density,
        polarization_current,
        polarization_field,
    )
    from open_polarity_sources import (
        induced_charge_density_open,
        polarization_current_open,
    )
    from open_gauge_dynamics import (
        OpenU1Hamiltonian,
        divergence as open_divergence,
        restrict_full_current_to_open,
        topological_magnetic_charge as open_topological_magnetic_charge,
        zero_links,
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
    from open_boundary_solver import (
        GateFieldFlux,
        balanced_gate_flux,
        boundary_flux_density,
        boundary_source_array,
        solve_open_gauss,
    )


def copy_scalar(field):
    return [[row[:] for row in plane] for plane in field]


def _np_scalar(field):
    return np.asarray(field, dtype=float)


def _np_vector(field):
    return {axis: np.asarray(field[axis], dtype=float) for axis in AXES}


def add_vector_fields(*fields):
    if not fields:
        raise ValueError("at least one vector field is required")
    out = {}
    for axis in AXES:
        arrays = [np.asarray(field[axis], dtype=float) for field in fields]
        shape = arrays[0].shape
        if any(a.shape != shape for a in arrays):
            raise ValueError("vector field shape mismatch")
        out[axis] = sum(arrays[1:], arrays[0].copy())
    return out


def cell_vector_to_open_links(cell_vector):
    """Average cell-centered vector values onto open interior links."""
    v = _np_vector(cell_vector)
    return {
        "x": 0.5 * (v["x"][:-1, :, :] + v["x"][1:, :, :]),
        "y": 0.5 * (v["y"][:, :-1, :] + v["y"][:, 1:, :]),
        "z": 0.5 * (v["z"][:, :, :-1] + v["z"][:, :, 1:]),
    }


def neutralize_periodic_source(rho):
    arr = _np_scalar(rho)
    total = float(np.sum(arr))
    return arr - np.mean(arr), total


def gauss_residual_periodic(state: U13DHamiltonian, target_rho):
    return _np_scalar(state.gauss()) - _np_scalar(target_rho)


def gauss_project_periodic(state: U13DHamiltonian, target_rho) -> float:
    target = _np_scalar(target_rho)
    if abs(float(np.sum(target))) > 1e-10:
        raise ValueError("periodic Gauss target must have zero total charge")
    residual = gauss_residual_periodic(state, target)
    correction = solve_minimum_energy_field(-residual)
    for axis in AXES:
        state.electric[axis] = (
            np.asarray(state.electric[axis], dtype=float)
            + correction.electric[axis]
        )
    return float(np.max(np.abs(gauss_residual_periodic(state, target))))


def open_gauss_residual(state, target_rho, gate_flux):
    face = boundary_flux_density(state.shape, gate_flux)
    return (
        open_divergence(state.electric, state.shape)
        + boundary_source_array(state.shape, face)
        - _np_scalar(target_rho)
    )


def gauss_project_open(state, target_rho, gate_flux) -> float:
    """Helmholtz-style longitudinal correction on an open cubical complex."""
    residual = open_gauss_residual(state, target_rho, gate_flux)
    correction_rho = -residual

    if abs(float(np.sum(correction_rho))) > 1e-9:
        raise ValueError("open Gauss correction is globally incompatible")

    correction = solve_open_gauss(
        correction_rho,
        GateFieldFlux(),
    )
    for axis in AXES:
        state.electric[axis] += correction.electric_links[axis]

    return float(
        np.max(np.abs(open_gauss_residual(state, target_rho, gate_flux)))
    )


def _gate_weights(boundary_flux: BoundaryFlux):
    rates = boundary_flux.as_dict()
    magnitudes = {name: abs(value) for name, value in rates.items()}
    return magnitudes if sum(magnitudes.values()) > 0 else None


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
        boundary_mode: str = "open",
    ):
        inferred_shape = (
            len(polarity_sites),
            len(polarity_sites[0]),
            len(polarity_sites[0][0]),
        )
        self.shape = shape or inferred_shape
        if self.shape != inferred_shape:
            raise ValueError("polarity site shape mismatch")
        if boundary_mode not in ("open", "periodic"):
            raise ValueError("boundary_mode must be 'open' or 'periodic'")
        self.boundary_mode = boundary_mode

        self.polarization = _np_vector(polarization_field(polarity_sites))
        if free_charge is None:
            free_charge = np.zeros(self.shape, dtype=float)

        if boundary_mode == "open":
            self.gauge = OpenU1Hamiltonian.zeros(self.shape, beta=beta)
            self.free_rho = _np_scalar(free_charge).copy()
            self.free = None
            self.polarization_charge = induced_charge_density_open(
                self.polarization
            )
            self.total_electric_source = (
                self.polarization_charge + self.free_rho
            )
            self.field_source = self.total_electric_source.copy()
            self.zero_mode_charge = 0.0

            total_q = float(np.sum(self.field_source))
            self.open_boundary_flux = balanced_gate_flux(total_q)
            self.open_boundary_solution = None
            self.max_gauss_residual = gauss_project_open(
                self.gauge,
                self.field_source,
                self.open_boundary_flux,
            )
            self.topological_magnetic_charge = open_topological_magnetic_charge(
                self.gauge.links,
                self.shape,
            )
        else:
            self.gauge = U13DHamiltonian.zeros(self.shape, beta=beta)
            self.free = FreeChargeSector(copy_scalar(free_charge))
            self.free_rho = None
            self.polarization_charge = _np_scalar(
                induced_charge_density(self.polarization, self.shape)
            )
            self.total_electric_source = (
                self.polarization_charge + _np_scalar(self.free.rho)
            )
            self.field_source, self.zero_mode_charge = (
                neutralize_periodic_source(self.total_electric_source)
            )
            self.max_gauss_residual = gauss_project_periodic(
                self.gauge,
                self.field_source,
            )
            self.open_boundary_flux = None
            self.open_boundary_solution = None
            self.topological_magnetic_charge = np.asarray(
                magnetic_monopole_density(self.gauge.field),
                dtype=int,
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

        old_total_charge = float(np.sum(self.total_electric_source))
        new_polarization = _np_vector(
            polarization_field(new_polarity_sites)
        )

        if self.boundary_mode == "open":
            p_current_cell = polarization_current_open(
                self.polarization,
                new_polarization,
                dt,
            )
            p_current_open = cell_vector_to_open_links(p_current_cell)
            free_current_open = restrict_full_current_to_open(
                free_current,
                self.shape,
            )
            total_current_open = add_vector_fields(
                p_current_open,
                free_current_open,
            )

            # Internal free-current continuity on the same open edges used by
            # the gauge dynamics.
            self.free_rho = (
                self.free_rho
                - dt * open_divergence(
                    free_current_open,
                    self.shape,
                )
            )

            # Explicit six-gate charge exchange.
            self.free_rho = _np_scalar(
                apply_boundary_flux(
                    self.free_rho.tolist(),
                    boundary_flux,
                    dt,
                )
            )

            # Evolve transverse + source-coupled open gauge degrees of freedom.
            self.gauge.leapfrog(dt, current=total_current_open)

            self.polarization = new_polarization
            self.polarization_charge = induced_charge_density_open(
                self.polarization
            )
            self.total_electric_source = (
                self.polarization_charge + self.free_rho
            )
            self.field_source = self.total_electric_source.copy()
            self.zero_mode_charge = 0.0

            total_q = float(np.sum(self.field_source))
            self.open_boundary_flux = balanced_gate_flux(
                total_q,
                weights=_gate_weights(boundary_flux),
            )
            max_gauss = gauss_project_open(
                self.gauge,
                self.field_source,
                self.open_boundary_flux,
            )
            self.max_gauss_residual = max_gauss

            self.topological_magnetic_charge = open_topological_magnetic_charge(
                self.gauge.links,
                self.shape,
            )
        else:
            p_current = polarization_current(
                self.polarization,
                new_polarization,
                dt,
                self.shape,
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
                self.field_source.tolist(),
                {
                    a: np.asarray(total_current[a]).tolist()
                    for a in AXES
                },
                dt,
            )

            self.polarization = new_polarization
            self.polarization_charge = _np_scalar(
                induced_charge_density(self.polarization, self.shape)
            )
            self.total_electric_source = (
                self.polarization_charge + _np_scalar(self.free.rho)
            )
            self.field_source, self.zero_mode_charge = (
                neutralize_periodic_source(self.total_electric_source)
            )
            max_gauss = gauss_project_periodic(
                self.gauge,
                self.field_source,
            )
            self.max_gauss_residual = max_gauss
            self.topological_magnetic_charge = np.asarray(
                magnetic_monopole_density(self.gauge.field),
                dtype=int,
            )

        topo_total = int(np.sum(self.topological_magnetic_charge))
        topo_nonzero = int(np.count_nonzero(self.topological_magnetic_charge))

        new_total_charge = float(np.sum(self.total_electric_source))
        expected_delta = dt * boundary_flux.net_inflow_rate()
        balance_residual = (
            new_total_charge - old_total_charge - expected_delta
        )

        return UnifiedStepDiagnostics(
            time=float(self.gauge.time),
            total_electric_charge=new_total_charge,
            zero_mode_charge=float(self.zero_mode_charge),
            field_source_total=float(np.sum(self.field_source)),
            boundary_inflow_rate=boundary_flux.net_inflow_rate(),
            charge_balance_residual=float(balance_residual),
            max_gauss_residual=float(max_gauss),
            total_topological_magnetic_charge=topo_total,
            nonzero_topological_cubes=topo_nonzero,
        )
