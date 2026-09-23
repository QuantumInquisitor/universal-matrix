# Universal Matrix Documentation Status

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Documentation baseline:** White Paper v0.6 / Software v0.4.0  
**Updated:** September 2026

This file defines the documentation hierarchy for the current repository.

## Authority order

When files disagree, use the following order:

1. executable implementation and tests for the subsystem in question;
2. `src/canonical_kernel.py` and `tests/test_canonical_kernel.py` for canonical finite mathematics;
3. `docs/canonical_spec_v0.4.md`;
4. `white_paper.md`;
5. `README.md` and `ARCHITECTURE.md`;
6. current subsystem technical notes in `docs/`;
7. historical inventories, migration audits, and legacy modules.

A historical file never overrides the current canonical specification or tested implementation.

## Current authoritative documents

| File | Role |
| --- | --- |
| `README.md` | Current repository overview, capabilities, licensing, and usage entry point. |
| `white_paper.md` | Current scientific and mathematical preprint, Version 0.6. |
| `ARCHITECTURE.md` | Current software and subsystem architecture. |
| `docs/canonical_spec_v0.4.md` | Canonical finite-kernel specification. |
| `docs/HOW_TO_USE.md` | Current installation, API, verification, and safety usage guide. |
| `docs/CURRENT_REPOSITORY_MANIFEST.md` | Current high-level repository and subsystem map. |
| `docs/physics_stack_status_2026-09.md` | Current research-stack status and open scientific work. |
| `docs/omniverse_design_questions_v0.1.md` | Open generative-design questions and gap ledger. |
| `docs/primitive_matrix_ontology_v0.1.md` | Current executable answer to ontology Questions 1-3. |
| `docs/matrix_local_transition_v0.1.md` | Current minimal local transition-law candidate and creator-question checkpoint. |
| `docs/matrix_polarity_phase_reduction_v0.1.md` | Exact algebraic bridge between canonical branch, phase representation, and fixed-amplitude matter. |
| `docs/universe_port_engine_v0.1.md` | Current exact contained Seed, Vesica, Flower, and derived Tree geometry with explicit candidate port dynamics. |
| `docs/vesica_tree_circulation_v0.1.md` | Current discrete continuity law for balanced Vesica, Tree, and recursive-scale currents. |
| `docs/transitive_plane_branching_v0.1.md` | Current product-address, overlap-route, mirror, and conservative possibility-branch contract. |
| `docs/sri_yantra_multidimensional_v0.1.md` | Current embedding-independent Sri Yantra inventory, realization family, simplex lift, spiral-cone chart, and enclosure-flow contract. |
| `docs/sri_yantra_incidence_topology_audit_v0.1.md` | Current incidence audit separating exact abstract topology, the numerical Huet chamber graph, and open spherical/Meru equivalence. |
| `docs/sri_yantra_chiodo_concurrency_v0.1.md` | Current sourced Chiodo 2021 planar concurrency contract for all nine maximal Sri Yantra triangles. |
| `docs/sri_yantra_huet_planar_v0.1.md` | Current Huet-reference planar coordinate reconstruction satisfying the sourced Chiodo concurrency constraints. |
| `docs/sri_yantra_huet_chambers_v0.1.md` | Current geometry-derived 43-chamber Huet incidence complex with 1 + 8 + 10 + 10 + 14 rings and 129 distinct chamber edges. |

| `docs/sri_yantra_chambers_v0.1.md` | Numerically verified Huet planar chamber extraction, odd-coverage selection, contact circuits, and computed diagram. |

