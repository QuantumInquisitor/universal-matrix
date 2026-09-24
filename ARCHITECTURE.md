# Universal Matrix Architecture

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Architecture baseline:** Canonical kernel v0.4 / White Paper v0.6 / Software v0.4.0  
**Status:** Current architecture document

This file describes the current repository architecture. Historical cosmological, physical, enterprise, and hardware interpretations are not canonical unless they are explicitly implemented, documented, and tested in the present stack.

See docs/DOCUMENTATION_STATUS.md for the repository documentation hierarchy.

## 1. Canonical finite layer

The canonical state architecture is

\[
\mathcal A=\mathbb Z_{108}\sqcup B_6,
\]

with

\[
B_6=\{+X,-X,+Y,-Y,+Z,-Z\}.
\]

The six boundary orientations are external to the \(\mathbb Z_{108}\) routing core.

Primary operators are

\[
E=T_9,\qquad T=T_{21},\qquad P=T_{54},\qquad F(n)=107-n.
\]

Important exact identities include

\[
E^{12}=I,\qquad T^{36}=I,\qquad T^{18}=P,\qquad P^2=I.
\]

The synchronized routing class is

\[
\{21,57,93\}.
\]

The current canonical routing step 21 is selected by a minimal-positive-lift convention. It is not claimed as a uniqueness theorem.

The register projection is

\[
\pi(n)=7n\bmod64.
\]

Executable authority:

- src/canonical_kernel.py
- tests/test_canonical_kernel.py
- docs/canonical_spec_v0.4.md

## 2. Primitive ontology layer

The exact 108-state core address now has an ontology-adapted decomposition

\[
n=a+54p,
\]

with

\[
a\in\{0,\ldots,53\},
\qquad
p\in\{0,1\}.
\]

The canonical polarity operation preserves \(a\) and toggles \(p\).

This prevents double-counting an independent polarity label when that label means exactly the canonical \(T_{54}\) branch.

The current candidate repeated-cell state adds scale level, phase, and conjugate phase momentum explicitly as hypotheses. Gauge connections and electric fields remain edge variables.

Implementation:

- src/matrix_ontology.py
- docs/primitive_matrix_ontology_v0.1.md
- tests/test_matrix_ontology.py

The repeated-cell complex is dimensionless and does not assign a physical lattice spacing.

## 3. Boundary symmetry layer

The six orientations form the signed three-axis set

\[
\{\pm e_x,\pm e_y,\pm e_z\}.
\]

Its abstract signed-permutation symmetry has order

\[
2^3 3!=48.
\]

The six directions serve as an orientation scaffold for later spatial and gauge adapters. This is a structural construction, not by itself a proof that the finite kernel derives physical Euclidean three-space.

## 4. Nested polarity and scale layer

The experimental nested state is represented schematically by

\[
X_\ell=(n_\ell,\sigma_\ell,\phi_\ell,A_\ell).
\]

The polarity flip is

\[
Q(n,\sigma)=(n+54,-\sigma),
\]

so

\[
Q^2=I.
\]

Routing is polarity sensitive,

\[
\sigma=+1\Rightarrow T_{21},
\]

\[
\sigma=-1\Rightarrow T_{-21}.
\]

The current layer also contains experimental nested-scale orientation, conservative exchange, phase clocks, and source coupling.

Representative modules:

- src/nested_polarity_dynamics.py
- src/polarity_oscillator.py
- src/canonical_polarity_clock.py
- src/scale_transfer.py
- src/canonical_scale_transfer.py

## 4A. Minimal local Matrix transition layer

The ontology-level local transition candidate uses site phase and conjugate
momentum,

\[
(\phi_x,\Pi_x),
\]

with compact transport phase \(\theta_{xy}\) on nearest-neighbor links.

The minimal Hamiltonian is

\[
H
=
\sum_x \frac{\Pi_x^2}{2I}
+
\kappa
\sum_{\langle xy\rangle}
\left[
1-\cos\left(\phi_y-\phi_x+\theta_{xy}\right)
\right].
\]

This layer supplies:

- six-neighbor locality;
- gauge-invariant nearest-neighbor coupling;
- pairwise antisymmetric momentum exchange;
- continuous-time conservation of total phase momentum;
- a weak-field graph-Laplacian limit;
- dimensionless lattice characteristic speed
  \[
  c_{\rm lat}=\sqrt{\kappa/I}.
  \]

It does not determine physical lattice spacing or physical time units.

Implementation:

- src/matrix_local_transition.py
- tests/test_matrix_local_transition.py
- docs/matrix_local_transition_v0.1.md

