# Universal Matrix

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Software version:** 0.4.0  
**White paper:** Version 0.6  
**Runtime:** Python 3.12+

![Verification](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/verification.yml/badge.svg)
![Container Pipeline](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/pipeline_test.yml/badge.svg)
![CodeQL](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/codeql.yml/badge.svg)

Universal Matrix is a source-available mathematical and scientific-computing platform built around a finite 108-state canonical core, six external boundary orientations, and a 64-address projection layer. Around that kernel, the repository develops tested geometry, field, lattice-gauge, fermion, spatial-computing, robotics, digital-twin, manufacturing, API, and deployment systems.

The project is deliberately layered. Exact finite mathematics is kept distinct from numerically verified software behavior, experimental physical interpretation, engineering interfaces, commercial product surfaces, and legacy compatibility code.

A passing test establishes behavior under the tested assumptions. It does not by itself establish a new law of nature, certify physical hardware, or replace an established physical theory.

## At a glance

| Layer | Role | Current status |
| --- | --- | --- |
| Canonical finite kernel | 108-state algebra, operators, routing, projection | **CANONICAL** |
| Recursive and sacred geometry | Seed, Vesica, Flower, Tree, Sri Yantra, higher-dimensional families | **EXACT / NUMERICALLY VERIFIED by subsystem** |
| Toroidal circulation | Conservative graph-to-volume routing and junction geometry | **NUMERICALLY VERIFIED, active geometry gate** |
| Gauge and fermion stack | U(1), SU(2), SU(3), Dirac, overlap, chiral and anomaly tooling | **NUMERICALLY VERIFIED research software** |
| Reciprocity and matter models | Candidate field, matter, Q-ball and coupled-dynamics studies | **EXPERIMENTAL** |
| Spatial and robotics stack | XR/VR, robot adapters, validation, digital twins | **ENGINEERING / EXPERIMENTAL** |
| Manufacturing | G-code, toolpaths, CNC/GRBL and winding utilities | **ENGINEERING / EXPERIMENTAL** |
| API and operations | Authenticated services, SDKs, containers, observability, Kubernetes | **SOFTWARE / PRODUCT** |
| Legacy compatibility | Historical terminology, APIs, models and migration surfaces | **LEGACY / COMPATIBILITY** |

## Canonical architecture

The current finite architecture is

$$
\mathcal A=\mathbb Z_{108}\sqcup B_6,
$$

with

$$
B_6=\{+X,-X,+Y,-Y,+Z,-Z\}.
$$

Canonical translations are

$$
T_d(n)=n+d\pmod{108}.
$$

The principal operators are

$$
E=T_9,\qquad P=T_{54},\qquad F(n)=107-n.
$$

The synchronized routing condition gives the class

$$
\{21,57,93\},
$$

and the current convention selects

$$
T=T_{21}
$$

by the minimal-positive-lift rule.

Important exact identities include

$$
E^{12}=I,\qquad
T^{36}=I,\qquad
T^{18}=P,\qquad
P^2=I.
$$

The register projection is

$$
\pi(n)=7n\bmod 64.
$$

The 64-address layer is a finite addressing structure. When represented as six independent binary boundary channels, it is a six-bit state space. It is not a claim of a 64-bit physical spacetime.

### Canonical authority

The finite kernel is defined and tested primarily in:

- [src/canonical_kernel.py](src/canonical_kernel.py)
- [tests/test_canonical_kernel.py](tests/test_canonical_kernel.py)
- [docs/canonical_spec_v0.4.md](docs/canonical_spec_v0.4.md)
- [white_paper.md](white_paper.md)

A derived mod-9/interface-phase audit is maintained separately in [docs/canonical_mod9_interface_audit_v0.1.md](docs/canonical_mod9_interface_audit_v0.1.md). That quotient analysis does not replace the canonical transition law.

## Evidence and maturity labels

| Label | Meaning |
| --- | --- |
| **CANONICAL** | Exact finite definitions and identities of the current mathematical kernel. |
| **EXACT FINITE RESULT** | A theorem-like identity or finite construction established within its stated model. |
| **NUMERICALLY VERIFIED** | Software or numerical behavior exercised by tests with defined tolerances. |
| **MODEL-DERIVED** | A result that follows from explicit model assumptions but is not externally validated. |
| **EXPERIMENTAL** | A physical, engineering, or interpretive extension requiring independent validation. |
| **LEGACY / COMPATIBILITY** | Historical code or terminology retained for migration, regression, provenance, or interoperability. |

When documents disagree, tested implementation and current canonical specifications take precedence over historical prose. See [docs/DOCUMENTATION_STATUS.md](docs/DOCUMENTATION_STATUS.md).

## Platform architecture

### 1. Finite discrete computation

The canonical engine can:

