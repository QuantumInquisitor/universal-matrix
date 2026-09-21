import math

from src.gauge_3d import U13DField, _zeros3
from src.source_channels import (
    BoundaryFlux,
    FreeChargeSector,
    UnifiedElectricSource,
    add_scalar_fields,
    apply_boundary_flux,
    electric_charge_balance,
    magnetic_monopole_density,
    plaquette_winding_integer,
    total_scalar,
)


def test_free_charge_sector_conserves_total_charge_without_boundary_flux():
    shape = (4,4,4)
    rho = _zeros3(shape)
    rho[1][1][1] = 1.0
    sector = FreeChargeSector(rho)

    currents = {axis: _zeros3(shape) for axis in ("x","y","z")}
    currents["x"][1][1][1] = 0.3
    before = total_scalar(sector.rho)
    sector.evolve(currents, 0.2)
    after = total_scalar(sector.rho)

    assert abs(after-before) < 1e-12


def test_boundary_flux_changes_total_charge_exactly():
    shape = (4,4,4)
    rho = _zeros3(shape)
    flux = BoundaryFlux(x_pos=2.0, y_neg=-0.5, z_pos=0.25)
    dt = 0.1

    before = total_scalar(rho)
    rho2 = apply_boundary_flux(rho, flux, dt)
    after = total_scalar(rho2)

    assert abs(electric_charge_balance(before, after, flux, dt)) < 1e-12


def test_unified_electric_source_sums_polarization_and_free_channels():
    shape = (3,3,3)
    p = _zeros3(shape)
    f = _zeros3(shape)
    p[0][0][0] = 0.4
    p[1][0][0] = -0.4
    f[2][2][2] = 1.5
    unified = UnifiedElectricSource(p, f)
    total = unified.total()
    assert math.isclose(total_scalar(total), 1.5, rel_tol=0, abs_tol=1e-12)


def test_compact_plaquette_detects_integer_winding():
    field = U13DField.zeros((3,3,3))
    # Make raw F_xy at origin exactly 2*pi + 0.2.
    field.links["x"][0][0][0] = 2.0 * math.pi + 0.2
    n = plaquette_winding_integer(field, ("x","y"), (0,0,0))
    assert n == 1


def test_topological_magnetic_charge_is_integer_valued():
    field = U13DField.zeros((3,3,3))
    field.links["x"][0][0][0] = 2.0 * math.pi + 0.2
    density = magnetic_monopole_density(field)
    for plane in density:
        for row in plane:
            for value in row:
                assert isinstance(value, int)