The richer gauge-matter and fully coupled field modules are treated as
extensions of this minimal ontology-level skeleton rather than as replacements
for it.

## 4B. Canonical polarity–phase reduction

The exact canonical branch bit can be represented as a sign

\[
s_p=(-1)^p,
\]

or, when the local phase is independent, as a phase offset

\[
\phi_{\rm eff}=\phi+\pi p.
\]

This gives the exact identity

\[
s_xs_y\sin(\phi_y-\phi_x+\theta_{xy})
=
\sin(
\phi_{{\rm eff},y}
-
\phi_{{\rm eff},x}
+
\theta_{xy}
).
\]

The fixed-amplitude complex matter link energy also reduces exactly to the
minimal rotor interaction:

\[
\left|
e^{i\theta_{xy}}\Phi_y-\Phi_x
\right|^2
=
2R^2
\left[
1-\cos\Delta_{xy}
\right].
\]

Thus, under the current normalization, the rotor coupling is

\[
K=2R^2.
\]

The engine therefore treats canonical branch sign, branch-as-\(\pi\)-offset,
and fixed-amplitude rotor coupling as reducible representations where their
assumptions overlap.

A strict bookkeeping rule follows: if a phase variable already represents the
canonical polarity clock, do not apply the same \(T_{54}\) branch reversal
again as an independent sign factor.

Implementation:

- src/matrix_polarity_phase_bridge.py
- tests/test_matrix_polarity_phase_bridge.py
- docs/matrix_polarity_phase_reduction_v0.1.md

## 4C. Recursive universe-port geometry

The recursive spatial layer distinguishes outward Flower growth from inward
universe containment.

For a circular parent vessel of radius (R_d), the complete contained Seed
uses seven circles of radius (R_d/2). Every one of its twelve neighboring
circle pairs forms an equal-circle Vesica. The largest circle centered at a
Vesica midpoint has radius

\[
R_{d+1}=R_d/4.
\]

The child contains a new complete Seed, giving (12^d) recursive addresses at
exact depth (d). Central mirroring is exact in both address and planar
coordinates.

Outward Flower growth instead preserves circle radius. A radius-(n) hexagonal
disk has (1+3n(n+1)) circles and (9n^2+3n) Vesica adjacencies. Inner and
outer Tree routes are reverse orientations of radial Flower edges; same-ring
links form the transverse weave. The sign of the axial horizontal coordinate
provides the negative, neutral, and positive pillar classification.

The active-state adapter attaches the canonical 36-tick clock, the 108-state
routing pair, alternating scale orientation, and one explicitly selected
Terryen cavity diagnostic. Geometry is exact under the construction. Dynamic,
elemental, DNA, toroidal, and cosmological meanings remain experimental.

Implementation:

- src/universe_port_engine.py
- tests/test_universe_port_engine.py
- docs/universe_port_engine_v0.1.md

## 4D. Conservative Vesica and Tree circulation

The port geometry now carries a minimal discrete continuity layer. For signed
edge current (J), the node convention is outgoing current minus incoming
current, and the local update obeys

\[
\frac{dq_a}{dt}+(\operatorname{div}J)_a=0.
\]

The local Vesica graph routes one through-current from cusp (A), through the
neutral center, to cusp (B), then returns it over two separately labeled lens
channels. The return currents sum to the through-current, so all three nodes
have zero divergence.

On the Flower-derived Tree, the normalized outer flow carries equal total flux
across every radial cut. The inner flow is its exact weighted reverse, and
same-ring weave currents are closed cycles. Their sum is therefore locally
balanced. Central mirroring preserves route weights and exchanges the positive
and negative pillar fluxes.

Recursive scale transfer is represented by a distinct parent-child address
edge. It is neither a Flower route nor a transitive-plane branch. Plane and
possibility changes are supplied by the separately typed subsystem below.

Implementation:

- src/vesica_tree_circulation.py
- tests/test_vesica_tree_circulation.py
- docs/vesica_tree_circulation_v0.1.md

## 4E. Plane overlap and possibility branching

The transitive-plane layer uses a product address

\[
X=(u,p,b)
\]

with independent recursive-universe, named-plane, and possibility-path
coordinates. An elementary move changes exactly one coordinate. Scale moves
join adjacent universe paths, plane moves follow one declared overlap edge,
and branch moves append or remove one signed outcome token. Mixed-coordinate
moves fail closed.

