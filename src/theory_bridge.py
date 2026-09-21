"""Optional theory-bridge adapters for the Universal Matrix.

These utilities expose mathematically legitimate correspondences to structures
used in other theoretical frameworks. They do not assert physical equivalence
between the Universal Matrix and string theory, M-theory, loop quantum gravity,
causal-set theory, holography, or lattice gauge theory.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Iterable, Sequence

try:
    from . import canonical_kernel as ck
except ImportError:
    import canonical_kernel as ck


@dataclass(frozen=True)
class TheoryBridge:
    name: str
    compatibility: str
    matrix_structure: str
    external_structure: str
    usable_mapping: str
    missing_requirements: tuple[str, ...]


BRIDGES = {
    "string_compact_cycle": TheoryBridge(
        name="String/Kaluza-Klein compact-cycle analogue",
        compatibility="strong-mathematical-analogy",
        matrix_structure="finite cyclic interface/routing orbits",
        external_structure="mode/winding decomposition on compact dimensions",
        usable_mapping="discrete Fourier modes and integer winding on Z_N",
        missing_requirements=(
            "worldsheet action",
            "string tension",
            "supersymmetry",
            "critical-dimension dynamics",
            "physical compactification geometry",
        ),
    ),
    "m_theory": TheoryBridge(
        name="M-theory",
        compatibility="weak-structural-analogy",
        matrix_structure="nested layers and higher-dimensional feature adapters",
        external_structure="11-dimensional theory with branes and supergravity limit",
        usable_mapping="none beyond generic dimensional bookkeeping",
        missing_requirements=(
            "11D Lorentzian dynamics",
            "supersymmetry",
            "2-branes and 5-branes",
            "3-form gauge field",
            "supergravity low-energy limit",
        ),
    ),
    "loop_quantum_gravity": TheoryBridge(
        name="Loop quantum gravity / spin networks",
        compatibility="partial-graph-analogy",
        matrix_structure="finite graph of states and routing/coupling edges",
        external_structure="spin networks with SU(2) representation labels and intertwiners",
        usable_mapping="Matrix graph can serve as an unlabeled graph substrate only",
        missing_requirements=(
            "SU(2) edge representations",
            "vertex intertwiners",
            "area operator",
            "volume operator",
            "Hamiltonian constraint",
        ),
    ),
    "causal_set": TheoryBridge(
        name="Causal-set theory",
        compatibility="strong-history-analogy",
        matrix_structure="discrete time-unwrapped transition history",
        external_structure="locally finite partially ordered causal events",
        usable_mapping="use time-unwrapped events, not cyclic core labels, as poset elements",
        missing_requirements=(
            "physical causal interpretation",
            "Lorentz-invariant continuum approximation",
            "causal-set dynamics/path sum",
        ),
    ),
    "holographic_tensor_network": TheoryBridge(
        name="Holography / tensor-network scale geometry",
        compatibility="partial-scale-analogy",
        matrix_structure="nested micro-to-macro layers with nearest-neighbor coupling",
        external_structure="multi-scale tensor networks with scale as an emergent direction",
        usable_mapping="layer index can act as a scale coordinate in a network adapter",
        missing_requirements=(
            "Hilbert-space tensor factorization",
            "entanglement entropy",
            "isometric tensors",
            "AdS geometry",
            "boundary conformal field theory",
        ),
    ),
    "lattice_gauge": TheoryBridge(
        name="Lattice gauge theory",
        compatibility="strong-mathematical-bridge",
        matrix_structure="finite directed links between discrete states",
        external_structure="group-valued link variables and gauge-invariant loop observables",
        usable_mapping="attach U(1) phases to Matrix links and compute Wilson-loop holonomy",
        missing_requirements=(
            "gauge action",
            "matter representations",
            "continuum limit",
            "physical coupling identification",
        ),
    ),
    "regge_cdt": TheoryBridge(
        name="Regge calculus / causal dynamical triangulations",
        compatibility="weak",
        matrix_structure="finite cyclic graph and nested layers",
        external_structure="simplicial Lorentzian geometry with curvature/triangulations",
        usable_mapping="none without adding simplices and geometric edge lengths",
        missing_requirements=(
            "simplicial complex",
            "edge lengths",
            "deficit angles",
            "Lorentzian triangulation rules",
        ),
    ),
}


def bridge_summary(name: str) -> TheoryBridge:
    return BRIDGES[name]


def discrete_compact_modes(size: int) -> tuple[tuple[complex, ...], ...]:
    """Return the complete discrete Fourier basis on Z_size.

    This is the exact finite analogue of mode decomposition on a compact circle.
    It is mathematical infrastructure only; it is not a string compactification.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    modes = []
    norm = 1.0 / math.sqrt(size)
    for k in range(size):
        modes.append(
            tuple(
                norm * cmath.exp(2j * math.pi * k * n / size)
                for n in range(size)
            )
        )
    return tuple(modes)