| `docs/sri_yantra_spherical_topology_control_v0.1.md` | Current homeomorphic spherical control carrying the complete derived 43-chamber incidence complex without topology change; explicitly distinct from Rao's great-circle construction. |
| `docs/higher_dimensional_e8_bridge_v0.1.md` | Current exact arbitrary-dimensional regular-family audit and exploratory E8/D4 construction bridge. |
| `docs/h4_direct_e8_lift_v0.1.md` | Current direct H4/600-cell to E8 lift using the reduced Q(phi) inner product and eight rational coefficient coordinates. |
| `docs/e8_equivalence_map_v0.1.md` | Current exact scale-orthogonal equivalence between the H4-derived and standard E8 root systems. |
| `docs/e8_state_representation_audit_v0.1.md` | Current no-fit audit separating E8 Weyl/Cartan coordinates from existing Matrix and SU(3) state variables. |
| `docs/e8_invariant_coupling_v0.1.md` | Current minimal Weyl-invariant scalar coupling that preserves existing U(1), SU(2), and SU(3) gauge transformation laws. |
| `docs/e8_coupling_observable_audit_v0.1.md` | Current audit showing fixed-root scalar E8 couplings reduce to parameter renormalization or source shifts rather than distinct E8 dynamics. |
| `docs/e8_radial_degree_audit_v0.1.md` | Current no-duplication audit showing no existing amplitude/content/scale variable can serve as an independent E8 radial degree. |
| `docs/qball_stability_map_v0.1.md` | Current charged-matter evidence-map design separating energetic, branch-slope, and finite-time persistence diagnostics. |
| `docs/qball_threshold_refinement_v0.1.md` | Current adaptive refinement of the charged-matter energetic threshold. |
| `docs/qball_threshold_persistence_scan_v0.1.md` | Current finite-time direct and perturbed 3D scan across the refined energetic threshold. |
| `docs/qball_mapping_convergence_v0.1.md` | Current radial-to-Cartesian energetic mapping convergence audit near the charged-matter threshold. |
| `docs/qball_mapping_error_decomposition_v0.1.md` | Current separation of spacing-resolution and finite-volume mapping errors near the charged-matter threshold. |
| `docs/qball_joint_mapping_extrapolation_v0.1.md` | Current joint spacing and finite-volume extrapolation using the localized branch tail scale. |
| `docs/qball_threshold_preserving_grid_v0.1.md` | Current finite-grid confirmation of radial energetic threshold-side preservation. |
| `docs/qball_highres_persistence_stage1_v0.1.md` | Current short-duration direct and perturbed persistence test on the 91^3 threshold-preserving grid. |
| `docs/qball_highres_persistence_stage2_v0.1.md` | Current four-times-longer persistence scaling test on the same 91^3 threshold-preserving grid. |
| `docs/qball_highres_persistence_stage3_v0.1.md` | Current 250-step duration-scaling test on the same 91^3 threshold-preserving grid. |
| `docs/qball_highres_time_scaling_v0.1.md` | Current diagnostic of conservation and structural time scaling across the first three high-resolution persistence stages. |
| `docs/qball_highres_persistence_stage4_v0.1.md` | Current 500-step persistence test selected by the prior high-resolution time-scaling diagnostic. |
| `docs/qball_highres_timeseries_v0.1.md` | Current in-run sampled diagnostic for monotonic, turning, or oscillatory response on the 91^3 high-resolution persistence grid. |
| `docs/qball_highres_timeseries_t1_v0.1.md` | Current sampled extension through t=1.0 with extrema-time diagnostics. |
| `docs/qball_highres_timeseries_t1p5_v0.1.md` | Current sampled extension through t=1.5 with explicit turning-time and half-cycle diagnostics. |
| `docs/qball_highres_timeseries_t2_v0.1.md` | Current sampled extension through t=2.0 with perturbed-peak half-cycle candidate diagnostics. |

## Licensing and governance authority

| File | Role |
| --- | --- |
| `LICENSE` | PolyForm Noncommercial License 1.0.0 plus project-required notice. |
| `NOTICE` | Project licensing and copyright notice. |
| `COMMERCIAL_LICENSE.md` | Commercial licensing framework. |
| `COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md` | Negotiated proprietary license template. |
| `CLA.md` | Contributor License Agreement. |
| `CONTRIBUTING.md` | Contribution rules. |
| `docs/LICENSING_GUIDE.md` | Plain-language licensing guide. |

