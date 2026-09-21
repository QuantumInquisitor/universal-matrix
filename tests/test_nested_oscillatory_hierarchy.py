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
