import math

from src.nested_oscillatory_hierarchy import (
    NestedOscillatorLayer,
    OscillatoryScaleHierarchy,
)
from src.phase_roles import PhaseState


def _layers():
    return [
        NestedOscillatorLayer(
            layer_id=0,
            base_node=0,
            phases=PhaseState(polarity_phase=0.0, gauge_phase=0.2),
            amplitude=1.0,
            angular_rate=1.0,
        ),
        NestedOscillatorLayer(
            layer_id=1,
            base_node=1,
            phases=PhaseState(polarity_phase=0.4, gauge_phase=-0.3),
            amplitude=0.4,
            angular_rate=0.8,
        ),
        NestedOscillatorLayer(
            layer_id=2,
            base_node=2,
            phases=PhaseState(polarity_phase=1.0, gauge_phase=0.7),
            amplitude=-0.2,
            angular_rate=0.6,
        ),
    ]


def test_hierarchy_conserves_quadratic_content_over_many_steps():
    hierarchy = OscillatoryScaleHierarchy(
        _layers(),
        transfer_coupling=0.4,
        gauge_coupling=0.2,
        link_phases=[0.1, -0.2],
    )
    before = hierarchy.total_quadratic_content()
    for _ in range(500):
        hierarchy.step(0.01)
    after = hierarchy.total_quadratic_content()

    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-11)
    assert hierarchy.verify_quadratic_conservation(1e-11)


def test_gauge_energy_does_not_change_when_only_polarity_phase_advances():
    hierarchy = OscillatoryScaleHierarchy(
        _layers(),
        transfer_coupling=0.0,
        gauge_coupling=0.3,
        link_phases=[0.2, 0.4],
    )
    before = hierarchy.total_gauge_link_energy()
    hierarchy.step(0.5)
    after = hierarchy.total_gauge_link_energy()

    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-14)


def test_half_cycle_changes_canonical_polarity_state():
    layer = NestedOscillatorLayer(
        layer_id=0,
        base_node=11,
        phases=PhaseState(polarity_phase=0.0, gauge_phase=0.0),
        amplitude=1.0,
        angular_rate=1.0,
    )
    hierarchy = OscillatoryScaleHierarchy([layer], transfer_coupling=0.0)
    node0 = layer.canonical_node
    polarity0 = layer.polarity

    hierarchy.step(math.pi)

    assert layer.canonical_node != node0
    assert layer.polarity == -polarity0


def test_telemetry_exposes_separate_phase_roles():
    hierarchy = OscillatoryScaleHierarchy(_layers())
    telemetry = hierarchy.step(0.1)
    assert "polarity_phase" in telemetry[0]
    assert "gauge_phase" in telemetry[0]
    assert telemetry[0]["model_status"] == "experimental_nested_oscillatory_hierarchy"


def test_canonical_tick_advance_is_content_independent_but_physical_time_is_not():
    layers = [
        NestedOscillatorLayer(
            layer_id=0,
            base_node=0,
            phases=PhaseState(polarity_phase=0.0, gauge_phase=0.0),
            amplitude=0.5,
        ),
        NestedOscillatorLayer(
            layer_id=1,
            base_node=1,
            phases=PhaseState(polarity_phase=0.0, gauge_phase=0.0),
            amplitude=2.0,
        ),
    ]
    hierarchy = OscillatoryScaleHierarchy(
        layers,
        transfer_coupling=0.0,
        gauge_coupling=0.0,
    )

    telemetry = hierarchy.step_routing_tick(
        reference_tick_duration=1.0,
        content_clock_coupling=0.2,
        reference_content=0.0,
    )

    assert math.isclose(
        layers[0].phases.polarity_phase,
        layers[1].phases.polarity_phase,
        abs_tol=1e-15,
    )
    assert telemetry[1]["physical_elapsed_time"] > telemetry[0]["physical_elapsed_time"]
    assert telemetry[1]["clock_rate_ratio"] < telemetry[0]["clock_rate_ratio"]


def test_eighteen_canonical_ticks_apply_polarity_involution_for_all_contents():
    layers = [
        NestedOscillatorLayer(
            layer_id=0,
            base_node=12,
            phases=PhaseState(polarity_phase=0.0, gauge_phase=0.0),
            amplitude=0.2,
        ),
        NestedOscillatorLayer(
            layer_id=1,
            base_node=30,
            phases=PhaseState(polarity_phase=0.0, gauge_phase=0.0),
            amplitude=1.7,
        ),
    ]
    hierarchy = OscillatoryScaleHierarchy(
        layers,
        transfer_coupling=0.0,
        gauge_coupling=0.0,
    )
    initial_nodes = [layer.canonical_node for layer in layers]

    for _ in range(18):
        hierarchy.step_routing_tick(
            reference_tick_duration=0.5,
            content_clock_coupling=0.3,
        )

    for layer, initial_node in zip(layers, initial_nodes):
        assert layer.canonical_node != initial_node
        assert layer.polarity == -1

    assert layers[1].physical_elapsed_time > layers[0].physical_elapsed_time


def test_content_clock_tick_path_preserves_quadratic_content_with_transfer():
    hierarchy = OscillatoryScaleHierarchy(
        _layers(),
        transfer_coupling=0.25,
        gauge_coupling=0.0,
    )
    before = hierarchy.total_quadratic_content()

    for _ in range(72):
        hierarchy.step_routing_tick(
            reference_tick_duration=1.0,
            content_clock_coupling=0.1,
        )

    after = hierarchy.total_quadratic_content()
    assert math.isclose(before, after, rel_tol=0, abs_tol=1e-10)