The plane catalogue is open rather than a fixed stack. The included Chapter 8
topology records explicitly described overlap routes while leaving a named
plane disconnected when no link was supplied. Indirect transitions must pass
through declared intermediary nodes.

Possibility labels occur in mirrored integer pairs with neutral zero. Branch
weights are nonnegative, normalized, and equal on each signed pair. The
outward split preserves total dimensionless content; adding exact return edges
makes the branch circulation divergence-free.

Implementation:

- src/transitive_plane_branching.py
- tests/test_transitive_plane_branching.py
- docs/transitive_plane_branching_v0.1.md

## 4F. Multidimensional Sri Yantra fibre

The Sri Yantra layer is defined first as an embedding-independent ordered
complex. Its canonical inventory retains nine generators, with four upward
and five downward orientations, and nine outer-to-inner enclosures. The five
triangular enclosure counts sum to

\[
14+10+10+8+1=43.
\]

Plane, spherical, and Meru forms are distinct typed realizations. The engine
also provides explicitly labelled higher-simplex and spiral-cone candidates.
Intrinsic and ambient dimension are stored separately, so a curved
two-dimensional spherical network embedded in three dimensions is not silently
called a three-dimensional volume.

The fibre state extends the existing base address without replacing it:

\[
Y=((u,p,b),a,m,\varphi;R,f,h),
\]

where \(a\) is enclosure, \(m\) is local member, \(\varphi\) is rational
phase, \(R\) is realization, \(f\) is inward/stationary/outward flow, and
\(h\) is handedness. Projection and lift change only \(R\). Recursive scale,
named plane, possibility path, enclosure, and phase remain explicit.

The dimension-open generator template is the centered regular \(d\)-simplex
in \(d+1\) barycentric coordinates. Its opposite orientation is exact central
inversion. At \(d=3\), the two orientations give a dual-tetrahedron compound
with eight vertices, providing a local bridge to the stella octangula without
equating the complete nine-generator Yantra with one stella.

Adjacent enclosure currents carry a constant dimensionless cut flux. The
inward and outward routes are exact reverses; their equal superposition has
zero divergence on all nine enclosures. No current is identified with energy,
Ether, Consciousness, or another physical observable in this layer.

Implementation:

- src/sri_yantra_multidimensional.py
- tests/test_sri_yantra_multidimensional.py
- docs/sri_yantra_multidimensional_v0.1.md

## 5. Open discrete-exterior-calculus layer

The default open field adapter uses a cubical complex with cochain sequence

\[
C^0\xrightarrow{d_0}C^1\xrightarrow{d_1}C^2
\]

and exact identity

\[
d_1d_0=0.
\]

The weak Hamiltonian form is

\[
H
=
\frac12\langle E,E\rangle
+
\frac{\beta}{2}\langle d_1A,d_1A\rangle.
\]

Representative modules:

- src/open_gauge_dynamics.py
- src/open_boundary_solver.py
- src/open_polarity_sources.py
- src/unified_engine.py

## 6. Six-gate open Gauss layer

The open finite-volume field satisfies a source/flux balance of the form

\[
\nabla_{\rm open}\cdot E+b_{\partial V}=\rho.
\]

Global compatibility is

\[
\sum_x\rho(x)=\sum_{g\in B_6}\Phi_g^{E,\mathrm{outward}}.
\]

The scalar-potential solve uses a matrix-free Neumann Laplacian and projected preconditioned conjugate gradients.

Implementation:

- src/open_boundary_solver.py

## 7. Source layer

The engine separates several source mechanisms rather than collapsing them into one quantity.

### 6.1 Polarization-induced source

\[
P=A\sigma\hat u,
\]

\[
\rho_{\rm pol}=-\nabla\cdot P.
\]

### 6.2 Free electric source

\[
\dot\rho_{\rm free}+\nabla\cdot J_{\rm free}=0.
\]

### 6.3 Six-gate boundary exchange

Internal total electric charge changes only through explicit boundary exchange.

### 6.4 Topological magnetic source

Compact plaquette winding can generate integer-valued magnetic/topological defects. These are kept separate from ordinary electric charge.

Representative modules:

- src/polarity_sources.py
- src/open_polarity_sources.py
- src/source_channels.py
- src/source_interaction.py

## 8. Abelian and non-Abelian gauge layer

The repository contains compact U(1), SU(2), and SU(3) lattice-gauge implementations.

For U(1),

\[
U_{ij}=e^{i\theta_{ij}}.
\]

For non-Abelian sectors,

\[
U_\mu(x)\to G(x)U_\mu(x)G^\dagger(x+\hat\mu).
\]

