from src.gauge_3d import AXES, _zeros3
from src.polarity_sources import PolaritySourceSite
from src.source_channels import BoundaryFlux
from src.unified_engine import UnifiedMatrixGaugeEngine


def sites(shape, amplitude=0.0, polarity=1, axis="x"):
    nx, ny, nz = shape
    return [
        [
            [PolaritySourceSite(amplitude, polarity, axis) for _ in range(nz)]
            for _ in range(ny)
        ]
        for _ in range(nx)
    ]


def zero_current(shape):
    return {axis: _zeros3(shape) for axis in AXES}


def test_closed_unified_step_preserves_total_charge_and_gauss():
    shape = (4,4,4)
    old = sites(shape)
    old[1][1][1] = PolaritySourceSite(0.5, 1, "x")
    engine = UnifiedMatrixGaugeEngine(old, shape=shape)

    new = sites(shape)
    new[1][1][1] = PolaritySourceSite(0.8, -1, "x")

    d = engine.step(new, zero_current(shape), BoundaryFlux(), 0.01)

    assert abs(d.total_electric_charge) < 1e-12
    assert abs(d.zero_mode_charge) < 1e-12
    assert abs(d.field_source_total) < 1e-12
    assert abs(d.charge_balance_residual) < 1e-12
    assert d.max_gauss_residual < 1e-10


def test_free_current_is_internally_conservative():
    shape = (4,4,4)
    engine = UnifiedMatrixGaugeEngine(sites(shape), shape=shape)

    j = zero_current(shape)
    j["x"][1][1][1] = 0.25

    d = engine.step(sites(shape), j, BoundaryFlux(), 0.02)

    assert abs(d.total_electric_charge) < 1e-12
    assert abs(d.charge_balance_residual) < 1e-12
    assert d.max_gauss_residual < 1e-10


def test_boundary_inflow_changes_total_charge_and_zero_mode_exactly():
    shape = (4,4,4)
    engine = UnifiedMatrixGaugeEngine(sites(shape), shape=shape)
    flux = BoundaryFlux(x_pos=1.5, y_neg=-0.25, z_pos=0.5)
    dt = 0.1

    d = engine.step(sites(shape), zero_current(shape), flux, dt)

    expected = dt * flux.net_inflow_rate()
    assert abs(d.total_electric_charge - expected) < 1e-12
    assert abs(d.zero_mode_charge) < 1e-12
    assert abs(d.field_source_total - expected) < 1e-12
    assert abs(d.charge_balance_residual) < 1e-12
    assert d.max_gauss_residual < 1e-9


def test_periodic_topological_total_is_reported_separately():
    shape = (3,3,3)
    engine = UnifiedMatrixGaugeEngine(sites(shape), shape=shape)

    import math
    engine.gauge.field.links["x"][0][0][0] = 2.0 * math.pi + 0.2

    d = engine.step(sites(shape), zero_current(shape), BoundaryFlux(), 0.01)

    assert isinstance(d.total_topological_magnetic_charge, int)
    assert isinstance(d.nonzero_topological_cubes, int)


def test_initial_nonzero_free_charge_is_supported_by_open_boundaries():
    shape = (4,4,4)
    rho = _zeros3(shape)
    rho[0][0][0] = 2.0
    engine = UnifiedMatrixGaugeEngine(
        sites(shape),
        free_charge=rho,
        shape=shape,
        boundary_mode="open",
    )

    assert abs(engine.zero_mode_charge) < 1e-12
    assert abs(sum(v for p in engine.field_source for r in p for v in r) - 2.0) < 1e-12
    assert engine.open_boundary_solution is not None
    assert engine.open_boundary_solution.max_abs_gauss_residual(
        __import__("numpy").asarray(engine.field_source, dtype=float)
    ) < 1e-9


def test_periodic_mode_retains_legacy_zero_mode_split():
    shape = (4,4,4)
    rho = _zeros3(shape)
    rho[0][0][0] = 2.0
    engine = UnifiedMatrixGaugeEngine(
        sites(shape),
        free_charge=rho,
        shape=shape,
        boundary_mode="periodic",
    )

    assert abs(engine.zero_mode_charge - 2.0) < 1e-12
    assert abs(sum(v for p in engine.field_source for r in p for v in r)) < 1e-12
