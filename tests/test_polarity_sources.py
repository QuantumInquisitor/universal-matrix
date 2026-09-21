from src.polarity_sources import (
    PolaritySourceSite,
    continuity_residual,
    induced_charge_density,
    max_abs,
    polarization_current,
    polarization_field,
    total_charge,
)


def blank_sites(shape, amplitude=0.0, polarity=1, axis="x"):
    nx, ny, nz = shape
    return [
        [
            [PolaritySourceSite(amplitude, polarity, axis) for _ in range(nz)]
            for _ in range(ny)
        ]
        for _ in range(nx)
    ]


def test_uniform_polarization_has_zero_induced_charge():
    shape = (4,4,4)
    sites = blank_sites(shape, amplitude=1.0, polarity=1, axis="x")
    p = polarization_field(sites)
    rho = induced_charge_density(p, shape)
    assert max_abs(rho) == 0.0


def test_localized_polarization_creates_opposite_source_faces():
    shape = (5,5,5)
    sites = blank_sites(shape)
    sites[2][2][2] = PolaritySourceSite(1.0, 1, "x")
    p = polarization_field(sites)
    rho = induced_charge_density(p, shape)

    nonzero = []
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                if rho[i][j][k] != 0.0:
                    nonzero.append(((i,j,k), rho[i][j][k]))

    assert len(nonzero) == 2
    assert sorted(v for _, v in nonzero) == [-1.0, 1.0]
    assert abs(total_charge(rho)) < 1e-12


def test_polarity_flip_reverses_induced_source_signs():
    shape = (5,5,5)
    plus = blank_sites(shape)
    minus = blank_sites(shape)
    plus[2][2][2] = PolaritySourceSite(1.0, 1, "z")
    minus[2][2][2] = PolaritySourceSite(1.0, -1, "z")

    rho_plus = induced_charge_density(polarization_field(plus), shape)
    rho_minus = induced_charge_density(polarization_field(minus), shape)

    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                assert rho_minus[i][j][k] == -rho_plus[i][j][k]


def test_polarization_current_satisfies_continuity_identity():
    shape = (4,4,4)
    old_sites = blank_sites(shape)
    new_sites = blank_sites(shape)
    old_sites[1][1][1] = PolaritySourceSite(0.4, 1, "y")
    new_sites[1][1][1] = PolaritySourceSite(0.9, -1, "y")

    p0 = polarization_field(old_sites)
    p1 = polarization_field(new_sites)
    rho0 = induced_charge_density(p0, shape)
    rho1 = induced_charge_density(p1, shape)
    dt = 0.05
    current = polarization_current(p0, p1, dt, shape)
    residual = continuity_residual(rho0, rho1, current, dt, shape)

    assert max_abs(residual) < 1e-12


def test_total_periodic_induced_charge_is_always_zero():
    shape = (4,4,4)
    sites = blank_sites(shape)
    sites[0][0][0] = PolaritySourceSite(1.2, 1, "x")
    sites[1][2][3] = PolaritySourceSite(0.8, -1, "y")
    sites[3][1][2] = PolaritySourceSite(0.5, 1, "z")
    rho = induced_charge_density(polarization_field(sites), shape)
    assert abs(total_charge(rho)) < 1e-12
