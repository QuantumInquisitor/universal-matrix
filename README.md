# Universal Matrix

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Software version:** 0.4.0  
**White paper:** Version 0.6  
**Runtime:** Python 3.12+

![Verification](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/verification.yml/badge.svg)
![Container Pipeline](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/pipeline_test.yml/badge.svg)
![CodeQL](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/codeql.yml/badge.svg)

Universal Matrix is a modular mathematical, scientific-computing, spatial-operations, robotics, manufacturing, digital-twin, and edge-integration platform built around a finite canonical architecture

\[
\mathcal A=\mathbb Z_{108}\sqcup B_6,
\]

where

\[
B_6=\{+X,-X,+Y,-Y,+Z,-Z\}.
\]

The repository is more than a theory manuscript or a single simulation engine. It contains an executable finite mathematical kernel, numerical field solvers, reciprocity-geometry research models, U(1), SU(2), and SU(3) lattice-gauge systems, overlap and Ginsparg-Wilson fermion tooling, Weyl-measure diagnostics, product-group anomaly bookkeeping, authenticated APIs, Python and JavaScript SDKs, container and Kubernetes deployment assets, observability tooling, G-code and manufacturing utilities, robotics and XR/VR interfaces, digital-twin infrastructure, hardware-abstraction adapters, and commercial entitlement components.

The project deliberately separates exact finite mathematics, numerically verified software behavior, experimental physical interpretation, commercial product surfaces, and legacy compatibility code. A passing test establishes behavior under the tested assumptions. It does not by itself establish a new law of nature, certify hardware, or replace an established physical theory.

## Project maturity labels

| Status | Meaning |
| --- | --- |
| **CANONICAL** | Exact finite definitions and identities of the current mathematical kernel. |
| **NUMERICALLY VERIFIED** | Software or numerical properties exercised by tests with defined tolerances. |
| **EXPERIMENTAL** | Physical, engineering, or interpretive extensions requiring independent validation. |
| **LEGACY / COMPATIBILITY** | Older modules retained for migration, regression, provenance, or historical compatibility. |

When files disagree, current executable tests and canonical specifications take precedence over historical prose.

## Canonical finite architecture

The canonical translations are

\[
T_d(n)=n+d\pmod{108}.
\]

The principal operators are

\[
E=T_9,\qquad P=T_{54},\qquad F(n)=107-n.
\]

The synchronized routing condition gives the class

\[
\{21,57,93\},
\]

and the current canonical convention selects

\[
T=T_{21}
\]

by the minimal-positive-lift rule.

Important exact identities include

\[
E^{12}=I,\qquad T^{36}=I,\qquad T^{18}=P,\qquad P^2=I.
\]

The register projection is

\[
\pi(n)=7n\bmod 64.
\]

The 64-address layer is a finite addressing structure. When represented as six independent binary boundary channels, it is a six-bit state space. It is not a claim of a 64-bit physical spacetime.

**Executable authority**

- `src/canonical_kernel.py`
- `tests/test_canonical_kernel.py`
- `docs/canonical_spec_v0.4.md`
- `white_paper.md`

## What the platform can do

### Finite discrete computation

The canonical engine can:

- route and invert \(\mathbb Z_{108}\) state transitions;
- apply interface, polarity, and reflection operators;
- encode and decode mixed-radix coordinates;
- compute 64-address projections and carry-aware deltas;
- enumerate routing cycles, polarity pairs, register collisions, and synchronized routing lifts;
- exhaustively verify the current finite-kernel identities.

### Nested polarity and scale dynamics

Experimental modules support:

- polarity-sensitive routing;
- a canonical 36-step phase clock;
- alternating scale orientation;
- nested self-similar layers;
- conservative adjacent-scale exchange;
- neutral-crossing transfer models;
- source and interaction channels across micro-to-macro scale layers.

### Open-field and discrete-exterior-calculus solvers

The open-field stack supports:

- node, edge, and plaquette cochains;
- exact checks such as \(d_1d_0=0\);
- open finite-volume Gauss constraints;
- nonzero enclosed charge;
- six-gate boundary-flux accounting;
- matrix-free projected conjugate-gradient solving;
- manufactured-solution tests;
- source continuity and charge-balance diagnostics.

Representative modules include:

- `src/open_gauge_dynamics.py`
- `src/open_boundary_solver.py`
- `src/open_polarity_sources.py`
- `src/unified_engine.py`

### U(1), SU(2), and SU(3) lattice-gauge research

The repository contains tested research implementations for:

- compact U(1) links, plaquettes, Wilson actions, and Hamiltonian evolution;
- Gauss constraints and weak-field lattice dispersion;
- SU(2) and SU(3) matrix-valued links;
- analytic staple forces checked against reference calculations;
- fundamental matter coupling;
- gauge/matter backreaction;
- reciprocity-geometry weighting.