Implemented capabilities include plaquettes and Wilson actions, Hamiltonian electric-field dynamics, Gauss constraints, analytic staple forces, fundamental matter coupling, gauge/matter backreaction, and geometry-dependent weighting.

## 9. Reciprocity geometry layer

The experimental reciprocity metric is

\[
ds^2=-e^{-2\psi}c_*^2dt^2+e^{2\psi}d\mathbf x^2.
\]

The current stack includes a self-consistent scalar action, matter and gauge coupling, static spherical vacuum solutions, weak-field and higher-order correspondence, circular-orbit and light-deflection calculations, and geometry backreaction.

The reciprocity premises remain experimental assumptions until derived from deeper canonical structure or validated empirically.

## 10. Dirac and chiral fermion layer

The repository contains Wilson-Dirac reference operators, reciprocity-background Dirac Hamiltonians, one-particle geometry backreaction, overlap-Dirac operators, Ginsparg-Wilson chirality, modified chiral projectors, overlap-index diagnostics, Weyl measure curvature and holonomy, finite Weyl determinants, charged-U(1) anomaly diagnostics, SU(2)/SU(3) overlap fermions, and product-group overlap representations.

## 11. Product-group anomaly layer

The repository computes supported anomaly coefficients for supplied Weyl spectra, including

\[
C_{SU(3)^3},\qquad
C_{SU(3)^2U(1)},\qquad
C_{SU(2)^2U(1)},\qquad
C_{U(1)^3},\qquad
C_{{\rm grav}^2U(1)}.
\]

The SU(2) global mod-2 doublet condition is tracked separately.

This layer tests candidate spectra. It does not derive the observed Standard Model representation content.

## 12. Spatial protocol layer

src/spatial_protocol.py defines versioned transport-neutral messages for commands, acknowledgements, telemetry, stop requests, and capability discovery.

This allows WebXR, robotics adapters, digital twins, APIs, and customer-specific transports to share one command vocabulary.

## 13. Spatial operations safety layer

src/spatial_operations_control.py provides software-level validation for stale-command rejection, replay protection, deadman controls, workspace boundaries, position-delta limits, linear-speed limits, angular-speed limits, emergency-stop request propagation, and deterministic bounded waypoint generation.

It does not itself authorize real hardware execution.

## 14. Robot adapter layer

src/robot_adapter.py defines a common robot contract for capabilities, state, command submission, stop requests, and acknowledgements.

The same interface can back simulated robots, ROS2 bridges, CAN devices, CNC systems, or customer-specific OEM hardware.

## 15. XR-to-robot bridge

src/xr_robot_bridge.py connects versioned spatial commands to the common robot adapter only after validation through the spatial operations control plane.

An XR or browser client therefore cannot bypass software command validation through this bridge.

## 16. Digital-twin layer

src/digital_twin_contract.py distinguishes measured telemetry from derived estimates and carries units, source, timestamp, quality, calibration, and uncertainty.

src/digital_twin_store.py provides a bounded thread-safe reference history store.

Production deployments can replace the in-memory store with a persistent database or stream backend without changing the telemetry contract.

## 17. Manufacturing layer

Current manufacturing and toolpath surfaces include authenticated G-code compilation, parametric path generation, CNC/GRBL compatibility, winding-path tools, visualization, geometry optimization prototypes, and stress/thermal digital-twin utilities.

Historical manufacturing modules can contain older SO(13), 114-node, toroidal, or 3/6/9 labels. Those labels are not canonical unless explicitly migrated and tested.

## 18. API and SDK layer

The current secured API is src/api_server.py.

It provides health, metrics, matrix evaluation, G-code compilation, spatial command validation, commercial entitlement evaluation, and audit-ledger access.

SDKs:

- sdk/python/universal_matrix_sdk.py
- sdk/js/universalMatrixSdk.js

The larger src/api.py remains a compatibility/experimental surface and should not be exposed publicly by default.

## 19. Commercial entitlement layer

src/commercial_entitlements.py models licensable product families and feature entitlements.

Technical entitlements do not themselves grant legal rights. The governing public license or executed commercial agreement controls.

## 20. Licensing and governance layer

The public repository is source-available for permitted noncommercial use under the PolyForm Noncommercial License 1.0.0.

Relevant files:

- LICENSE
- NOTICE
- COMMERCIAL_LICENSE.md
- COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md
- CLA.md
- CONTRIBUTING.md
- docs/LICENSING_GUIDE.md

Commercial use outside the public license requires a separate written Waters Legacy Trust commercial license unless otherwise permitted by applicable law.

