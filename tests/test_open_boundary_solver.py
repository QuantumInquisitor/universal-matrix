import numpy as np
import pytest

from src.open_boundary_solver import (
    GateFieldFlux,
    balanced_gate_flux,
    compatibility_residual,
    solve_open_gauss,
)


def test_nonzero_total_charge_supported_with_matching_boundary_flux():
    rho = np.zeros((8, 8, 8))
    rho[4, 4, 4] = 2.0
    flux = GateFieldFlux(x_pos=2.0)

    solution = solve_open_gauss(rho, flux)

    assert abs(solution.compatibility_residual) < 1e-12
    assert solution.max_abs_gauss_residual(rho) < 1e-9
    assert abs(np.mean(solution.potential)) < 1e-12


def test_incompatible_neumann_data_is_rejected():
    rho = np.zeros((4, 4, 4))
    rho[1, 1, 1] = 1.0
    with pytest.raises(ValueError):
        solve_open_gauss(rho, GateFieldFlux())


def test_equal_gate_balancing_matches_total_charge():
    flux = balanced_gate_flux(3.0)
    assert abs(flux.total_outward_flux() - 3.0) < 1e-12
    vals = list(flux.as_dict().values())
    assert max(vals) - min(vals) < 1e-12


def test_weighted_gate_balancing_can_select_specific_gate():
    weights = {
        "x_pos": 1.0,
        "x_neg": 0.0,
        "y_pos": 0.0,
        "y_neg": 0.0,
        "z_pos": 0.0,
        "z_neg": 0.0,
    }
    flux = balanced_gate_flux(1.25, weights)
    assert flux.x_pos == 1.25
    assert flux.total_outward_flux() == 1.25


def test_zero_charge_zero_flux_returns_zero_field():
    rho = np.zeros((5, 5, 5))
    solution = solve_open_gauss(rho, GateFieldFlux())
    assert solution.field_energy() == 0.0
    assert solution.max_abs_gauss_residual(rho) == 0.0


def test_compatibility_residual_matches_charge_minus_flux():
    rho = np.zeros((3, 3, 3))
    rho[0, 0, 0] = 1.7
    flux = GateFieldFlux(z_neg=0.4)
    assert abs(compatibility_residual(rho, flux) - 1.3) < 1e-12