### Reciprocity geometry and coupled dynamics

The experimental reciprocity program includes:

- clock-space reciprocity;
- a scalar geometry action;
- stationary source-universality tests;
- static spherical vacuum solutions under the stated model;
- weak-field and higher-order correspondence calculations;
- light-deflection and circular-orbit diagnostics;
- matter, U(1), SU(2), and SU(3) geometry coupling;
- unified variational and backreaction studies.

These are model-derived results under explicit assumptions. They are not presented as experimentally established replacements for General Relativity.

### Dirac and chiral lattice tooling

The current fermion stack includes:

- Wilson-Dirac reference operators;
- gauge-covariant Wilson-Dirac operators;
- reciprocity-background Dirac propagation;
- analytic Dirac geometry sources;
- one-particle semiclassical Dirac/geometry backreaction;
- overlap-Dirac operators;
- Ginsparg-Wilson chirality;
- modified chiral projectors;
- overlap-index diagnostics;
- Weyl bases, projector curvature, closed-loop holonomy, and Stokes consistency;
- finite Weyl determinants;
- charged-U(1) anomaly diagnostics;
- SU(2) and SU(3) fundamental overlap fermions;
- (SU(3)	imes SU(2)	imes U(1)) product-representation overlap operators;
- perturbative product-group anomaly bookkeeping.

The code can test a supplied candidate representation spectrum. It does not currently derive the observed Standard Model spectrum or hypercharges from the finite kernel.

### Research API and SDKs

The secured API in `src/api_server.py` provides:

- health reporting;
- Prometheus metrics;
- authenticated experimental matrix evaluation;
- authenticated G-code compilation;
- bounded spatial-command validation;
- commercial-entitlement evaluation;
- cryptographic audit-ledger access.

SDKs are provided in:

- `sdk/python/universal_matrix_sdk.py`
- `sdk/js/universalMatrixSdk.js`

The larger `src/api.py` surface remains a compatibility and experimental integration layer and should not be exposed publicly without dedicated review.

### Robotics, XR/VR, and digital twins

The productized spatial stack now includes:

- versioned transport-neutral spatial commands;
- stale-command rejection;
- replay protection;
- deadman enforcement;
- workspace and motion limits;
- emergency-stop request propagation;
- a common robot-adapter contract;
- a bounded XR-to-robot bridge;
- typed measured-versus-derived telemetry;
- a bounded thread-safe digital-twin history store;
- ROS2/CAN/CNC and other adapter surfaces.

The intended commercial control path is:

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
robot acknowledgement + state
        ↓
typed digital twin
        ↓
telemetry / history / audit
```

Real hardware remains fail-closed by default and requires independent physical safety controls.

### Manufacturing and toolpaths

The repository includes:

- authenticated 5-axis G-code generation;
- parametric toolpath generation;
- winding-path research tools;
- CNC/GRBL adapters;
- toolpath visualization;
- geometry-optimization prototypes;
- stress/thermal digital-twin utilities.

Historical modules may retain older SO(13), 3/6/9, toroidal, or 114-node terminology. Those terms are not canonical unless a current module and test explicitly establish them.

### Deployment and operations

The repository includes:

- a non-root Docker runtime;
- Docker Compose;
- Prometheus;
- Grafana provisioning;
- optional nginx reverse proxy;
- Kubernetes manifests;
- Helm charts;
- synthetic load testing;
- Python 3.12 and 3.14 verification;
- a full legacy compatibility suite;
- container smoke testing;
- CodeQL scanning;
- container provenance and SBOM generation.

## Licensable product families

The platform can be licensed as a whole or by product family.

| Product family | Scope |
| --- | --- |
| **Universal Matrix Core** | Canonical kernel, routing/projection logic, SDK integration, private embedding. |
| **Universal Matrix Spatial** | XR/VR, spatial commands, teleoperation, digital-twin viewing. |
| **Universal Matrix Robotics** | Bounded robotics commands, adapter contracts, HIL, ROS2/CAN/CNC integration, swarm research. |
| **Universal Matrix Manufacturing** | G-code, toolpaths, visualization, optimization, machine adapters. |
| **Universal Matrix Research** | Gauge, reciprocity, Dirac, overlap/chiral, anomaly, and numerical research stack. |
| **Universal Matrix Edge** | HAL/device adapters, telemetry, orchestration, deployment, audit. |
| **Universal Matrix Enterprise** | Private APIs, tenancy, entitlements, metering, deployment support, negotiated proprietary terms. |

See `docs/COMMERCIAL_PRODUCT_SURFACES.md` and `docs/ROBOTICS_XR_PRODUCT_ARCHITECTURE.md`.

## Scientific boundaries

The project does not currently claim to have experimentally established:

- a replacement for General Relativity;
- a replacement for quantum mechanics or quantum field theory;
- equivalence with string theory, M-theory, loop quantum gravity, or another external theory;
- exact SI constants derived from the finite kernel;
- a derived Standard Model particle spectrum;
- medically validated bio-field or consciousness physics;
- certified industrial safety or guaranteed production hardware performance.

Calibration to a known result must be labeled as calibration rather than derivation.

## Quick start

### Requirements

- Python 3.12 or newer
- `uv` recommended
- Git

### Install

```bash
git clone https://github.com/QuantumInquisitor/universal-matrix.git
cd universal-matrix
uv sync --group dev --extra scientific
```

### Verify

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```

