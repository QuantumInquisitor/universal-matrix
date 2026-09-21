import cmath
import math

from src import canonical_kernel as ck
from src.theory_bridge import (
    BRIDGES,
    causal_history,
    causal_precedes,
    discrete_compact_modes,
    interface_modes,
    routing_modes,
    routing_winding_number,
    scale_network_edges,
    transformed_wilson_loop,
    u1_wilson_loop,
)


def test_bridge_registry_has_required_frameworks():
    required = {
        "string_compact_cycle",
        "m_theory",
        "loop_quantum_gravity",
        "causal_set",
        "holographic_tensor_network",
        "lattice_gauge",
        "regge_cdt",
    }
    assert required <= set(BRIDGES)


def test_discrete_fourier_modes_are_orthonormal():
    modes = discrete_compact_modes(12)
    for i, a in enumerate(modes):
        for j, b in enumerate(modes):
            inner = sum(x.conjugate() * y for x, y in zip(a, b))
            if i == j:
                assert abs(inner - 1.0) < 1e-12
            else:
                assert abs(inner) < 1e-12


def test_interface_and_routing_mode_counts():
    assert len(interface_modes()) == 12
    assert len(routing_modes()) == 36


def test_canonical_and_reverse_winding():
    assert routing_winding_number(ck.ROUTING_STEP) == 7
    assert routing_winding_number(-ck.ROUTING_STEP) == -7


def test_u1_wilson_loop_is_locally_gauge_invariant():
    links = [0.1, 0.2, -0.4, 0.3]
    gauges = [0.7, -0.2, 1.1, 0.4]
    original = u1_wilson_loop(links)
    transformed = transformed_wilson_loop(links, gauges)
    assert abs(original - transformed) < 1e-12


def test_causal_history_unwraps_closed_core_cycle():
    history = causal_history(0, 36)
    assert len(history) == 37
    assert history[0][1] == history[-1][1]
    assert history[0] != history[-1]
    assert causal_precedes(history[0], history[-1])


def test_scale_network_edges():
    assert scale_network_edges(4) == ((0, 1), (1, 2), (2, 3))
