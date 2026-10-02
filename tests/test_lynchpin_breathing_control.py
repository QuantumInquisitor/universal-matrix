import math

import numpy as np
import pytest

from src.lynchpin_breathing_control import BreathingCycle
from src.lynchpin_finite_panel_control import panel_vertices, separation_bound


def polygon_area(vertices):
    vertices = np.array(vertices)
    area = 0.0
    for i in range(1, len(vertices) - 1):
        a, b = vertices[i] - vertices[0], vertices[i + 1] - vertices[0]
        area += 0.5 * math.sqrt(max(0.0, np.dot(a, a) * np.dot(b, b) - np.dot(a, b) ** 2))
    return area


@pytest.mark.parametrize("dimension", (3, 4))
def test_actual_panel_area_and_density_conserve_material(dimension):
    cycle = BreathingCycle()
    for panel in range(6):
        original_area = polygon_area(panel_vertices(0, dimension, panel, 0.15))
        for phase in (0, 0.13, 0.25, 0.5, 0.75, 0.91, 1):
            result = cycle.panel(phase, dimension, panel)
            area = polygon_area(result["vertices"])
            assert area / original_area == pytest.approx(result["area_ratio"], rel=1e-12)
            assert area * result["material_surface_density_ratio"] == pytest.approx(
                original_area, rel=1e-12
            )
            assert result["total_core_thickness"] == pytest.approx(
                0.02 * cycle.state(phase)["scale"]
            )


def test_breath_cycle_closes_and_expands_and_contracts():
    cycle = BreathingCycle()
    assert cycle.state(0) == cycle.state(1)
    assert cycle.state(0.25)["scale"] == 1.1
    assert cycle.state(0.75)["scale"] == 0.9
    assert cycle.state(0.25)["scale_rate_per_phase"] == 0
    assert cycle.state(0.75)["scale_rate_per_phase"] == 0
    for dimension in (3, 4):
        for panel in range(6):
            np.testing.assert_allclose(
                cycle.panel(0, dimension, panel)["vertices"],
                cycle.panel(1, dimension, panel)["vertices"],
                atol=1e-14,
            )


@pytest.mark.parametrize("phase", (0.13, 0.25, 0.5, 0.75, 0.91))
def test_independent_continuity_and_moving_face_flux(phase):
    cycle, h = BreathingCycle(), 1e-6
    density = 2.3
    reference = np.array((0.2, -0.4, 0.7))
    position = np.array((0.3, -0.7, 1.1))
    density_rate = (
        density
        * (
            cycle.state(phase + h)["similarity_density_ratio"]
            - cycle.state(phase - h)["similarity_density_ratio"]
        )
        / (2 * h)
    )
    divergence = 0.0
    for i in range(3):
        delta = np.eye(3)[i] * h
        divergence += (
            cycle.similarity_lab_current(phase, position + delta, reference, density)[i]
            - cycle.similarity_lab_current(phase, position - delta, reference, density)[i]
        ) / (2 * h)
    assert abs(density_rate + divergence) < 2e-8
    state = cycle.state(phase)
    scale = state["scale"]
    wall_velocity = position * state["scale_rate_per_phase"] / scale
    lab_current = cycle.similarity_lab_current(phase, position, reference, density)
    relative = lab_current - density / scale**3 * wall_velocity
    # Independent area scaling of a material square with unit reference normal Z.
    assert relative[2] * scale**2 == pytest.approx(reference[2], rel=1e-12)
    # Omitting advective current breaks continuity except at stationary size.
    if phase not in (0.25, 0.75):
        assert abs(density_rate) > 0.1


@pytest.mark.parametrize("dimension", (3, 4))
def test_core_gap_and_thickness_scale_together(dimension):
    cycle = BreathingCycle()
    for phase in (0.25, 0.75):
        a, b = panel_vertices(phase, dimension, 0, 0.15), panel_vertices(phase, dimension, 5, 0.15)
        scale = cycle.state(phase)["scale"]
        original = separation_bound(a, b)["lower_bound"] - 0.02
        scaled = separation_bound(scale * a, scale * b)["lower_bound"] - 0.02 * scale
        assert scaled == pytest.approx(scale * original, rel=1e-8, abs=1e-10)


@pytest.mark.parametrize("amplitude", (-0.1, 1.0, 2.0, float("nan"), True, 1j))
def test_nonpositive_or_invalid_cycle_scales_are_rejected(amplitude):
    with pytest.raises(ValueError):
        BreathingCycle(amplitude)


def test_zero_amplitude_is_a_static_scale_control():
    cycle = BreathingCycle(0)
    assert cycle.state(0.3)["scale"] == 1
    np.testing.assert_allclose(
        cycle.similarity_lab_current(0.3, (2, 3, 4), (0.2, 0.3, 0.4)), (0.2, 0.3, 0.4)
    )
