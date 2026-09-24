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
- `src/canonical_mod9_interface_audit.py`
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
- `src/sri_yantra_incidence_topology_audit.py`
- `src/sri_yantra_chiodo_concurrency.py`
- `src/sri_yantra_huet_planar.py`
- `src/sri_yantra_huet_chambers.py`

- `src/sri_yantra_chambers.py`

- `src/sri_yantra_spherical_topology_control.py`
- `src/higher_dimensional_geometry.py`
- `src/h4_direct_e8_lift.py`
- `src/e8_equivalence_map.py`
- `src/e8_state_audit.py`
- `src/e8_invariant_coupling.py`
- `src/e8_coupling_observable_audit.py`
- `src/e8_radial_degree_audit.py`

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


## Direct H4 to E8 lift

The geometry manifest now includes `src/h4_direct_e8_lift.py`, which derives a
240-root E8 system directly from the existing H4 / 600-cell coordinates by
forming H4 union phi*H4 and applying the reduced rational-coefficient inner
product. Its coefficient expansion spans eight exact rational dimensions.


## E8 equivalence map

The geometry manifest now includes `src/e8_equivalence_map.py`, which derives
an exact rational change of basis between the H4-derived E8 root system and the
standard integer-scaled E8 construction. The map is scale-orthogonal, maps all
240 roots bijectively, and intertwines mirror and root reflections.


## E8 state-space boundary

The geometry manifest now includes `src/e8_state_audit.py`. It records that
the canonical core, the 8 x 8 stella register, and the eight-component SU(3)
electric field are not established E8 representations. A separate
`E8CartanState` carries only the exact rank-eight Weyl reflection action.


## E8 invariant scalar coupling

The geometry/state manifest now includes `src/e8_invariant_coupling.py`, which
couples only the Weyl-invariant Cartan norm to an already gauge-invariant scalar.
The E8 coordinate remains a singlet under the existing U(1), SU(2), and SU(3)
gauge transformations.


## E8 coupling observable boundary

The state/dynamics manifest now includes
`src/e8_coupling_observable_audit.py`. It records that fixed-root E8 scalar
couplings to current matter norms, gauge energy, or the neutral scalar do not
produce distinct E8 orientation dynamics. They reduce to parameter shifts,
coupling rescalings, or source offsets unless a new E8-covariant or radial
degree of freedom is introduced.


## E8 radial-degree boundary

The state/dynamics manifest now includes `src/e8_radial_degree_audit.py`.
It records that the existing matter amplitude, port circulation amplitude,
nested oscillatory amplitude, neutral content scalar, and scale coordinate are
already committed to other roles and are not reused as an E8 radius. A distinct
E8 radial mode would be a new degree of freedom and is not introduced.


## Sri Yantra topology boundary

The geometry manifest now includes
`src/sri_yantra_incidence_topology_audit.py`. It tests the abstract topology
that is declared by the current Sri Yantra contract, and records the new
numerical Huet planar chamber graph separately from open historical
spherical/Meru incidence equivalence. The
current spherical and spiral-cone candidate charts preserve all declared
locations without collisions.


## Sri Yantra sourced concurrency graph

The geometry manifest now includes `src/sri_yantra_chiodo_concurrency.py`,
which encodes Chiodo's proved planar concurrency conditions for t1 through t9.
This gives a sourced relation graph across all nine maximal triangles without
conflating it with the separately computed planar chamber graph.


## Sri Yantra Huet planar reconstruction

The geometry manifest now includes `src/sri_yantra_huet_planar.py`, which
reconstructs all nine maximal triangles for the Huet reference parameters from
the sourced Chiodo concurrency equations. It provides the 27 planar edge
segments used by the two chamber extractors.


## Derived Sri Yantra chamber complex

The geometry manifest now includes `src/sri_yantra_huet_chambers.py`.

Starting from the 27 finite Huet parent edges, it derives the complete planar
intersection arrangement, enumerates all supported triangular circuits, and
selects the unique globally admissible chamber system satisfying the sourced
central plus 8, 10, 10, and 14 enclosure contract.

The resulting 43 chambers are mirror closed, the four noncentral enclosures
are vertex-touching cycles, and their 129 chamber sides are all distinct.
The result is a planar incidence contract. Nonplanar Sri Yantra candidates have
not yet been shown to preserve it.


## Sri Yantra chamber extraction

`src/sri_yantra_chambers.py` derives 43 odd-coverage triangular chambers
from the finite Huet edges, and verifies their 14 + 10 + 10 + 8 + 1 contact
circuits. It exposes the full 69-vertex, 142-edge, 74-bounded-face arrangement.
`docs/sri_yantra_chambers_v0.1.md` records the numerical scope and tests.
`python -m scripts.render_sri_yantra_chambers` regenerates the computed SVG.