def interface_modes() -> tuple[tuple[complex, ...], ...]:
    """Fourier basis on the order-12 E=T9 interface cycle."""
    return discrete_compact_modes(12)


def routing_modes() -> tuple[tuple[complex, ...], ...]:
    """Fourier basis on one 36-state T21 routing orbit."""
    return discrete_compact_modes(36)


def routing_winding_number(step: int = ck.ROUTING_STEP) -> int:
    """Signed winding number of a 36-step routing orbit.

    For the canonical step 21 this is +7. For the inverse step 87 it is -7
    when represented by the shortest signed displacement -21.
    """
    d = step % ck.N_CORE
    signed = d if d <= ck.N_CORE // 2 else d - ck.N_CORE
    turns = 36 * signed
    if turns % ck.N_CORE:
        raise ValueError("step does not close after 36 routing steps")
    return turns // ck.N_CORE


def u1_link(phase: float) -> complex:
    """U(1) link variable exp(i*phase)."""
    return cmath.exp(1j * phase)


def u1_wilson_loop(link_phases: Sequence[float]) -> complex:
    """Gauge-invariant U(1) holonomy for a closed oriented loop adapter."""
    value = 1.0 + 0.0j
    for phase in link_phases:
        value *= u1_link(phase)
    return value


def u1_gauge_transform_link(
    link_phase: float,
    source_gauge_phase: float,
    target_gauge_phase: float,
) -> float:
    """Transform a U(1) link angle theta_ij -> theta_ij + a_i - a_j."""
    return (
        link_phase + source_gauge_phase - target_gauge_phase
    ) % (2.0 * math.pi)


def transformed_wilson_loop(
    link_phases: Sequence[float],
    vertex_gauge_phases: Sequence[float],
) -> complex:
    """Apply local U(1) gauge phases around a closed loop then compute holonomy."""
    if len(link_phases) != len(vertex_gauge_phases):
        raise ValueError("closed loop requires one link and one gauge phase per vertex")
    transformed = []
    count = len(link_phases)
    for i, phase in enumerate(link_phases):
        transformed.append(
            u1_gauge_transform_link(
                phase,
                vertex_gauge_phases[i],
                vertex_gauge_phases[(i + 1) % count],
            )
        )
    return u1_wilson_loop(transformed)


def causal_history(
    initial_node: int,
    steps: int,
    polarity: int = 1,
) -> tuple[tuple[int, int], ...]:
    """Unwrap cyclic routing into an acyclic event history (tick,node).

    The event order is supplied by tick. Core labels may repeat after closure,
    but events remain distinct because their ticks differ.
    """
    if steps < 0:
        raise ValueError("steps must be non-negative")
    if polarity not in (-1, 1):
        raise ValueError("polarity must be -1 or +1")
    node = initial_node % ck.N_CORE
    events = [(0, node)]
    signed_step = polarity * ck.ROUTING_STEP
    for tick in range(1, steps + 1):
        node = ck.translate(node, signed_step)
        events.append((tick, node))
    return tuple(events)


def causal_precedes(event_a: tuple[int, int], event_b: tuple[int, int]) -> bool:
    """Minimal history-order relation: earlier tick precedes later tick."""
    return event_a[0] < event_b[0]


def scale_network_edges(layer_count: int) -> tuple[tuple[int, int], ...]:
    """Nearest-neighbor edges for a 1D multi-scale tensor-network adapter."""
    if layer_count <= 0:
        raise ValueError("layer_count must be positive")
    return tuple((i, i + 1) for i in range(layer_count - 1))
