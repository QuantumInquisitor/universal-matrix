import math

import numpy as np
import pytest

from src.toroidal_assembly_breathing import (
    AssemblyBreathing,
    BreathingAssembly,
    audit_assembly_breathing,
)


@pytest.mark.parametrize(
    "amplitude", [-0.1, 0.10001, 1, True, complex(0.1), float("nan"), float("inf")]
)
def test_rejects_unreviewed_or_singular_cycles(amplitude):
    with pytest.raises(ValueError):
        AssemblyBreathing(amplitude)


@pytest.mark.parametrize("phase", [-0.01, 1.01, True, complex(0), float("nan"), float("inf")])
def test_rejects_invalid_phase(phase):
    with pytest.raises(ValueError):
        AssemblyBreathing().state(phase)


def test_cycle_extrema_periodicity_and_analytic_jacobian():
    cycle = AssemblyBreathing()
    assert [cycle.state(p)["scale"] for p in (0, 0.25, 0.5, 0.75, 1)] == [1, 1.1, 1, 0.9, 1]
    assert cycle.state(0) == cycle.state(1)
    for p in np.linspace(0, 1, 101):
        s = cycle.state(p)["scale"]
        assert s >= 0.9
        assert np.linalg.det(s * np.eye(3)) >= 0.729 - 1e-15
        x = np.array((3.4, -5.6, 1.2))
        np.testing.assert_allclose(cycle.inverse(cycle.forward(x, p), p), x, rtol=1e-14)
    assert AssemblyBreathing(0).state(0.125)["scale_rate_per_phase"] == 0


@pytest.fixture(scope="module", params=[1.0, -1.0])
def assembly(request):
    return BreathingAssembly(request.param)


def test_both_aperture_holes_follow_the_actual_moving_domains(assembly):
    ref, patch = assembly.reference, assembly.second
    charts = [
        (ref.host_name, lambda x: np.asarray(ref.origin) + np.asarray(x) * (1, ref.sign, ref.sign)),
        (patch.host.name, patch.to_global),
    ]
    for name, place in charts:
        hole = place((12.4, 0, 0))
        material = place((-12.4, 0, 0))
        for phase in (0, 0.25, 0.75, 1):
            xhole = assembly.cycle.forward(hole, phase)
            xmaterial = assembly.cycle.forward(material, phase)
            assert not assembly.contains(name, xhole, phase)
            assert assembly.relative_current(name, xhole, phase) is None
            assert assembly.contains(name, xmaterial, phase)
            j = assembly.relative_current(name, xmaterial, phase)
            j0 = assembly.relative_current(name, material, 0)
            np.testing.assert_allclose(
                j * assembly.cycle.state(phase)["scale"] ** 2, j0, atol=1e-15, rtol=1e-12
            )


def test_nonuniform_density_obeys_eulerian_continuity_and_material_transport():
    cycle = AssemblyBreathing()

    # A nonconstant density prevents a material derivative from accidentally
    # replacing the Eulerian derivative at fixed spatial x.
    def rho0(X):
        return 2 + 0.1 * np.dot(X, X)

    def rho(x, p):
        return cycle.density(rho0(cycle.inverse(x, p)), p)

    def lab(x, p):
        X = cycle.inverse(x, p)
        divergence_free = (-X[1], X[0], 0.3)
        return cycle.lab_current(x, divergence_free, rho0(X), p)

    x, phase, step = np.array((1.2, -0.7, 0.3)), 0.13, 1e-5
    partial = (rho(x, phase + step) - rho(x, phase - step)) / (2 * step)
    divergence = sum(
        (lab(x + step * e, phase)[i] - lab(x - step * e, phase)[i]) / (2 * step)
        for i, e in enumerate(np.eye(3))
    )
    assert abs(partial + divergence) < 1e-8
    X = cycle.inverse(x, phase)
    material_rate = (
        rho(cycle.forward(X, phase + step), phase + step)
        - rho(cycle.forward(X, phase - step), phase - step)
    ) / (2 * step)
    assert abs(material_rate - partial) > 1e-3
    for p in (0, 0.125, 0.25, 0.75, 1):
        assert rho(cycle.forward(X, p), p) * cycle.state(p)["determinant"] == pytest.approx(rho0(X))


def test_density_jump_requires_relative_not_lab_current_balance():
    cycle = AssemblyBreathing()
    x, j0, phase = np.array((1.0, 2.0, 3.0)), (0, 0, 0.4), 0.1
    w = cycle.velocity(x, phase)
    left = cycle.lab_current(x, j0, 1, phase)
    right = cycle.lab_current(x, j0, 3, phase)
    assert abs(left[2] - right[2]) > 0.1
    np.testing.assert_allclose(
        left - cycle.density(1, phase) * w,
        right - cycle.density(3, phase) * w,
        rtol=1e-13,
        atol=1e-14,
    )


@pytest.mark.parametrize("current", [1.0, -1.0, 2e-8, -2e-8, 7.0, -7.0])
def test_six_signed_cases_keep_complete_inventory_and_moving_flux(current):
    report = audit_assembly_breathing(current)
    assert (
        report["component_count"],
        report["pair_count"],
        report["interface_count"],
        report["port_count"],
    ) == (69, 2346, 62, 8)
    assert len(report["moving_cut_diagnostics"]) == 48
    assert report["maximum_relative_cut_error"] < 1e-10
    assert math.isclose(report["minimum_deformation_determinant"], 0.729)
    assert report["continuous_common_similarity_clearance"]
    assert not report["relative_folding_validated"]
    assert not report["emergent_motion_validated"]
    assert not report["material_energy_validated"]