- route and invert $\mathbb{Z}_{108}$ state transitions;
- apply interface, polarity, and reflection operators;
- encode and decode mixed-radix coordinates;
- compute 64-address projections and carry-aware deltas;
- enumerate routing cycles, polarity pairs, register collisions, and synchronized routing lifts;
- exhaustively verify current finite-kernel identities.

### 2. Recursive geometry and scale structure

The repository includes tested constructions for:

- contained seven-circle Seed geometry;
- exact equal-circle Vesica interfaces;
- recursive child-vessel addressing;
- Flower growth and derived Tree routing;
- negative, neutral, and positive pillar classification;
- graph-content continuity across Vesica and Tree routes;
- explicit parent-child scale-current edges;
- named-plane overlap routing;
- mirror-paired possibility branching;
- embedding-independent Sri Yantra state structure;
- planar, spherical, Meru, simplex-family and spiral-cone realizations;
- arbitrary-dimensional simplex, hypercube and cross-polytope families;
- H4, 24-cell, D4 and E8 mathematical bridge studies.

These constructions are not all claims about physical spacetime. Each subsystem note states its own evidence boundary.

### 3. Sri Yantra geometry

The Sri Yantra program separates abstract incidence from any one visual projection.

Current verified or audited components include:

- four upward and five downward maximal generators;
- nine ordered enclosures;
- the traditional 43 selected triangular chambers for the audited Huet reference;
- independent chamber extraction and incidence checks;
- a topology-preserving spherical control;
- an audited Rao great-circle reference for one corrected parameter row;
- an explicit Meru candidate control;
- dimension-open simplex and spiral-cone candidate realizations.

Primary entry points:

- [docs/sri_yantra_multidimensional_v0.1.md](docs/sri_yantra_multidimensional_v0.1.md)
- [docs/sri_yantra_chambers_v0.1.md](docs/sri_yantra_chambers_v0.1.md)
- [docs/sri_yantra_rao_great_circles_v0.1.md](docs/sri_yantra_rao_great_circles_v0.1.md)
- [docs/sri_yantra_meru_candidate_v0.1.md](docs/sri_yantra_meru_candidate_v0.1.md)

### 4. Toroidal circulation and connected field geometry

The toroidal program develops a conservative three-dimensional routing construction from discrete graph currents.

The current chain includes:

1. conservative toroidal cut-flux fields;
2. graph-to-toroidal channel assignment;
3. connected junction control volumes;
4. topology-correct annular connectors;
5. annular junction edge ports;
6. framed edge assemblies;
7. global routed placement;
8. smooth positive-Jacobian annular bends;
9. same-face incident overlap auditing;
10. edge-specific separated channel shells;
11. incident bend/straight collision auditing.

The present compact separated-shell geometry removes coaxial connector overlap but still produces incident bend/straight intersections in the tested Vesica and Flower/Tree references.

The active geometric gate is therefore to determine whether spacing and curvature alone admit a collision-free, scale-consistent region. If not, same-face incident edges require a separate-axis spatial fan-out before whole-network field sampling can be admitted.

Primary notes:

- [docs/conservative_toroidal_field_v0.1.md](docs/conservative_toroidal_field_v0.1.md)
- [docs/graph_toroidal_flux_bundle_v0.1.md](docs/graph_toroidal_flux_bundle_v0.1.md)
- [docs/toroidal_connector_topology_v0.1.md](docs/toroidal_connector_topology_v0.1.md)
- [docs/toroidal_separated_channels_v0.1.md](docs/toroidal_separated_channels_v0.1.md)
- [docs/toroidal_incident_bend_audit_v0.1.md](docs/toroidal_incident_bend_audit_v0.1.md)
- [docs/toroidal_bend_spacing_scan_v0.1.md](docs/toroidal_bend_spacing_scan_v0.1.md)
- [docs/MATRIX_ENGINE_WORK_QUEUE.md](docs/MATRIX_ENGINE_WORK_QUEUE.md)

### 5. Gauge, Dirac and chiral lattice research

The repository contains tested research implementations for:

- compact U(1) lattice gauge fields;
- SU(2) and SU(3) matrix-valued links;
- plaquettes, Wilson actions and Hamiltonian evolution;
- Gauss constraints and weak-field lattice dispersion;
- fundamental matter coupling;
- analytic staple-force checks;
- Wilson-Dirac reference operators;
- overlap-Dirac operators;
- Ginsparg-Wilson chirality;
- modified chiral projectors;
- Weyl bases, projector curvature and holonomy;
- finite Weyl determinants;
- U(1), SU(2), SU(3) and product-group anomaly diagnostics.

The code can test supplied candidate representation spectra. It does not currently derive the observed Standard Model particle content or hypercharges from the finite kernel.

### 6. Matter, reciprocity and Q-ball research

Experimental research modules include:

