import numpy as np

from src.open_polarity_sources import (
    continuity_residual_open,
    finite_volume_divergence,
    induced_charge_density_open,
    polarization_current_open,
)


def test_open_polarization_continuity_identity():
    shape=(4,5,3)
    old={a:np.zeros(shape) for a in ("x","y","z")}
    new={a:np.zeros(shape) for a in ("x","y","z")}
    old["x"][1,2,1]=0.4
    new["x"][1,2,1]=-0.9
    new["z"][2,1,1]=0.3
    dt=0.07
    r0=induced_charge_density_open(old)
    r1=induced_charge_density_open(new)
    j=polarization_current_open(old,new,dt)
    residual=continuity_residual_open(r0,r1,j,dt)
    assert np.max(np.abs(residual)) < 1e-12


def test_uniform_polarization_has_zero_bulk_divergence():
    shape=(4,4,4)
    p={a:np.zeros(shape) for a in ("x","y","z")}
    p["x"][...]=1.0
    div=finite_volume_divergence(p)
    assert np.max(np.abs(div)) < 1e-12