## Sri Yantra spherical topology control

The geometry manifest includes `src/sri_yantra_spherical_topology_control.py`.
It maps the actual 43-chamber Huet incidence complex through an injective
inverse-stereographic chart, retains complete chamber and ring membership, and
verifies mirror equivariance and planar roundtrip recovery.

The construction is intentionally a topology-preserving control. It is not
identified with Rao's sourced great-circle spherical geometry.

## Rao reference and great-circle geometry

The audited Rao reference construction now supplies nine unit-sphere root
triangles with great-circle edges. After refinement within the published
rounding intervals and two explicitly documented formula fixes, its 69
vertices, 142 atomic edges, 74 bounded faces, and 43 selected chambers match
the Huet complex through a complete generator-edge-labelled correspondence.
This numerical result applies to one reference row; broader spherical families
and independently specified Meru geometry remain open.

Implementation: `src/sri_yantra_rao_spherical_reference.py` and
`src/sri_yantra_rao_great_circles.py`. Verification: the corresponding
`tests/test_sri_yantra_rao_*.py` modules.
See `docs/sri_yantra_rao_great_circles_v0.1.md` for the formula audit and
`docs/MATRIX_ENGINE_WORK_QUEUE.md` for remaining gates.

## Explicit Meru candidate control

`src/sri_yantra_meru_candidate.py` now provides a conical graph-surface
control with explicit vertices, complete edge paths, and an invertible
horizontal projection. It preserves the computed 43-chamber incidence for
positive horizontal scale. A separate audit detects 53 failed projected
concurrencies if the default raised root corners are instead joined by straight
spatial chords. This is an explicitly chosen candidate metric, not a sourced
historical Meru reconstruction.

Technical note: `docs/sri_yantra_meru_candidate_v0.1.md`.
Verification: `tests/test_sri_yantra_meru_candidate.py`.

## Conservative toroidal field candidate

`src/conservative_toroidal_field.py` defines a compact, divergence-free
three-dimensional content current on an explicit solid ring torus. A stream
function fixes local conservation; signed parameters equal independently
integrated poloidal and toroidal cut fluxes. Cartesian tests distinguish
central mirroring, axial-plane mirroring, and flow reversal. This is a
prescribed dimensionless kinematic candidate with no derived force law or
physical content identification.

Technical note: `docs/conservative_toroidal_field_v0.1.md`.
Verification: `tests/test_conservative_toroidal_field.py`.

- `src/graph_toroidal_flux_bundle.py`
- `src/toroidal_junction_control_volume.py`
- `src/toroidal_connector_topology.py`
- `src/toroidal_annular_junction.py`
- `src/toroidal_framed_edge_assembly.py`
- `src/toroidal_global_routing.py`
- `src/toroidal_smooth_bends.py`
- `src/toroidal_incident_overlap_audit.py`
- `src/toroidal_separated_channels.py`
- `src/toroidal_incident_bend_audit.py`


## Graph-to-toroidal flux bundle

`src/graph_toroidal_flux_bundle.py` maps every conservative directed graph
edge to one disjoint translated solid-ring-torus domain. Each edge current is
the mapped torus poloidal cut flux, so the signed channel flux and graph node
divergence are preserved exactly. The construction remains a kinematic volume
assignment; connected three-dimensional node junctions and dynamics are not
yet claimed.

Primary verification: `tests/test_graph_toroidal_flux_bundle.py`.
Primary note: `docs/graph_toroidal_flux_bundle_v0.1.md`.


## Connected toroidal junction control volumes

`src/toroidal_junction_control_volume.py` constructs one connected rectangular
control volume for each conservative graph node. Incident edge currents are
represented as signed boundary-port fluxes and routed through nonoverlapping
divergence-free internal lanes. The network checks flux continuity between
source junction ports, toroidal channel cuts, and target junction ports.

Primary verification: `tests/test_toroidal_junction_control_volume.py`.
Primary note: `docs/toroidal_junction_control_volume_v0.1.md`.


## Toroidal connector topology and Piola field

`src/toroidal_connector_topology.py` records the disk-to-annulus interface
no-fit, exposes the two annular boundary copies of a cut-open toroidal channel,
and constructs a compatible annulus-to-annulus connector through an explicit
Piola map. The connector preserves signed flux, has positive Jacobian, and
matches the purely poloidal toroidal field on the target cut.

Primary verification: `tests/test_toroidal_connector_topology.py`.
Primary note: `docs/toroidal_connector_topology_v0.1.md`.


