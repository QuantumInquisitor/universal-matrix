import numpy as np
import pytest

from src.open_boundary_solver import (
    GateFieldFlux,
    balanced_gate_flux,
    compatibility_residual,
    patterned_compatibility_residual,
    solve_open_gauss,
    solve_open_gauss_with_face_flux,
    total_boundary_flux,
    validate_face_flux_density,
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


def zero_face_flux(shape):
    nx, ny, nz = shape
    return {
        "x_pos": np.zeros((ny, nz)),
        "x_neg": np.zeros((ny, nz)),
        "y_pos": np.zeros((nx, nz)),
        "y_neg": np.zeros((nx, nz)),
        "z_pos": np.zeros((nx, ny)),
        "z_neg": np.zeros((nx, ny)),
    }


def test_patterned_neumann_patches_preserve_exact_flux_and_gauss_balance():
    shape = (10, 10, 10)
    rho = np.zeros(shape)
    face_flux = zero_face_flux(shape)

    face_flux["z_neg"][1:3, 1:3] = -0.25
    face_flux["z_pos"][7:9, 7:9] = 0.25

    assert total_boundary_flux(face_flux) == pytest.approx(0.0, abs=1e-15)
    assert patterned_compatibility_residual(rho, face_flux) == pytest.approx(
        0.0,
        abs=1e-15,
    )

    solution = solve_open_gauss_with_face_flux(rho, face_flux)

    assert solution.compatibility_residual == pytest.approx(0.0, abs=1e-15)
    assert solution.max_abs_gauss_residual(rho) < 1e-9
    assert np.array_equal(
        solution.boundary_flux_density["z_neg"],
        face_flux["z_neg"],
    )
    assert np.array_equal(
        solution.boundary_flux_density["z_pos"],
        face_flux["z_pos"],
    )
    assert abs(np.mean(solution.potential)) < 1e-12
    assert solution.field_energy() > 0.0


def test_multiple_disjoint_patches_on_one_face_are_supported():
    shape = (12, 12, 8)
    rho = np.zeros(shape)
    face_flux = zero_face_flux(shape)

    face_flux["z_neg"][1:3, 1:3] = -0.125
    face_flux["z_neg"][8:10, 8:10] = -0.125
    face_flux["z_pos"][4:8, 4:8] = 0.0625

    assert np.sum(face_flux["z_neg"]) == pytest.approx(-1.0)
    assert np.sum(face_flux["z_pos"]) == pytest.approx(1.0)

    solution = solve_open_gauss_with_face_flux(rho, face_flux)
    assert solution.max_abs_gauss_residual(rho) < 1e-9
    assert total_boundary_flux(solution.boundary_flux_density) == pytest.approx(
        0.0,
        abs=1e-15,
    )


def test_uniform_gate_solver_matches_explicit_uniform_face_flux_solver():
    rho = np.zeros((7, 6, 5))
    flux = GateFieldFlux(x_pos=1.2, x_neg=-1.2)
    explicit = validate_face_flux_density(
        rho.shape,
        {
            "x_pos": np.full((6, 5), 1.2 / 30.0),
            "x_neg": np.full((6, 5), -1.2 / 30.0),
            "y_pos": np.zeros((7, 5)),
            "y_neg": np.zeros((7, 5)),
            "z_pos": np.zeros((7, 6)),
            "z_neg": np.zeros((7, 6)),
        },
    )

    legacy = solve_open_gauss(rho, flux)
    patterned = solve_open_gauss_with_face_flux(rho, explicit)

    assert np.allclose(legacy.potential, patterned.potential, atol=1e-13)
    for axis in ("x", "y", "z"):
        assert np.allclose(
            legacy.electric_links[axis],
            patterned.electric_links[axis],
            atol=1e-13,
        )


def test_patterned_face_flux_rejects_missing_extra_wrong_shape_and_nonfinite():
    shape = (5, 6, 7)
    valid = zero_face_flux(shape)

    missing = dict(valid)
    missing.pop("x_pos")
    with pytest.raises(ValueError, match="missing boundary faces"):
        validate_face_flux_density(shape, missing)

    extra = dict(valid)
    extra["bad_face"] = np.zeros((1, 1))
    with pytest.raises(ValueError, match="unknown boundary faces"):
        validate_face_flux_density(shape, extra)

    wrong_shape = dict(valid)
    wrong_shape["z_pos"] = np.zeros((5, 5))
    with pytest.raises(ValueError, match="z_pos flux array must have shape"):
        validate_face_flux_density(shape, wrong_shape)

    nonfinite = {name: np.array(values, copy=True) for name, values in valid.items()}
    nonfinite["y_neg"][0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        validate_face_flux_density(shape, nonfinite)


def test_patterned_solver_rejects_incompatible_total_flux():
    shape = (6, 6, 6)
    rho = np.zeros(shape)
    face_flux = zero_face_flux(shape)
    face_flux["z_pos"][2:4, 2:4] = 0.25

    with pytest.raises(ValueError, match="incompatible Neumann data"):
        solve_open_gauss_with_face_flux(rho, face_flux)
