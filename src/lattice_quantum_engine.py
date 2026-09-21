#!/usr/bin/env python3
"""Exploratory finite-lattice cascade engine.

The canonical architecture is a 108-state internal core plus six external
boundary gates. Numerical field calculations in this module are experimental
and are not claims of quantum, gravitational, or vacuum physics.
"""

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
    import canonical_kernel as ck
except ImportError:
    print("CRITICAL: calculator.py and canonical_kernel.py must be present.")
    sys.exit(1)


class LatticeQuantumEngine:
    """Experimental field engine constrained by the canonical node topology."""

    def __init__(self):
        self.total_nodes = ck.M_TOTAL
        self.core_nodes = ck.N_CORE
        self.boundary_gates = ck.BOUNDARY_COUNT
        self.boundary_gate_ids = tuple(ck.BOUNDARY_GATES.values())
        self.calculator = mc.UniversalMatrixCalculator()

        self.state_lattice = np.zeros(self.total_nodes, dtype=complex)
        self.interference_amplitudes = np.zeros(self.total_nodes)

    def _get_node_bit_signature(self, node_id: int) -> tuple:
        """Return legacy stream bits using the canonical 64-address projection."""
        bit_shift_offset = ck.register_address(node_id)
        up_bit = (self.calculator.STREAM_UP >> bit_shift_offset) & 1
        down_bit = (self.calculator.STREAM_DOWN >> bit_shift_offset) & 1
        return up_bit, down_bit, bit_shift_offset

    @staticmethod
    def _routing_harmonic(node_id: int) -> int:
        """Legacy 3/6/9 label with reachable, explicit precedence.

        This is a classification helper only. It is not a canonical operator.
        """
        if node_id % 9 == 0:
            return 9
        if node_id % 6 == 0:
            return 6
        if node_id % 3 == 0:
            return 3
        return 1

    def _boundary_state(self, flux_val: float) -> complex:
        phase_angle = flux_val * mc.ALPHA_GEOMETRIC * 2.0 * math.pi
        return complex(math.cos(phase_angle), math.sin(phase_angle))

    def inject_multi_vector_flux(self, external_flux_matrix: list):
        """Inject six external values and interpolate them over the internal core.

        Boundary nodes remain 108..113 and are never reinterpreted as core nodes.
        The interpolation itself is an experimental numerical rule.
        """
        if len(external_flux_matrix) != self.boundary_gates:
            raise ValueError(
                f"Flux inputs must match the {self.boundary_gates} external gates. "
                f"Got {len(external_flux_matrix)}"
            )

        self.state_lattice.fill(0.0)

        gate_states = []
        for gate_node, flux_val in zip(self.boundary_gate_ids, external_flux_matrix):
            state = self._boundary_state(flux_val)
            gate_states.append(state)
            self.state_lattice[gate_node] = state

        # Map the six external orientations to six equal phase sectors of the
        # 108-state core. This is an interpolation convention, not a new gate map.
        sector_width = self.core_nodes // self.boundary_gates  # 18
        for node_id in range(self.core_nodes):
            sector = node_id // sector_width
            next_sector = (sector + 1) % self.boundary_gates
            local = node_id % sector_width
            fraction = local / float(sector_width)

            left_state = gate_states[sector]
            right_state = gate_states[next_sector]
            combined_phase = ((1.0 - fraction) * left_state) + (fraction * right_state)

            up_bit, down_bit, _ = self._get_node_bit_signature(node_id)
            bit_modulation = (up_bit * 1.5) - (down_bit * 0.5)
            harmonic = self._routing_harmonic(node_id)

            self.state_lattice[node_id] = (
                combined_phase
                * harmonic
                * bit_modulation
                * mc.ALPHA_GEOMETRIC
            )

    def execute_measurement_collapse(self) -> dict:
        """Normalize squared magnitudes into an experimental density map."""
        magnitudes = np.abs(self.state_lattice) ** 2
        total_mass = float(np.sum(magnitudes))
        if total_mass == 0.0:
            total_mass = 1.0

        self.interference_amplitudes[:] = magnitudes / total_mass
        density_map = {}

        for node_id, normalized_density in enumerate(self.interference_amplitudes):
            density_map[f"node_{node_id}"] = {
                "raw_complex_state": str(self.state_lattice[node_id]),
                "normalized_density": round(float(normalized_density), 6),
                "is_above_uniform_density": bool(
                    normalized_density > (1.0 / self.total_nodes)
                ),
                "node_class": (
                    "external_boundary"
                    if node_id in self.boundary_gate_ids
                    else "internal_core"
                ),
            }

        highest_density_node = int(np.argmax(self.interference_amplitudes))
        lowest_density_node = int(np.argmin(self.interference_amplitudes))

        return {
            "simulation_metrics": {
                "total_squared_magnitude": round(total_mass, 4),
                "highest_density_node": highest_density_node,
                "lowest_density_node": lowest_density_node,
            },
            "full_lattice_density_matrix": density_map,
        }


def main():
    print("Initializing exploratory finite-lattice cascade simulation...")
    engine = LatticeQuantumEngine()
    mock_flux_values = [1.23, 4.56, 7.89, 9.87, 6.54, 3.21]
    engine.inject_multi_vector_flux(mock_flux_values)
    results = engine.execute_measurement_collapse()

    print(json.dumps(results["simulation_metrics"], indent=2))
    print("Sample internal node 0:")
    print(json.dumps(results["full_lattice_density_matrix"]["node_0"], indent=2))
    print("Sample external gate 108:")
    print(json.dumps(results["full_lattice_density_matrix"]["node_108"], indent=2))


if __name__ == "__main__":
    main()