## Annular junction edge ports

`src/toroidal_annular_junction.py` assigns one annular boundary band to every
incident graph edge and uses lower/upper cumulative streamfunctions to build a
divergence-free axisymmetric junction current. Flux-coordinate interval
overlaps preserve the deterministic conservative transport decomposition. Each
port's normal-density profile matches the annular Piola connector source
profile exactly.

Primary verification: `tests/test_toroidal_annular_junction.py`.
Primary note: `docs/toroidal_annular_junction_v0.1.md`.


## Framed toroidal edge assemblies

`src/toroidal_framed_edge_assembly.py` composes source annular junction ports,
general Piola transitions, a straightened cut-open toroidal chart, and target
annular junction ports into one local edge path. It verifies pointwise vector
continuity, signed interface-flux cancellation, and endpoint agreement under a
one-bit current-sign frame rule.

Primary verification: `tests/test_toroidal_framed_edge_assembly.py`.
Primary note: `docs/toroidal_framed_edge_assembly_v0.1.md`.


## Global collision-audited toroidal routing

`src/toroidal_global_routing.py` rigidly places annular junctions and assigns
each framed graph edge a deterministic orthogonal global route with unique y and
z lanes. Conservative route envelopes are checked against all nonincident edge
routes and nonincident junctions.

The checkpoint proves a collision-free routing envelope for the tested finite
networks. It does not yet construct smooth current-preserving bend fields at
the orthogonal corners.

Primary verification: `tests/test_toroidal_global_routing.py`.
Primary note: `docs/toroidal_global_routing_v0.1.md`.


## Smooth positive-Jacobian toroidal bends

`src/toroidal_smooth_bends.py` replaces every orthogonal internal route corner
with an annular quarter bend whose bend radius exceeds the annular outer
radius. The Piola-transported current preserves the connector-compatible flux
profile and matches the adjacent straight fields.

Primary verification: `tests/test_toroidal_smooth_bends.py`.
Primary note: `docs/toroidal_smooth_bends_v0.1.md`.


## Same-face incident connector overlap audit

`src/toroidal_incident_overlap_audit.py` measures annular interval overlap for
nonzero graph edges sharing one junction face. It confirms that the present
common-channel transition loses disjointness before the channel endpoint even
though each connector separately preserves flux.

Primary verification: `tests/test_toroidal_incident_overlap_audit.py`.
Primary note: `docs/toroidal_incident_overlap_audit_v0.1.md`.


## Edge-specific separated toroidal channel shells

`src/toroidal_separated_channels.py` allocates pairwise-disjoint annular
channel shells in edge-index order, constructs edge-specific toroidal fields,
and reuses the annular junction and framed-edge builders. The same-face
connector overlap audit returns zero nonzero pairs for the corrected Vesica and
Flower/Tree connector networks.

Primary verification: `tests/test_toroidal_separated_channels.py`.
Primary note: `docs/toroidal_separated_channels_v0.1.md`.


## Incident smooth-bend collision audit

`src/toroidal_incident_bend_audit.py` samples actual endpoint annular bend
volumes against neighboring same-face trimmed straight shells. It demonstrates
that edge-specific separated channel shells remove connector interpolation
overlap but do not prevent later incident bend/straight collisions.

Primary verification: `tests/test_toroidal_incident_bend_audit.py`.
Primary note: `docs/toroidal_incident_bend_audit_v0.1.md`.


## Toroidal incident-bend spacing scan

`src/toroidal_bend_spacing_scan.py` varies edge-shell radial gap and positive
bend-radius margin while preserving the existing graph, signed currents,
annular junctions, Piola connectors, and smooth-bend maps. The deterministic
25-point Vesica grid includes colliding controls and at least one
collision-free sample.

This converts the earlier compact bend/straight no-fit from an apparent
topology gate into a parameter-boundary problem. Scale-consistent clearance
and an optimal or conservative spacing law remain open.

Primary verification: `tests/test_toroidal_bend_spacing_scan.py`.
Primary note: `docs/toroidal_bend_spacing_scan_v0.1.md`.


## Toroidal sampled bend-clearance frontier

`src/toroidal_bend_clearance_boundary.py` groups the finite bend-spacing
samples by bend margin and records the first collision-free sampled shell gap,
the nearest lower colliding sample when available, and margins that remain
unresolved on the tested grid.

The result is a sampled parameter frontier only. It does not establish a
continuous monotone boundary, an optimal compactness law, scale invariance, or
a physical length scale.

Primary verification: `tests/test_toroidal_bend_clearance_boundary.py`.
Primary note: `docs/toroidal_bend_clearance_boundary_v0.1.md`.