## Commercial and engineering product documents

| File | Role |
| --- | --- |
| `docs/COMMERCIAL_PRODUCT_SURFACES.md` | Product families and buildout roadmap. |
| `docs/ROBOTICS_XR_PRODUCT_ARCHITECTURE.md` | Current spatial/robotics/XR/digital-twin product architecture. |

## Current subsystem technical notes

Versioned files such as

`docs/*_v0.1.md`

are subsystem research notes. They remain current only for the subsystem and version they describe. They do not redefine the canonical kernel or imply experimental confirmation.

Examples include:

- gauge and matter notes;
- reciprocity geometry derivations;
- Dirac and overlap-fermion notes;
- Weyl measure and anomaly diagnostics;
- source and boundary solver notes;
- nested-scale and polarity notes.

## Historical or provenance documents

The following are retained to preserve development history and should not be treated as current scientific authority:

- `docs/FEATURE_HISTORY.md`;
- `docs/REPOSITORY_MANIFEST.md`;
- `docs/repository_audit_2026-09.md` where it describes the repository at the time of that audit;
- any archived historical presentation material explicitly marked superseded.

Historical terminology can include:

- Z_114 or a 114-state cyclic routing group;
- SO(13) as physical spacetime;
- "64-bit spacetime";
- fixed 3/6/9 physical laws;
- unverified physical-constant derivations;
- legacy toroidal, biological, chakra, meridian, or consciousness mappings;
- older API or hardware claims.

Such terminology is preserved only where needed for provenance or compatibility.

## Naming conventions

Use:

- **108-state core plus six external boundary orientations** for the canonical architecture;
- **114 labeled positions** only when referring to the total count of core plus external boundary labels;
- **64-address projection** or **six-bit boundary-state model** rather than "64-bit spacetime";
- **source-available noncommercial** for the public licensing model;
- **PolyForm Noncommercial License 1.0.0** for the public license;
- **Waters Legacy Trust commercial license** for commercial use.

Do not call the current public license OSI open source.

## Scientific claim conventions

Use these labels consistently:

- **Exact finite result**
- **Model-derived result**
- **Numerically verified result**
- **Physical hypothesis**
- **Experimental engineering interface**
- **Legacy / compatibility**

Do not turn calibration into derivation, numerical consistency into experimental validation, or a compatibility module into canonical authority.

## Current product flow

The present spatial/robotics stack is:

```text
XR / desktop operator
        ↓
versioned spatial protocol
        ↓
spatial command validation
        ↓
common robot adapter
        ↓
ROS2 / CAN / CNC / OEM adapter
        ↓
acknowledgement + robot state
        ↓
typed digital twin
        ↓
telemetry / history / audit
```

Real hardware remains fail-closed and requires independent physical safety systems.

## Maintenance rule

Whenever a major subsystem is merged:

1. update `README.md`;
2. update `ARCHITECTURE.md`;
3. update `white_paper.md` if the scientific state changed;
4. update `docs/HOW_TO_USE.md` if the user workflow changed;
5. update this file if authority or document status changed;
6. update the relevant subsystem technical note;
7. add tests that prevent stale licensing or authority claims from reappearing.

## Rao geometric checkpoint

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

| `docs/graph_toroidal_flux_bundle_v0.1.md` | Current one-to-one mapping from conservative graph currents to disjoint 3D toroidal flux domains with exact signed cut-flux preservation. |

| `docs/toroidal_junction_control_volume_v0.1.md` | Current connected conservative graph-node control volumes with explicit 3D boundary-port flux routing and toroidal edge-interface checks. |

| `docs/toroidal_connector_topology_v0.1.md` | Current topology audit for junction/toroidal interfaces and divergence-free annular Piola connector to the cut-open purely poloidal torus. |
