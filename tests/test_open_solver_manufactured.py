import numpy as np

from src.open_boundary_solver import (
    GateFieldFlux,
    boundary_flux_density,
    boundary_source_array,
    neumann_laplacian,
    solve_open_gauss,
)


def _mean_zero(a):
    return a - np.mean(a)


def test_manufactured_zero_flux_solution_recovers_potential():
    rng = np.random.default_rng(20260921)
    phi = _mean_zero(rng.normal(size=(7, 6, 5)))
    rho = neumann_laplacian(phi)

    solution = solve_open_gauss(
        rho,
        GateFieldFlux(),
        tolerance=1e-12,
    )

    assert np.max(np.abs(solution.potential - phi)) < 1e-9
    assert solution.max_abs_gauss_residual(rho) < 1e-9


def test_manufactured_six_gate_solution_recovers_potential():
    rng = np.random.default_rng(10864)
    shape = (6, 5, 4)
    phi = _mean_zero(rng.normal(size=shape))
    flux = GateFieldFlux(
        x_pos=0.7,
        x_neg=-0.2,
        y_pos=0.4,
        y_neg=0.1,
        z_pos=-0.3,
        z_neg=0.5,
    )
    faces = boundary_flux_density(shape, flux)
    boundary = boundary_source_array(shape, faces)

    # By construction L phi = rho - boundary, so rho = L phi + boundary.
    rho = neumann_laplacian(phi) + boundary

    solution = solve_open_gauss(
        rho,
        flux,
        tolerance=1e-12,
    )

    assert abs(np.sum(rho) - flux.total_outward_flux()) < 1e-12
    assert np.max(np.abs(solution.potential - phi)) < 1e-9
    assert solution.max_abs_gauss_residual(rho) < 1e-9