## Toroidal bend-clearance refinement

`src/toroidal_bend_clearance_refinement.py` subdivides each resolved sampled
collision/free bracket from the coarse frontier, reuses the coarse endpoint
classifications, evaluates only the interior gaps, and reports a narrower
sampled bracket together with transition-count and re-entrant-collision
diagnostics.

The refinement does not assume that clearance is monotone in shell gap and
does not promote the finite samples to a continuous boundary or physical scale
law.

Primary verification: `tests/test_toroidal_bend_clearance_refinement.py`.
Primary note: `docs/toroidal_bend_clearance_refinement_v0.1.md`.


## Toroidal uniform-scale similarity audit

`src/toroidal_uniform_scale_similarity.py` scales the complete declared
toroidal routing length set by one positive similarity factor, including shell,
junction, connector, channel, routing-gap, and bend-margin dimensions.

The audit checks that collision classification is invariant under uniform
similarity and that any dimensional penetration scales linearly, so normalized
penetration remains constant. It is a numerical Vesica similarity test, not a
physical scale law or recursive-depth theorem.

Primary verification: `tests/test_toroidal_uniform_scale_similarity.py`.
Primary note: `docs/toroidal_uniform_scale_similarity_v0.1.md`.


## Toroidal latent-path geometry audit

`src/toroidal_latent_path_geometry_audit.py` compares the same Flower/Tree
circulation with zero-current weave pathways retained geometrically versus
omitted from the active-current support. It measures latent edge and port
counts, active-channel center displacement, active shell-radius residual, and
active annular-port width compression.

The audit is diagnostic. It does not decide whether dormant pathways should
persist, disappear, or contract continuously.

Primary verification: `tests/test_toroidal_latent_path_geometry_audit.py`.
Primary note: `docs/toroidal_latent_path_geometry_audit_v0.1.md`.


## Toroidal sampling reliability audit

`src/toroidal_sampling_reliability.py` holds geometry fixed and compares three
sampling densities with original and half-step-shifted grids. It reproduces
the coarse grid's missed gap-3 collision and reports every grid's provenance.
No-detection results are explicitly finite-sampling observations, not
continuous-clearance certificates or a convergence proof.

Primary verification: `tests/test_toroidal_sampling_reliability.py`.
Primary note: `docs/toroidal_sampling_reliability_v0.1.md`.


## Toroidal inside-out inversion control

`src/toroidal_inversion_control.py` defines spherical inversion, explicit
orientation-aware Piola/area transport, and a control that preserves known
collision witnesses while excluding the pole from their volume pairs. It also
identifies the singularity of a straight interpolation to the inverted map.
It introduces no collision repair or continuous deformation law.

Primary verification: `tests/test_toroidal_inversion_control.py`.
Primary note: `docs/toroidal_inversion_control_v0.1.md`.


## Toroidal fixed bend-interface obstruction

`src/toroidal_fixed_interface_obstruction.py` constructs strict end-face
collision witnesses independently of volume sampling. In the gap-3,
margin-0.05 reference, two internal bend interfaces penetrate a neighboring
finite straight shell by 0.2. Continuous regular bend deformations fixing
those faces and the neighboring shells cannot remove these overlaps.
The restricted witness search does not certify unwitnessed pairs or global
clearance, and it does not alter routing or current fields.

Primary verification: `tests/test_toroidal_fixed_interface_obstruction.py`.
Primary note: `docs/toroidal_fixed_interface_obstruction_v0.1.md`.


## Toroidal shared return route candidate

`src/toroidal_shared_return_route.py` moves the inner Vesica return's joins
and straight sections onto the outer return's centerline while retaining
distinct annular shells, currents, and junction frames. The endpoint has
conservative piece bounds separating the two routed return tubes from each
other and the unchanged routes. The simple interpolating family still
collides. Junction/connector integration is covered by the follow-up below.
Existing routing builders are unchanged.

Primary verification: `tests/test_toroidal_shared_return_route.py`.
Primary note: `docs/toroidal_shared_return_route_v0.1.md`.


## Connected shared return endpoint

`src/toroidal_shared_return_connectors.py` places the eight existing Piola
transitions between the Vesica junction ports and shortened shared-route
channels. Proper rotations preserve signed currents in both axial
directions. A global current evaluator selects one matching field at each
shared face. Conservative boxes and coaxial radial-order checks exclude
overlapping component interiors while allowing intended boundary contact.
This remains an opt-in static reference, not general fan-out or a safe motion.

Primary verification: `tests/test_toroidal_shared_return_connectors.py`.
Primary note: `docs/toroidal_shared_return_connectors_v0.1.md`.

