# Universal Matrix Usage Guide

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Baseline:** Software v0.4.0 / White Paper v0.6  
**Status:** Current

This guide describes the current development, research, API, spatial, robotics, digital-twin, manufacturing, and licensing workflows.

For documentation authority, see docs/DOCUMENTATION_STATUS.md.

## 1. Environment

Python 3.12 or newer is supported. CI exercises the core stack on Python 3.12 and 3.14.

Recommended setup:

~~~bash
git clone https://github.com/QuantumInquisitor/universal-matrix.git
cd universal-matrix
uv sync --group dev --extra scientific
~~~

Run checks:

~~~bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
~~~

For API work:

~~~bash
uv sync --group dev --extra api --extra scientific
~~~

For broad compatibility testing:

~~~bash
uv sync --group test --all-extras
uv run pytest
~~~

pyproject.toml is the authoritative dependency configuration.

## 2. Canonical kernel

Primary files:

- src/canonical_kernel.py
- tests/test_canonical_kernel.py
- docs/canonical_spec_v0.4.md

Focused verification:

~~~bash
uv run pytest -q tests/test_canonical_kernel.py tests/test_property_invariants.py
~~~

## 2A. Minimal local transition law

Use:

- \`src/matrix_local_transition.py\`
- \`docs/matrix_local_transition_v0.1.md\`

Focused verification:

~~~bash
uv run pytest -q tests/test_matrix_local_transition.py
~~~

The transition model is dimensionless. Its \`lattice_wave_speed\` is measured in
lattice sites per model-time unit and must not be presented as a measured
physical speed without an independently justified unit map.

## 3. Open field engine

Primary experimental open-field path:

- src/open_gauge_dynamics.py
- src/open_boundary_solver.py
- src/open_polarity_sources.py
- src/unified_engine.py

Focused verification:

~~~bash
uv run pytest -q \
  tests/test_open_boundary_solver.py \
  tests/test_open_solver_manufactured.py \
  tests/test_open_gauge_dynamics.py \
  tests/test_open_polarity_sources.py \
  tests/test_unified_engine.py
~~~

## 4. Gauge and chiral research

Current areas include U(1), SU(2), and SU(3) lattice gauge systems, Wilson-Dirac and overlap-Dirac operators, Ginsparg-Wilson chirality, Weyl measure curvature and holonomy, product-group overlap operators, and anomaly ledgers.

Use each subsystem note together with its matching implementation and tests.

Do not interpret numerical consistency as experimental confirmation.

## 5. Research API

Use the secured API in src/api_server.py.

Configure API credentials:

~~~bash
export UNIVERSAL_MATRIX_API_KEYS="replace-with-secret:RESEARCH"
~~~

Optional CORS origins:

~~~bash
export UNIVERSAL_MATRIX_CORS_ORIGINS="https://example.org"
~~~

Start locally:

~~~bash
uv run uvicorn src.api_server:app --host 127.0.0.1 --port 8000
~~~

Authenticated requests use:

~~~text
X-API-Key: replace-with-secret
~~~

Current secured endpoints include:

~~~text
GET  /health
GET  /metrics
POST /api/v1/matrix/evaluate
POST /api/v1/gcode/compile
POST /api/v1/spatial/validate-command
POST /api/v1/commercial/entitlements/evaluate
GET  /api/v1/audit/ledger
~~~

Do not use wildcard credentialed CORS.

## 6. Legacy compatibility API

src/api.py is a broad historical/experimental surface.

It should not be exposed publicly by default.

If it is used, review authentication, authorization, route-specific dependencies, hardware behavior, and customer-specific risk before deployment.

## 7. Spatial command validation

Use:

- src/spatial_protocol.py
- src/spatial_operations_control.py

The spatial control plane checks command freshness, sequence/replay safety, deadman state, workspace bounds, motion bounds, and emergency-stop request propagation.

It does not perform physical hardware I/O.

Focused tests:

~~~bash
uv run pytest -q \
  tests/test_spatial_operations_control.py \
  tests/test_spatial_protocol.py
~~~

## 8. Robot adapter integration

Use:

- src/robot_adapter.py
- src/xr_robot_bridge.py

The common adapter contract provides capabilities, state, command submission, stop handling, and acknowledgement.

The XR bridge validates a spatial command before submitting a bounded robot command.

Focused test:

~~~bash
uv run pytest -q tests/test_robotics_xr_product.py
~~~

## 9. Digital twins

Use:

- src/digital_twin_contract.py
- src/digital_twin_store.py

The contract distinguishes measured values from derived values.

Production integrations should preserve units, source identity, timestamp, quality, calibration metadata, and uncertainty.

The current store is an in-process reference implementation, not a production database.

## 10. Manufacturing and G-code

The secured API exposes G-code compilation.

Additional compatibility modules provide path generation, visualization, CNC/GRBL adaptation, winding research, optimization, and digital-twin utilities.

Before physical execution:

1. verify units;
2. verify coordinate frames;
3. verify machine limits;
4. run simulation or dry-run;
5. use independent physical safety systems;
6. inspect generated code for the target controller.

## 11. Hardware safety

Do not connect experimental software outputs directly to hazardous physical hardware without independent safety engineering.

Real hardware mode requires both:

~~~bash
export UNIVERSAL_MATRIX_SYSTEM_MODE=REAL
export UNIVERSAL_MATRIX_ALLOW_HARDWARE=1
~~~

Relevant hardware can include CNC and motion systems, robotics, CAN buses, high-voltage systems, RF transmitters, lasers, battery or grid-power systems, and laboratory instruments.

A passing unit test is not a hardware safety certification.

A software stop request is not equivalent to physical power removal.

## 12. Scientific experiments

Current validation rules are documented in docs/physics_proofs/falsifiable_predictions.md.

A physical benchmark should specify:

1. observable;
2. units;
3. initial conditions;
4. boundary conditions;
5. independently fixed parameters;
6. numerical convergence/error;
7. uncertainty;
8. predeclared falsification criterion.

Calibration to a target result must be labeled as calibration.

## 13. Theory comparisons

Use docs/comparative_theory_bridge_audit_v0.1.md for comparisons with string theory, M-theory, loop quantum gravity, causal sets, holographic/tensor-network ideas, lattice gauge theory, and related frameworks.

Comparison does not imply equivalence.

## 14. Omniverse design questions

Use docs/omniverse_design_questions_v0.1.md as the current gap ledger for the creator-style design exercise.

The creator framing is a systems-design metaphor used to ask what laws must exist for a complete universe model. It is not treated as evidence that the model is physically correct.

The current recursive geometry and circulation boundaries are documented in
docs/universe_port_engine_v0.1.md and
docs/vesica_tree_circulation_v0.1.md. Plane overlap and possibility branching
are documented separately in docs/transitive_plane_branching_v0.1.md. The
embedding-independent Sri Yantra fibre, its plane/spherical/Meru realization
family, and the explicitly candidate simplex and spiral-cone lifts are in
docs/sri_yantra_multidimensional_v0.1.md. A rendering is only a view of the
abstract state; it does not change recursive universe, named plane, or
possibility coordinates. The circulation state is dimensionless; do not
relabel it as measured energy, charge, Ether, Consciousness, or matter without
a separately tested adapter.

## 15. Licensing

The public repository is source-available for permitted noncommercial use under the PolyForm Noncommercial License 1.0.0.

Commercial use outside the public license requires a separate written Waters Legacy Trust commercial license unless applicable law independently permits the use.

Read:

- LICENSE
- NOTICE
- docs/LICENSING_GUIDE.md
- COMMERCIAL_LICENSE.md
- COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md

Commercial licensing contact:

waterslegacytrust@gmail.com

## 16. Contributions

External contributions require acceptance of CLA.md unless expressly waived in writing by Waters Legacy Trust.

Read:

- CLA.md
- CONTRIBUTING.md

Do not submit third-party material you do not have authority to contribute.

## 17. Repository status

Before extending a legacy module, consult:

- docs/DOCUMENTATION_STATUS.md
- docs/CURRENT_REPOSITORY_MANIFEST.md
- docs/repository_audit_2026-09.md
- ARCHITECTURE.md

Historical modules can retain old terminology and assumptions for provenance. They do not override current canonical definitions.


## 18. Compute the Huet Sri Yantra chambers

```bash
python -m src.sri_yantra_chambers
python -m scripts.render_sri_yantra_chambers
python -m pytest -q tests/test_sri_yantra_chambers.py
```

The report derives 43 selected triangles from 74 bounded regions and checks
the contact circuits. The renderer writes `docs/assets/sri_yantra_chambers.svg`
from computed geometry. See `docs/sri_yantra_chambers_v0.1.md` for the
numerical scope and the remaining spherical/Meru mapping question.

## Compute the Rao great-circle reference

With the scientific extra installed:

```sh
python -m src.sri_yantra_rao_great_circles
python -m pytest -q tests/test_sri_yantra_rao_spherical_reference.py tests/test_sri_yantra_rao_great_circles.py
```

The report gives constraint closure, the literal/corrected point-16 residuals,
chamber circuits, and the full Huet vertex correspondence. See
`docs/sri_yantra_rao_great_circles_v0.1.md` for the source audit.

## Compare Meru candidate edge rules

```sh
python -m src.sri_yantra_meru_candidate
python -m pytest -q tests/test_sri_yantra_meru_candidate.py
```

The report distinguishes the incidence-preserving surface lift from the
straight-root-chord substitution and reports the latter's height separations.
See `docs/sri_yantra_meru_candidate_v0.1.md` for the chosen metric.

## Compute the conservative toroidal current

```sh
python -m src.conservative_toroidal_field
python -m pytest -q tests/test_conservative_toroidal_field.py
```

The API accepts signed poloidal and toroidal cut fluxes. The CLI reports
analytic flux normalization; the tests independently integrate the cuts.
See `docs/conservative_toroidal_field_v0.1.md` for domain and mirror rules.


## Map conservative graph currents into toroidal volumes

```sh
python -m pytest -q tests/test_graph_toroidal_flux_bundle.py
```

`map_graph_currents_to_tori(...)` assigns one disjoint translated toroidal
domain to each `DirectedCurrent`. The mapped inner-cut flux equals the signed
graph current, and the original source/target incidence remains available for
node-balance checks. See `docs/graph_toroidal_flux_bundle_v0.1.md` for the
kinematic scope and the remaining junction problem.


## Build connected conservative junction control volumes

```sh
python -m pytest -q tests/test_toroidal_junction_control_volume.py
```

Build a `GraphToroidalFluxBundle` first, then pass it with the complete node
set to `connect_toroidal_bundle_with_junctions(...)`. The result contains one
connected 3D control volume per graph node and verifies flux agreement across
source junctions, toroidal channels, and target junctions.

See `docs/toroidal_junction_control_volume_v0.1.md` for the port convention,
lane construction, and remaining connector problem.


## Audit and evaluate annular toroidal connectors

```sh
python -m pytest -q tests/test_toroidal_connector_topology.py
```

Use `CutOpenToroidalChannel` to expose the two annular boundary copies of a
purely poloidal toroidal edge, then construct `AnnularPiolaConnector` from a
compatible annular source port. The implementation rejects the existing
disk-like rectangular port as a nonsingular annulus connector.

See `docs/toroidal_connector_topology_v0.1.md` for the topology audit, Piola
map, and current limitations.


## Build connector-compatible annular junctions

```sh
python -m pytest -q tests/test_toroidal_annular_junction.py
```

Use `connect_bundle_to_annular_junctions(...)` with a
`GraphToroidalFluxBundle` and complete graph node set. Each incident edge
receives one annular boundary band whose signed surface flux equals the graph
contribution and whose profile matches the annular Piola connector.

See `docs/toroidal_annular_junction_v0.1.md` for the cumulative-flux and
streamfunction construction.


## Build local framed toroidal edge assemblies

```sh
python -m pytest -q tests/test_toroidal_framed_edge_assembly.py
```

After building an annular junction network, call
`build_framed_edge_network(...)`. The result creates one local five-part
assembly per graph edge and checks signed flux cancellation, internal vector
continuity, and endpoint vector agreement for positive, negative, and zero
currents.

See `docs/toroidal_framed_edge_assembly_v0.1.md` for the local frame rule and
remaining global-routing gate.


## Build the global collision-audited toroidal routing

```sh
python -m pytest -q tests/test_toroidal_global_routing.py
```

Build the annular junction network and framed edge network first, then call
`build_global_toroidal_routing(...)`. The result rigidly places all
junctions, assigns one deterministic routed centerline to every graph edge,
preserves the +z endpoint frames, and audits nonincident edge and junction
clearance.

See `docs/toroidal_global_routing_v0.1.md` for the routing construction and
the remaining smooth-bend field gate.


## Smooth the global toroidal routing

```sh
python -m pytest -q tests/test_toroidal_smooth_bends.py
```

Call `build_smooth_global_toroidal_routing(...)` on a framed edge network.
The builder regenerates the global routing with bend-aware clearance, inserts
one positive-Jacobian annular quarter bend at every internal corner, and
verifies straight-to-bend vector matching, positive Jacobian margin, trimmed
straight length, and global collision certification.

See `docs/toroidal_smooth_bends_v0.1.md` for the Piola derivation and the
remaining incident-overlap gate before unified field sampling.


## Audit same-face incident connector overlap

```sh
python -m pytest -q tests/test_toroidal_incident_overlap_audit.py
```

Run `audit_incident_connector_overlap(...)` on a framed edge network to list
every nonzero same-face connector pair that converges onto the common channel
annulus. The report includes affected nodes, the first normalized overlap
progress, and terminal overlap width.

See `docs/toroidal_incident_overlap_audit_v0.1.md` for the no-fit result and
the separated-channel/fan-out correction gate.


## Build separated toroidal channel shells

```sh
python -m pytest -q tests/test_toroidal_separated_channels.py
```

Use `build_separated_framed_edge_network(...)` to allocate one ordered
annular channel shell per graph edge, build the edge-specific toroidal bundle,
attach the existing annular junctions, and reuse the framed-edge assembly
logic. The helper reports terminal shell gaps and the same-face connector audit
returns zero overlap pairs.

See `docs/toroidal_separated_channels_v0.1.md` for the order-preservation
argument and the remaining incident-bend collision gate.


## Audit incident smooth-bend collisions

```sh
python -m pytest -q tests/test_toroidal_incident_bend_audit.py
```

Run `audit_incident_bend_collisions(...)` on a separated framed-edge network.
The audit builds the smooth global routing, samples each endpoint bend, and
tests those bend points against neighboring same-face trimmed straight shells.
It returns affected nodes, edge pairs, witness points, and penetration margins.

See `docs/toroidal_incident_bend_audit_v0.1.md` for the compact-geometry
no-fit. Run the spacing scan below before committing to a topology redesign.


## Scan toroidal bend spacing and curvature

```sh
python -m pytest -q tests/test_toroidal_bend_spacing_scan.py
```

Use `evaluate_vesica_bend_spacing(...)` for one shell-gap/bend-margin point or
`scan_vesica_bend_spacing(...)` for a deterministic Cartesian grid. The scan
keeps the graph, signed currents, annular junctions, Piola connectors, and
smooth-bend field unchanged while varying only shell separation and bend
curvature.

The current regression grid contains at least one collision-free sample, so
separate-axis fan-out is not yet forced by the tested geometry. The next task
is boundary mapping and scale-consistency, not immediate topology replacement.

See `docs/toroidal_bend_spacing_scan_v0.1.md` for the evidence boundary.