## 21. Legacy compatibility layer

Older modules can contain terminology such as Z_114 as a routing group, SO(13) physical spacetime, 64-bit physical geometry, fixed 3/6/9 physical laws, M-theory/string/brane equivalence labels, toroidal physical geometry, biological/chakra/meridian mappings, or hand-authored physical constants.

These are historical, compatibility, visualization, or experimental surfaces unless explicitly migrated to the current canonical stack.

No legacy module overrides src/canonical_kernel.py, tests/test_canonical_kernel.py, or the current canonical specification.

## 22. Verification hierarchy

The repository uses three scientific verification levels.

### Level A: exact finite identities

Deterministic algebraic tests for the canonical kernel.

### Level B: numerical structural invariants

Gauge covariance, DEC exactness, Gauss consistency, continuity, Hermiticity, chiral identities, unitarity, solver residuals, and bounded-control behavior.

### Level C: physical validation

External experiment or observation with units, independently fixed parameters, uncertainty, and falsification criteria.

A Level A or Level B result must not be presented as Level C evidence.

## 23. Software verification

Current CI includes Python 3.12 core verification, Python 3.14 core verification, full legacy compatibility tests, container smoke tests, CodeQL analysis, and licensing-governance regression checks.

Typical developer workflow:

~~~bash
uv sync --group dev --extra scientific
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
~~~

## 24. Documentation authority

When repository documents disagree, use:

1. tested implementation for the subsystem in question;
2. src/canonical_kernel.py and tests/test_canonical_kernel.py for canonical finite mathematics;
3. docs/canonical_spec_v0.4.md;
4. white_paper.md;
5. README.md and this architecture document;
6. current subsystem technical notes;
7. historical inventories and legacy documentation.

See docs/DOCUMENTATION_STATUS.md.


## 4G. Higher-dimensional regular families and E8 bridge

`src/higher_dimensional_geometry.py` extends the exact finite geometry into
arbitrary-dimensional simplex, hypercube, and cross-polytope families. It
keeps simplex mirror completion distinct from cross-polytope geometry and
implements recursive coordinate projections for the two centrally symmetric
families.

The same module builds the 240-root E8 configuration in integer coordinates
scaled by two, verifies exact root-reflection closure, and embeds the existing
24-cell dual D4 root subsystem into E8. No E8 coordinate is assigned a physical
interpretation in this layer.

Primary verification: `tests/test_higher_dimensional_geometry.py`.
Primary note: `docs/higher_dimensional_e8_bridge_v0.1.md`.


## 4H. Direct H4 to E8 lift

`src/h4_direct_e8_lift.py` starts from the existing 120 H4 / 600-cell roots in
Q(phi)^4, forms H4 union phi*H4, and uses the reduced rational-coefficient inner
product to obtain an exact 240-root E8 system. Resolving each a+b*phi component
into its two rational coefficients yields an eight-component representation
with exact rank eight.

Primary verification: `tests/test_h4_direct_e8_lift.py`.
Primary note: `docs/h4_direct_e8_lift_v0.1.md`.


## 4I. Exact equivalence of the two E8 realizations

`src/e8_equivalence_map.py` independently selects simple-root bases inside the
H4-derived and standard E8 root sets, matches their Dynkin Gram structure, and
derives the exact rational map between them. The map is a scale-sqrt(8)
orthogonal transformation, maps all 240 roots bijectively, and intertwines
central mirror and root reflections.

Primary verification: `tests/test_e8_equivalence_map.py`.
Primary note: `docs/e8_equivalence_map_v0.1.md`.


## 4J. E8 state representation audit

`src/e8_state_audit.py` separates E8 root/Cartan coordinates from existing
physical state variables. The canonical Z_108 core, the 8 x 8 register, and the
eight-component SU(3) electric field are explicitly rejected as full E8 state
representations. A dedicated `E8CartanState` carries only the rank-eight Weyl
reflection action.

Primary verification: `tests/test_e8_state_audit.py`.
Primary note: `docs/e8_state_representation_audit_v0.1.md`.


## 4K. Gauge-compatible E8 scalar coupling

`src/e8_invariant_coupling.py` supplies the minimal optional interaction
`g ||h||^2 O`, where `h` is an `E8CartanState` and `O` is a scalar already
invariant under the gauge group of its own sector. The E8 layer remains a gauge
singlet with respect to U(1), SU(2), and SU(3); no componentwise identification
with their fields is introduced.