Additional verification: `tests/test_toroidal_shared_return_parameters.py`
checks six bounded parameter cases and independent physical-cut fluxes;
`tests/test_toroidal_shared_return_adversarial.py` checks weak-current
interface mismatches, fractional flux leaks and unresolved shell gaps.


## Shared-prefix different-destination control

`src/toroidal_shared_prefix_fanout.py` preserves endpoint frames and local
regularity in a balanced three-node, four-edge shared-prefix experiment.
An explicit point penetrates both tubes by 0.2 where the inner branch
departs toward its distinct destination. This rejects the particular
candidate without claiming all fan-out geometries are impossible.

Primary verification: `tests/test_toroidal_shared_prefix_fanout.py`.
Primary note: `docs/toroidal_shared_prefix_fanout_v0.1.md`.

## Local junction bore passage

`src/toroidal_junction_bore_passage.py` contracts a separate annular current
through the empty center of the unchanged C junction and its two existing
port transitions, then expands it again. Analytic radial bounds certify
the finite coaxial passage; the reference central gap is 0.3. The two
transit ends remain unattached, so full fan-out and later side exit remain
uncertified.

Primary verification: `tests/test_toroidal_junction_bore_passage.py`.
Primary note: `docs/toroidal_junction_bore_passage_v0.1.md`.


## Canonical mod-9 quotient audit

`src/canonical_mod9_interface_audit.py` derives nine mod-9 fibers and twelve
interface phases from the canonical 108-state core. It records exact coordinate
actions for `E`, `P`, `F`, and `T_21`, plus the separate
multiplication-by-two automorphism of `Z_9`.

Primary verification: `tests/test_canonical_mod9_interface_audit.py`.
Primary note: `docs/canonical_mod9_interface_audit_v0.1.md`.

## Source-tracked frequency catalog

`src/frequency_source_catalog.py` validates optional historical instrument
observations in `src/reference_data/rife_scoon_catalog.json`. The selected
Scoon reports supply 24 frequency records, five ranges and 12 unresolved
settings. Exact decimal unit conversion and explicit role selection preserve
source memberships and keep carrier, modulation and spectral observations
distinct. Unknown measurement uncertainty remains unknown.

This is a source-data audit, not a biological resonance map or a piezoelectric
model. Physical time/length scales, material tensors, boundaries, drive, losses
and independently measured response remain required. No hardware output or
canonical-state change is introduced.

Primary verification: `tests/test_frequency_source_catalog.py`.
Primary note: `docs/frequency_source_audit_v0.1.md`.

## Single-mode piezoelectric reference

`src/piezoelectric_mode_reference.py` implements an optional linear modal
electromechanical model with explicit SI parameters and their source. It
provides short/open and voltage-driven harmonic responses, ordered frequency
sweeps, and midpoint time steps with external work and passive losses. The
short-circuit guard rejects inconsistent charge rather than discarding energy.
Its synthetic control verifies analytic limits and numerical conservation;
material-tensor reduction, spatial ring geometry and measured validation
remain open.

Primary verification: `tests/test_piezoelectric_mode_reference.py`.
Primary note: `docs/piezoelectric_mode_reference_v0.1.md`.

## Classified spectral references and theory controls

- `src/spectral_reference_catalog.py`: separate CAFL anecdotal entries and evaluated NIST hydrogen wavelengths, with explicit media and uncertainty.
- `src/reference_data/cafl_explicit_catalog.json`: 1,557 source entries, including 1,403 numeric lists; 11,668 occurrences, not distinct discoveries.
- `src/reference_data/nist_hydrogen_lines.json`: all 30 rows of the NIST hydrogen strong-line table, not all physical spectra.
- `src/reference_data/universal_one_numeric_leads.json` and `docs/universal_one_source_audit_v0.1.md`: historical proposals and unresolved units with book context.
- `src/physical_theory_controls.py`: declared hydrogen approximation and periodic ABC field controls; no fit of canonical geometry.
- `docs/m4_source_and_claim_audit_v0.1.md`: image claim constraints, source attribution gaps and supplied-link triage.
- `docs/spectral_reference_catalog_v0.1.md` and `docs/physical_theory_controls_v0.1.md`: evidence classes, numerical results and remaining scope.

These optional references do not normalize the Matrix clock, establish clinical efficacy or identify the pictured M4 cosmology.

The optional `src/microplane_projection_reference.py` checks normal/tangential projections and virtual work against macroscopic tensor contractions. It is a spherical projection reference, not the full nonlinear concrete M4 model, an OOFEM quadrature reproduction, or a piezoelectric material law. See `docs/microplane_projection_reference_v0.1.md`.
