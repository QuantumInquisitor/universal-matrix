import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import canonical_kernel as ck
from lattice_quantum_engine import LatticeQuantumEngine


def test_lattice_uses_canonical_architecture():
    engine = LatticeQuantumEngine()
    assert engine.core_nodes == 108
    assert engine.boundary_gates == 6
    assert engine.total_nodes == 114
    assert engine.boundary_gate_ids == tuple(range(108, 114))


def test_external_flux_is_written_only_to_external_gate_indices_before_core_cascade():
    engine = LatticeQuantumEngine()
    flux = [1, 2, 3, 4, 5, 6]
    engine.inject_multi_vector_flux(flux)

    assert all(engine.state_lattice[n] != 0 for n in range(108, 114))
    assert engine.state_lattice.shape == (114,)


def test_register_signature_uses_canonical_projection():
    engine = LatticeQuantumEngine()
    for node in range(108):
        _, _, address = engine._get_node_bit_signature(node)
        assert address == ck.register_address(node)


def test_legacy_harmonic_six_branch_is_reachable():
    assert LatticeQuantumEngine._routing_harmonic(3) == 3
    assert LatticeQuantumEngine._routing_harmonic(6) == 6
    assert LatticeQuantumEngine._routing_harmonic(9) == 9
    assert LatticeQuantumEngine._routing_harmonic(18) == 9


def test_density_normalization_and_node_classes():
    engine = LatticeQuantumEngine()
    engine.inject_multi_vector_flux([1, 2, 3, 4, 5, 6])
    result = engine.execute_measurement_collapse()

    densities = np.array([
        entry["normalized_density"]
        for entry in result["full_lattice_density_matrix"].values()
    ])
    # Stored JSON-facing values are rounded to six decimals.
    assert abs(float(np.sum(densities)) - 1.0) < 1e-4
    assert result["full_lattice_density_matrix"]["node_107"]["node_class"] == "internal_core"
    assert result["full_lattice_density_matrix"]["node_108"]["node_class"] == "external_boundary"