- polarity-sensitive matter routing;
- a 36-step phase clock;
- local rotor and transition-law candidates;
- clock-space reciprocity;
- scalar geometry-action studies;
- weak-field and spherical diagnostics;
- charged-matter and Q-ball existence studies;
- threshold refinement;
- radial-to-Cartesian mapping audits;
- finite-time persistence and time-series diagnostics;
- matter, gauge and geometry backreaction candidates.

These results are model-derived or numerically verified within stated assumptions. They are not presented as experimentally established replacements for General Relativity, quantum mechanics, or quantum field theory.

### 7. Spatial computing, robotics and digital twins

The engineering stack includes:

- versioned transport-neutral spatial commands;
- stale-command rejection;
- replay protection;
- deadman enforcement;
- workspace and motion limits;
- emergency-stop request propagation;
- a common robot-adapter contract;
- XR-to-robot command bridging;
- typed measured-versus-derived telemetry;
- bounded digital-twin history;
- ROS2, CAN, CNC and OEM adapter surfaces.

The intended control path is:

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

Real hardware remains fail-closed by default and requires independent physical safety systems.

### 8. Manufacturing and toolpaths

Current surfaces include:

- authenticated G-code compilation;
- parametric toolpath generation;
- CNC/GRBL compatibility;
- winding-path research;
- geometry and toolpath visualization;
- optimization prototypes;
- stress and thermal digital-twin utilities.

Historical manufacturing modules can retain older terminology for provenance. Those labels do not become canonical unless explicitly migrated and tested.

### 9. API, SDKs and operations

The secured API in [src/api_server.py](src/api_server.py) provides:

- health reporting;
- Prometheus metrics;
- authenticated Matrix evaluation;
- authenticated G-code compilation;
- spatial-command validation;
- commercial-entitlement evaluation;
- cryptographic audit-ledger access.

SDKs:

- [sdk/python/universal_matrix_sdk.py](sdk/python/universal_matrix_sdk.py)
- [sdk/js/universalMatrixSdk.js](sdk/js/universalMatrixSdk.js)

Operational assets include Docker, Docker Compose, Kubernetes, Helm, Prometheus, Grafana, CodeQL, container smoke tests, provenance and SBOM generation.

The broader [src/api.py](src/api.py) surface remains a compatibility and experimental integration layer and should not be exposed publicly without dedicated review.

## Current scientific gates

| Research gate | Current state |
| --- | --- |
| Huet planar Sri Yantra chambers | Implemented and independently cross-checked |
| Spherical topology control | Implemented |
| Rao great-circle reference | Implemented for one corrected reference row |
| Meru geometry | Explicit conical candidate implemented, independent historical metric remains open |
| Broader Rao family | Open |
| Toroidal whole-network field | A collision-free spacing/curvature point exists in the tested grid; boundary mapping and scale-consistency remain open |
| Physical normalization | Open derivation |
| Six-gate/sevenfold physical coupling | Open derivation |
| Particle interpretation | Open physical identification |
| Thermodynamics and cosmology | Open physical validation |
| Falsifiable physical predictions | Required before strong physical claims |

The live research queue is maintained in [docs/MATRIX_ENGINE_WORK_QUEUE.md](docs/MATRIX_ENGINE_WORK_QUEUE.md), while the broader physics inventory is in [docs/physics_stack_status_2026-09.md](docs/physics_stack_status_2026-09.md).

## Scientific boundaries

Universal Matrix does not currently claim to have experimentally established:

- a replacement for General Relativity;
- a replacement for quantum mechanics or quantum field theory;
- equivalence with string theory, M-theory, loop quantum gravity, or another external theory;
- exact SI constants derived from the finite kernel;
- a derived Standard Model particle spectrum;
- medically validated bio-field or consciousness physics;
- certified industrial safety or guaranteed production hardware performance.

Calibration to a known result must be identified as calibration, not derivation.

## Repository map

| Path | Purpose |
| --- | --- |
| [src/](src/) | Canonical kernel, numerical research, APIs, spatial and engineering modules |
| [tests/](tests/) | Canonical, numerical, regression, security and compatibility verification |
| [docs/](docs/) | Specifications, subsystem notes, research status, licensing and usage |
| [white_paper.md](white_paper.md) | Current mathematical and scientific preprint |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed software and subsystem architecture |
| [scripts/](scripts/) | Rendering, analysis and repository utilities |
| [sdk/](sdk/) | Python and JavaScript client SDKs |
| [deploy/](deploy/) | Deployment and operations assets |
| [LICENSE](LICENSE) | PolyForm Noncommercial License 1.0.0 |
| [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) | Commercial licensing framework |

## Quick start

### Requirements

