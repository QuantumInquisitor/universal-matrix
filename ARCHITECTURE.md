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