Primary verification: `tests/test_e8_invariant_coupling.py`.
Primary note: `docs/e8_invariant_coupling_v0.1.md`.


## 4L. E8 coupling observable audit

`src/e8_coupling_observable_audit.py` verifies that the quadratic E8 invariant
is constant across the fixed 240-root orbit. The currently available scalar
couplings are therefore classified as parameter renormalizations or source
shifts rather than distinct orientation-sensitive E8 dynamics. No preferred
physical observable is selected.

Primary verification: `tests/test_e8_coupling_observable_audit.py`.
Primary note: `docs/e8_coupling_observable_audit_v0.1.md`.


## 4M. E8 radial-degree audit

`src/e8_radial_degree_audit.py` checks whether any existing amplitude, content,
or scale variable can supply a genuinely independent E8 radius. Matter
amplitude, port circulation amplitude, nested hierarchy amplitude, neutral
content, and scale level are all rejected because they are already committed
to other subsystem roles. A distinct E8 radial mode would require a new
independently motivated degree of freedom.

Primary verification: `tests/test_e8_radial_degree_audit.py`.
Primary note: `docs/e8_radial_degree_audit_v0.1.md`.


## 4N. Sri Yantra incidence and topology audit

`src/sri_yantra_incidence_topology_audit.py` separates declared abstract
topology from historical incidence that is not yet encoded. It enumerates 72
abstract enclosure locations, 70 same-enclosure cyclic edges, and eight
adjacent-enclosure shell interfaces. The current spherical and spiral-cone
candidate charts are tested for injective placement of all declared locations.

The Huet planar chamber graph is now numerically derived by the extractor in
section 4Q. Exact generator-pair intersection multiplicities and
incidence-preserving equivalence with historical spherical and Meru
realizations remain explicitly open.

Primary verification:
`tests/test_sri_yantra_incidence_topology_audit.py`.
Primary note:
`docs/sri_yantra_incidence_topology_audit_v0.1.md`.


## 4O. Sourced Sri Yantra concurrency contract

`src/sri_yantra_chiodo_concurrency.py` encodes the minimal planar concurrency
conditions in Chiodo 2021. It fixes the t1..t9 orientation convention, the
t3/t7 common circumcircle, seven apex-to-base incidences, twelve three-line
concurrencies, and the four ordered base parameters P,Q,R,S on the normalized
diameter. The resulting graph describes maximal-triangle constraints; the
separate extractor in section 4Q computes chamber boundaries and contacts.

Primary verification: `tests/test_sri_yantra_chiodo_concurrency.py`.
Primary note: `docs/sri_yantra_chiodo_concurrency_v0.1.md`.


## 4P. Huet reference Sri Yantra planar reconstruction

`src/sri_yantra_huet_planar.py` reconstructs the nine maximal planar
triangles for the Huet parameter choice quoted by Chiodo. The common t3/t7
circumcircle initializes the solution; the remaining apex locations, base
locations, and leg slopes are derived from the sourced apex/base and
three-line concurrency conditions. The implementation emits all 27 finite
maximal-triangle edges and verifies closure to numerical precision.

Primary verification: `tests/test_sri_yantra_huet_planar.py`.
Primary note: `docs/sri_yantra_huet_planar_v0.1.md`.


### Huet 43-chamber incidence extraction

`src/sri_yantra_huet_chambers.py` reconstructs the traditional chamber complex
from the 27 finite Huet parent edges rather than storing chamber coordinates.
It derives 69 snapped arrangement nodes and 122 supported triangular circuits,
finds the nine atomic symmetry-axis anchors, identifies the central t1/t5
chamber, and solves the four nested mirror-closed ring constraints.

The Huet reference has one globally conflict-free solution with chamber counts
1, 8, 10, 10, and 14. Its rings are vertex-touching cycles with 3, 16, 20, 20,
and 28 unique circuit vertices, and the complete chamber set has 129 distinct
edges.

Primary verification: `tests/test_sri_yantra_huet_chambers.py`.
Primary note: `docs/sri_yantra_huet_chambers_v0.1.md`.

## 4Q. Huet planar chamber complex

`src/sri_yantra_chambers.py` constructs the planar arrangement of the 27
finite edges, retaining every incidence vertex. It computes 74 bounded faces
and independently classifies generator coverage and dual-graph exterior
depth. The odd-coverage faces yield 43 triangles at depths 1, 3, 5, 7, 9, with
ring sizes 14, 10, 10, 8, 1. Shared-vertex adjacency recovers four connected
cycles and one central chamber. Face adjacency and chamber contact are
different relations: selected chambers never share an atomic edge.