Focused canonical verification:

```bash
uv run pytest -q tests/test_canonical_kernel.py tests/test_property_invariants.py
```

## Research API

Install API dependencies:

```bash
uv sync --extra api
```

Configure credentials:

```bash
export UNIVERSAL_MATRIX_API_KEYS="replace-with-secret:RESEARCH"
```

Start locally:

```bash
uv run uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```

Primary secured endpoints include:

```text
GET  /health
GET  /metrics
POST /api/v1/matrix/evaluate
POST /api/v1/gcode/compile
POST /api/v1/spatial/validate-command
POST /api/v1/commercial/entitlements/evaluate
GET  /api/v1/audit/ledger
```

## Hardware safety

Real hardware mode requires both:

```bash
export UNIVERSAL_MATRIX_SYSTEM_MODE=REAL
export UNIVERSAL_MATRIX_ALLOW_HARDWARE=1
```

Individual drivers can require additional ports, libraries, credentials, executors, or device-specific configuration.

Software interlocks are not a substitute for independent hardware interlocks, machine guarding, electrical protection, collision protection, qualified supervision, or regulatory compliance.

## Documentation

Start with:

- `white_paper.md`
- `ARCHITECTURE.md`
- `docs/DOCUMENTATION_STATUS.md`
- `docs/CURRENT_REPOSITORY_MANIFEST.md`
- `docs/canonical_spec_v0.4.md`
- `docs/HOW_TO_USE.md`
- `docs/physics_stack_status_2026-09.md`
- `docs/COMMERCIAL_PRODUCT_SURFACES.md`
- `docs/ROBOTICS_XR_PRODUCT_ARCHITECTURE.md`
- `docs/omniverse_design_questions_v0.1.md`

Historical files are retained for provenance but do not override current canonical or experimental documentation.

## Commercial Licensing & Legal Framework

Universal Matrix uses a **source-available noncommercial + proprietary commercial** dual-license model.

### Free noncommercial public license

The public source is licensed under the **PolyForm Noncommercial License 1.0.0**.

The public license covers permitted noncommercial uses such as personal study, hobby work, covered educational use, covered academic/public research, charitable use, and individual research or experimentation without anticipated commercial application.

This is source-available, not OSI open source, because general commercial use is restricted.

### Commercial license required

Use outside the permitted noncommercial scope requires a separate written Waters Legacy Trust commercial license unless applicable law independently permits the use.

Commercial licensing is intended for uses including:

- revenue-generating SaaS or hosted services;
- paid consulting built around the platform;
- internal commercial business deployment;
- proprietary products;
- OEM embedding;
- closed-source software;
- commercial robotics;
- commercial XR/VR and digital twins;
- manufacturing and CNC products;
- commercial hardware integration;
- enterprise deployment;
- commercial research and development;
- redistribution as part of a commercial offering.

Commercial licenses can cover the full platform or selected product families.

**Commercial licensing contact:** waterslegacytrust@gmail.com

See:

- `LICENSE`
- `NOTICE`
- `docs/LICENSING_GUIDE.md`
- `COMMERCIAL_LICENSE.md`
- `COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md`

## Contributing

External contributions require acceptance of `CLA.md` unless Waters Legacy Trust expressly waives that requirement in writing.

Contributors retain ownership of their contributions while granting Waters Legacy Trust the rights needed to distribute, sublicense, dual-license, and commercially license accepted contributions.

See `CONTRIBUTING.md` for the complete development rules.

## Formal citation

### Mathematical and physical framework

**Waters, Matthew. (2026). _The Universal Matrix: Canonical Finite Architecture, Reciprocity Field Dynamics, and Chiral Lattice Extensions_. Working Mathematical and Physical Preprint, Version 0.6. Waters Legacy Trust Research Program.**

### Software

**Waters, Matthew. (2026). _Universal Matrix_ (Version 0.4.0) [Computer software]. QuantumInquisitor GitHub repository. https://github.com/QuantumInquisitor/universal-matrix**

## Contact

**Matthew Waters**  
**Waters Legacy Trust**  
waterslegacytrust@gmail.com

## Responsible use

This repository includes experimental physics, engineering, optimization, robotics, manufacturing, XR, and hardware-control research surfaces. Users are responsible for evaluating suitability, legality, safety, and regulatory obligations for their own deployments.
