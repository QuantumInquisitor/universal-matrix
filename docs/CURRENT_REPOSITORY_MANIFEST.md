# Current Repository Manifest

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Baseline:** White Paper v0.6 / Software v0.4.0  
**Status:** Current operational manifest  
**Updated:** September 2026

This document is the current high-level repository map.

For authority and historical-status rules, see `docs/DOCUMENTATION_STATUS.md`.

## 1. Canonical core

Primary authority:

- `src/canonical_kernel.py`
- `tests/test_canonical_kernel.py`
- `docs/canonical_spec_v0.4.md`
- `white_paper.md`

The canonical finite architecture is the 108-state cyclic core plus six external boundary orientations.

## 2. Ontology and nested dynamics

Current experimental modules include:

- `src/matrix_ontology.py`
- `src/nested_polarity_dynamics.py`
- `src/polarity_oscillator.py`
- `src/canonical_polarity_clock.py`
- `src/scale_transfer.py`
- `src/canonical_scale_transfer.py`
- `src/matrix_local_transition.py`
- `src/matrix_polarity_phase_bridge.py`
- `src/recursive_omniverse_contract.py`
- `src/sevenfold_seed_contract.py`
- `src/universe_port_engine.py`
- `src/vesica_tree_circulation.py`
- `src/transitive_plane_branching.py`
- `src/sri_yantra_multidimensional.py`
- `src/higher_dimensional_geometry.py`

The current ontology distinguishes exact canonical address structure from candidate physical variables. The local-transition layer adds the minimal gauge-covariant nearest-neighbor Hamiltonian used to test locality, conservative exchange, and the weak-field wave limit. The polarity-phase bridge removes redundant polarity bookkeeping by proving equivalence between branch sign, pi-shifted effective phase, and the fixed-amplitude rotor reduction where their assumptions overlap. The recursive port layer supplies exact contained circle, Seed, Vesica, Flower, and Tree geometry, then exposes polarity-clock and negative-space adapters as explicit hypotheses rather than physical facts. The circulation layer adds a dimensionless graph continuity law, balanced Vesica and Tree currents, and a separately typed parent-child scale current without assigning a physical identity to the conserved content. The plane layer adds an open overlap graph and a mirror-paired possibility address while rejecting any elementary move that conflates scale, plane, and branch coordinates. The Sri Yantra layer attaches an embedding-independent enclosure fibre over that product address, distinguishes plane, spherical, Meru, simplex, and spiral-cone realizations, and preserves separate phase, flow, mirror, and handedness operations.

## 3. Open field and gauge systems

Current field engines include:

- open DEC and boundary solvers;
- compact U(1);
- SU(2);
- SU(3);
- matter coupling;
- geometry weighting;
- Hamiltonian reference implementations.

Representative paths:

- `src/open_gauge_dynamics.py`
- `src/open_boundary_solver.py`
- `src/unified_engine.py`
- `src/su2_lattice_gauge.py`
- `src/su3_lattice_gauge.py`

## 4. Reciprocity geometry

Current research modules include:

- scalar reciprocity geometry;
- static and dynamic source coupling;
- stationary-source universality;
- vacuum exterior analysis;
- higher-order weak-field predictions;
- circular orbits and second-order light deflection;
- matter and non-Abelian geometry backreaction.

The reciprocity premises remain experimental assumptions until derived from the canonical kernel.

## 5. Fermion and chiral program

Current modules include:

- Wilson-Dirac references;
- reciprocity-background Dirac dynamics;
- analytic Dirac geometry sources;
- semiclassical Dirac backreaction;
- overlap/Ginsparg-Wilson operators;
- Weyl projectors;
- measure curvature and holonomy;
- finite Weyl determinants;
- U(1), SU(2), SU(3), and product-group overlap constructions;
- anomaly ledgers.

The repository does not yet contain a complete second-quantized chiral gauge theory.

## 6. Spatial, robotics, and XR

Current product modules include:

- `src/spatial_protocol.py`
- `src/spatial_operations_control.py`
- `src/robot_adapter.py`
- `src/xr_robot_bridge.py`

The product path is:

```text
operator / XR client
    -> spatial protocol
    -> bounded command validation
    -> robot adapter
    -> customer-specific driver
```

Real hardware remains fail-closed and requires independent physical safety systems.

## 7. Digital twins

Current modules include:

- `src/digital_twin_contract.py`
- `src/digital_twin_store.py`

The telemetry contract separates measured values from derived estimates and preserves units, source, timestamp, quality, calibration, and uncertainty metadata.

## 8. Manufacturing and hardware compatibility

The repository includes experimental or compatibility modules for:

- G-code and toolpaths;
- CNC/GRBL;
- CAN;
- ROS2-style bridges;
- sensor ingestion;
- CUDA/FPGA/QPU/photonic adapters;
- RF/SDR;
- HIL mocks;
- edge orchestration.

These surfaces have different maturity levels. Historical labels in compatibility modules are not canonical unless separately documented and tested.

## 9. API and SDK surfaces

Current secured API:

- `src/api_server.py`

Current client SDKs:

- `sdk/python/universal_matrix_sdk.py`
- `sdk/js/universalMatrixSdk.js`

The broader `src/api.py` remains a legacy/experimental compatibility surface.

## 10. Deployment and observability

Current infrastructure includes:

- Docker;
- Docker Compose;
- Kubernetes;
- Helm;
- Prometheus;
- Grafana;
- CodeQL;
- Python 3.12/3.14 verification;
- full compatibility tests;
- container smoke tests;
- SBOM/provenance generation.

## 11. Licensing and governance

Public source license:

- PolyForm Noncommercial License 1.0.0

Commercial licensing:

- Waters Legacy Trust proprietary commercial license

Governance files:

- `LICENSE`
- `NOTICE`
- `COMMERCIAL_LICENSE.md`
- `COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md`
- `CLA.md`
- `CONTRIBUTING.md`
- `docs/LICENSING_GUIDE.md`

## 12. Documentation hierarchy

Current authority:

- `README.md`
- `white_paper.md`
- `ARCHITECTURE.md`
- `docs/DOCUMENTATION_STATUS.md`
- `docs/HOW_TO_USE.md`
- `docs/canonical_spec_v0.4.md`
- `docs/physics_stack_status_2026-09.md`
- `docs/omniverse_design_questions_v0.1.md`

Historical/provenance files are retained with explicit banners and do not override current authority.

## 13. Repository hygiene

Generated artifacts such as Python bytecode, `__pycache__`, and runtime audit logs are ignored and must not be committed.

The CI documentation-governance tests enforce current authority, licensing terminology, white-paper uniqueness, and historical-document labeling.


## Higher-dimensional finite geometry

The current geometry manifest also includes `src/higher_dimensional_geometry.py`.
It constructs arbitrary-dimensional simplex, hypercube, and cross-polytope
families, tests central-mirror and recursive-projection behavior, constructs
the 240 E8 roots exactly, and embeds the existing 24-cell dual D4 subsystem.
The E8 layer remains mathematical and exploratory; no physical eight-dimensional
ontology is declared.