The extractor exposes immutable geometry and uses only the standard library.
Normalization makes its coincidence tolerance relative to the input extent.
This is numerically verified Huet geometry; historical spherical/Meru maps
and topology throughout the parameter family are not established.

Primary verification: `tests/test_sri_yantra_chambers.py`.
Primary note: `docs/sri_yantra_chambers_v0.1.md`.
Diagram generator: `scripts/render_sri_yantra_chambers.py`.

Primary verification: \`tests/test_sri_yantra_huet_chambers.py\`.
Primary note: \`docs/sri_yantra_huet_chambers_v0.1.md\`.


### Spherical chamber-topology control

`src/sri_yantra_spherical_topology_control.py` lifts the complete derived
43-chamber planar complex through one inverse-stereographic homeomorphism.
Chamber IDs, ring cycles, mirror pairing, and all incidence data are preserved
by construction while the carrier becomes a unit sphere.

This is a topology control, not Rao's sourced great-circle spherical Sri Yantra.
It exists so later spherical reconstructions can distinguish genuine
constraint-induced incidence changes from a harmless change of embedding.

Primary verification: `tests/test_sri_yantra_spherical_topology_control.py`.
Primary note: `docs/sri_yantra_spherical_topology_control_v0.1.md`.

## Rao great-circle incidence

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


## Graph-to-toroidal flux bundle

`src/graph_toroidal_flux_bundle.py` is the first explicit graph-to-volume
coupling layer. It assigns one translated compact toroidal field domain to
each `DirectedCurrent`, uses the graph edge current as the signed poloidal cut
flux, and preserves the source/target incidence ledger for node-divergence
checks. Pairwise-disjoint supports keep the summed prescribed field locally
divergence-free without introducing hidden junction dynamics.

Primary verification: `tests/test_graph_toroidal_flux_bundle.py`.
Primary note: `docs/graph_toroidal_flux_bundle_v0.1.md`.


## Connected toroidal junction control volumes

`src/toroidal_junction_control_volume.py` replaces conservative graph-node
balance as ledger-only bookkeeping with explicit connected 3D control volumes.
Incident edge contributions are classified as inlet or outlet boundary fluxes,
decomposed into nonoverlapping transfer lanes, and carried by analytic fields
of the form `(f(y,z),0,0)`, which have zero interior divergence.

The layer is coupled to `GraphToroidalFluxBundle` and checks source-port,
toroidal-cut, and target-port flux continuity for every edge.

Primary verification: `tests/test_toroidal_junction_control_volume.py`.
Primary note: `docs/toroidal_junction_control_volume_v0.1.md`.


## Toroidal connector topology and annular Piola bridge

`src/toroidal_connector_topology.py` audits the cross-section topology of the
junction and toroidal interfaces. Disk-like rectangular lane ports are not
diffeomorphic to the annular poloidal cut, so a nonsingular one-to-one sweep is
rejected. The torus is represented as cut open along the annulus, exposing two
boundary copies with opposite outward flux.

For annular source ports, an explicit smoothstep coordinate map and
contravariant Piola transform give a zero-divergence connector with positive
Jacobian, preserved transverse flux, and pointwise target-vector agreement with
the purely poloidal toroidal field.

Primary verification: `tests/test_toroidal_connector_topology.py`.
Primary note: `docs/toroidal_connector_topology_v0.1.md`.


## Annular junction edge ports

`src/toroidal_annular_junction.py` replaces disk-like external junction ports
with concentric annular bands. Lower and upper face streamfunctions encode the
incident flux distributions; cubic interpolation between them produces an
axisymmetric zero-divergence internal current. Cumulative-flux interval
overlaps recover the deterministic conservative transfer plan.

The annular boundary profile is algebraically identical to the source profile
of `AnnularPiolaConnector`, providing local topology and flux-density
compatibility.

Primary verification: `tests/test_toroidal_annular_junction.py`.
Primary note: `docs/toroidal_annular_junction_v0.1.md`.


## Framed toroidal edge assemblies

`src/toroidal_framed_edge_assembly.py` composes annular junction ports,
general annular Piola transitions, and a straightened flux-equivalent
cut-open toroidal chart into one local edge assembly. Internal interface
vectors agree pointwise and all adjacent outward fluxes cancel.

The edge-local axial frame uses `sign(current)` to align negative-current
assemblies with the fixed axial direction of the annular junction fields while
retaining the signed graph flux.

Primary verification: `tests/test_toroidal_framed_edge_assembly.py`.
Primary note: `docs/toroidal_framed_edge_assembly_v0.1.md`.


## Global collision-audited toroidal routing

`src/toroidal_global_routing.py` supplies a deterministic global embedding
contract for the local framed edge assemblies. Annular junctions are translated
rigidly along x; every edge receives a unique y corridor and high/low z level.
Endpoint tangents follow `axis_sign * +z` and therefore preserve the signed
annular junction frame contract.

The routing layer uses conservative tube envelopes and exact finite-segment
distance calculations to reject nonincident edge collisions and
edge-to-nonincident-junction overlaps.

Primary verification: `tests/test_toroidal_global_routing.py`.
Primary note: `docs/toroidal_global_routing_v0.1.md`.


## Smooth positive-Jacobian toroidal bends

`src/toroidal_smooth_bends.py` turns each orthogonal global route corner into
a quarter-circle annular tube. The bend map retains a positive Jacobian when
its bend radius exceeds the annular outer radius. The straight annular current
is transported by the contravariant Piola map, yielding the same radial flux
density along the bend tangent and exact vector matching at both interfaces.

The global routing envelope is expanded by the bend radius so the previously
verified collision audit also bounds the curved volume.

Primary verification: `tests/test_toroidal_smooth_bends.py`.
Primary note: `docs/toroidal_smooth_bends_v0.1.md`.


## Same-face incident connector overlap audit

`src/toroidal_incident_overlap_audit.py` evaluates pairs of nonzero edge
connectors sharing one annular junction face. It parameterizes each connector
from the junction port to the channel annulus and detects radial-interval
overlap by bisection.

The current common-channel construction necessarily overlaps because disjoint
port bands continuously converge to one identical channel annulus. This
obstruction prevents promotion of the nonincident routing certificate to a
complete whole-network collision certificate.

Primary verification: `tests/test_toroidal_incident_overlap_audit.py`.
Primary note: `docs/toroidal_incident_overlap_audit_v0.1.md`.


## Edge-specific separated toroidal channel shells

`src/toroidal_separated_channels.py` replaces the common cut annulus used by
all framed edges with globally ordered, pairwise-disjoint edge-specific
annular shells. Each shell is the inner poloidal cut of its own purely poloidal
toroidal field and preserves the signed graph current.

Since same-face junction bands and channel shells share edge-index order, the
smooth radial Piola interpolation cannot reverse interval order. The earlier
same-face connector overlap is therefore removed without changing the annular
junction or framed-edge APIs.

Primary verification: `tests/test_toroidal_separated_channels.py`.
Primary note: `docs/toroidal_separated_channels_v0.1.md`.


## Incident smooth-bend collision audit

`src/toroidal_incident_bend_audit.py` evaluates actual annular bend samples
against the exact finite endpoint straight shell of every other nonzero edge
sharing the same junction face. Positive penetration requires both axial and
radial interior membership.

The audit shows that separated channel shells solve the coaxial connector
overlap but do not solve the later bend/straight interaction for the tested
compact reference parameters.

Primary verification: `tests/test_toroidal_incident_bend_audit.py`.
Primary note: `docs/toroidal_incident_bend_audit_v0.1.md`.


## Toroidal bend-spacing parameter gate

`src/toroidal_bend_spacing_scan.py` preserves the existing graph, signed
currents, annular junctions, Piola connector maps, and smooth-bend field while
varying edge-shell radial gap and positive bend-radius margin.

The deterministic 25-point Vesica grid contains both colliding samples and at
least one collision-free sample. The compact incident-bend result is therefore
a parameter-dependent no-fit rather than a topology theorem.

The next geometry layer is boundary mapping and scale-consistency testing. A
separate-axis fan-out is reserved as a fallback if no compact
scale-consistent clearance region survives.

Primary verification: `tests/test_toroidal_bend_spacing_scan.py`.
Primary note: `docs/toroidal_bend_spacing_scan_v0.1.md`.


## Canonical mod-9 quotient audit

`src/canonical_mod9_interface_audit.py` is a derived exact-arithmetic layer
over the canonical `Z_108` kernel. It uses reduction modulo nine to label the
nine `E = T_9` orbits and a twelve-step phase coordinate inside each orbit.

It also records the independent multiplication-by-two automorphism of `Z_9`
and its three orbit classes. That automorphism is not a canonical translation
operator and remains separate from `E`, `P`, and `T_21`.

Primary verification: `tests/test_canonical_mod9_interface_audit.py`.
Primary note: `docs/canonical_mod9_interface_audit_v0.1.md`.