- Python 3.12 or newer
- Git
- [uv](https://docs.astral.sh/uv/) recommended

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

The CI matrix also exercises Python 3.12 and 3.14, the full compatibility suite, container smoke tests and CodeQL analysis.

## Research API

Install API dependencies:

```bash
uv sync --group dev --extra api --extra scientific
```

Configure an API key:

```bash
export UNIVERSAL_MATRIX_API_KEYS="replace-with-secret:RESEARCH"
```

Start locally:

```bash
uv run uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```

Primary secured endpoints:

```text
GET  /health
GET  /metrics
POST /api/v1/matrix/evaluate
POST /api/v1/gcode/compile
POST /api/v1/spatial/validate-command
POST /api/v1/commercial/entitlements/evaluate
GET  /api/v1/audit/ledger
```

See [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md) for the complete workflow.

## Hardware safety

Real hardware mode requires both:

```bash
export UNIVERSAL_MATRIX_SYSTEM_MODE=REAL
export UNIVERSAL_MATRIX_ALLOW_HARDWARE=1
```

Software interlocks are not substitutes for physical emergency stops, machine guarding, electrical protection, collision protection, qualified supervision, or regulatory compliance.

A passing unit test is not a hardware safety certification.

## Documentation authority

Start here:

1. [README.md](README.md), repository overview and entry point.
2. [white_paper.md](white_paper.md), current scientific and mathematical preprint.
3. [ARCHITECTURE.md](ARCHITECTURE.md), software and subsystem architecture.
4. [docs/canonical_spec_v0.4.md](docs/canonical_spec_v0.4.md), canonical finite specification.
5. [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md), installation, API, verification and safety workflows.
6. [docs/CURRENT_REPOSITORY_MANIFEST.md](docs/CURRENT_REPOSITORY_MANIFEST.md), subsystem map.
7. [docs/physics_stack_status_2026-09.md](docs/physics_stack_status_2026-09.md), research status.
8. [docs/MATRIX_ENGINE_WORK_QUEUE.md](docs/MATRIX_ENGINE_WORK_QUEUE.md), active scientific gates.
9. Versioned subsystem notes in [docs/](docs/).

The complete authority policy is defined in [docs/DOCUMENTATION_STATUS.md](docs/DOCUMENTATION_STATUS.md).

## Licensable product families

| Product family | Scope |
| --- | --- |
| **Universal Matrix Core** | Canonical kernel, routing, projection, SDK integration and private embedding |
| **Universal Matrix Spatial** | XR/VR, spatial commands, teleoperation and digital-twin viewing |
| **Universal Matrix Robotics** | Bounded robotics commands, adapter contracts, HIL and ROS2/CAN/CNC integration |
| **Universal Matrix Manufacturing** | G-code, toolpaths, visualization, optimization and machine adapters |
| **Universal Matrix Research** | Gauge, reciprocity, matter, Dirac, chiral, anomaly and numerical research |
| **Universal Matrix Edge** | Device adapters, telemetry, orchestration, deployment and audit |
| **Universal Matrix Enterprise** | Private APIs, tenancy, entitlements, deployment support and negotiated terms |

See [docs/COMMERCIAL_PRODUCT_SURFACES.md](docs/COMMERCIAL_PRODUCT_SURFACES.md).

## Licensing

Universal Matrix uses a source-available noncommercial plus proprietary commercial licensing model.

The public repository is licensed under the **PolyForm Noncommercial License 1.0.0** for covered noncommercial use. It is **source-available, not OSI open source**, because general commercial use is restricted.

Commercial use outside the public license requires a separate written Waters Legacy Trust commercial license unless applicable law independently permits the use.

Read:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)
- [docs/LICENSING_GUIDE.md](docs/LICENSING_GUIDE.md)
- [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)
- [COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md](COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md)

**Commercial licensing:** waterslegacytrust@gmail.com

## Contributing

External contributions require acceptance of [CLA.md](CLA.md) unless Waters Legacy Trust expressly waives that requirement in writing.

Contributions should preserve the repository's distinctions between canonical mathematics, numerical verification, experimental interpretation, engineering surfaces and legacy compatibility.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Citation

### Mathematical and physical framework

Waters, Matthew. (2026). *The Universal Matrix: Canonical Finite Architecture, Reciprocity Field Dynamics, and Chiral Lattice Extensions*. Working Mathematical and Physical Preprint, Version 0.6. Waters Legacy Trust Research Program.

### Software

Waters, Matthew. (2026). *Universal Matrix* (Version 0.4.0) [Computer software]. QuantumInquisitor GitHub repository.

## Contact

**Matthew Waters**  
**Waters Legacy Trust**  
waterslegacytrust@gmail.com

## Responsible use

This repository contains experimental physics, engineering, optimization, robotics, manufacturing, XR and hardware-control research surfaces. Users are responsible for evaluating suitability, legality, safety and regulatory obligations for their own deployments.
