import math

from src.gauge_3d import U13DHamiltonian, _zeros3
from src.gauge_matter import (
    current_field,
    gauss_residual,
    link_current,
    max_abs,
    site_gauge_transform,
    sourced_weak_step,
    total_charge,
    uniform_matter,
)


def test_link_current_is_gauge_invariant():
    state = U13DHamiltonian.zeros((3,3,3))
    matter = uniform_matter((3,3,3), amplitude=1.0, polarity=1, phase=0.0)
    matter[1][0][0].phase = 0.7
    state.field.links["x"][0][0][0] = 0.2

    before = current_field(matter, state.field, 0.3)["x"][0][0][0]

    alpha = [
        [[0.05*(1+i+2*j+3*k) for k in range(3)] for j in range(3)]
        for i in range(3)
    ]
    matter2 = site_gauge_transform(matter, alpha)
    field2 = state.field.gauge_transform(alpha)
    after = current_field(matter2, field2, 0.3)["x"][0][0][0]

    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-12)


def test_reversing_link_orientation_reverses_current():
    from src.gauge_matter import MatterSite
    a = MatterSite(1.2, 1, 0.3)
    b = MatterSite(0.8, -1, -0.4)
    theta = 0.2
    jab = link_current(a, b, theta, 0.5)
    jba = link_current(b, a, -theta, 0.5)
    assert math.isclose(jab, -jba, rel_tol=0, abs_tol=1e-12)


def test_periodic_continuity_conserves_total_charge():
    state = U13DHamiltonian.zeros((3,3,3))
    matter = uniform_matter((3,3,3), amplitude=1.0, polarity=1, phase=0.0)
    matter[1][0][0].phase = 0.5
    currents = current_field(matter, state.field, 0.2)
    rho = _zeros3((3,3,3))
    initial = total_charge(rho)

    from src.gauge_matter import continuity_step
    rho2 = continuity_step(rho, currents, state.field.shape, 0.1)
    assert abs(total_charge(rho2) - initial) < 1e-12


def test_source_step_preserves_gauss_constraint_with_conserved_current():
    state = U13DHamiltonian.zeros((3,3,3), beta=1.0)

    # Choose one nonzero electric link and initialize rho=div E.
    state.electric["x"][0][0][0] = 0.25
    rho = state.gauss()

    matter = uniform_matter((3,3,3), amplitude=1.0, polarity=1, phase=0.0)
    matter[1][0][0].phase = 0.6
    matter[0][1][0].phase = -0.2
    currents = current_field(matter, state.field, 0.05)

    assert max_abs(gauss_residual(state, rho)) < 1e-14
    rho = sourced_weak_step(state, rho, currents, 0.01)
    assert max_abs(gauss_residual(state, rho)) < 1e-10
