# Universal Matrix

**Author:** Matthew Waters  
**Steward:** Waters Legacy Trust  
**Software version:** 0.4.0  
**White paper:** Version 0.5  
**Runtime:** Python 3.12+

![Verification](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/verification.yml/badge.svg)
![Container Pipeline](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/pipeline_test.yml/badge.svg)
![CodeQL](https://github.com/QuantumInquisitor/universal-matrix/actions/workflows/codeql.yml/badge.svg)

Universal Matrix is a modular mathematical, scientific-computing, spatial-operations, robotics, manufacturing, digital-twin, and edge-integration platform built around a finite 108-state canonical core, six external boundary orientations, and a 64-address projection layer.

It is more than a theory document or a single simulation engine. The repository contains an executable finite mathematical kernel, numerical field solvers, reciprocity-geometry research models, U(1), SU(2), and SU(3) lattice gauge systems, overlap and Ginsparg-Wilson fermion tooling, Weyl measure diagnostics, product-group anomaly bookkeeping, authenticated APIs, Python and JavaScript SDKs, container and Kubernetes deployment assets, observability tooling, 5-axis G-code compilation, robotics and XR/VR prototypes, digital-twin modules, hardware-abstraction interfaces, and enterprise licensing/metering components.

The project intentionally separates exact finite mathematics from numerical verification, experimental physical interpretation, commercial software surfaces, and legacy compatibility code. A passing unit test establishes software behavior under tested assumptions. It does not by itself establish a new law of nature or certify production hardware.

## Project maturity labels

| Status | Meaning |
| --- | --- |
| **CANONICAL** | Exact finite definitions and identities of the current mathematical kernel. |
| **NUMERICALLY VERIFIED** | Software or numerical properties exercised by tests with stated tolerances. |
| **EXPERIMENTAL** | Physical, engineering, or interpretive extensions requiring independent validation. |
| **LEGACY / COMPATIBILITY** | Older interfaces retained for migration, testing, or historical compatibility. |

The canonical specification and executable tests take precedence over older descriptive material.

## Canonical mathematical kernel

The canonical architecture is

[
mathcal A = mathbb Z_{108} sqcup B_6
]

with

[
B_6={+X,-X,+Y,-Y,+Z,-Z}.
]

Primary operators include

[
E=T_9,
qquad
P=T_{54},
qquad
F(n)=107-n,
]

with the canonical routing convention

[
T=T_{21},
]

selected from the synchronized class

[
{21,57,93}
]

by the minimal-positive-lift convention.

Important exact identities include

[
E^{12}=I,
qquad
T^{36}=I,
qquad
T^{18}=P,
qquad
P^2=I.
]

The register projection is

[
pi(n)=7nmod64.
]

The 64-address layer is a finite address structure. When represented as six independent binary boundary channels it is naturally a six-bit state space. It is not a claim of a 64-bit physical spacetime.

**Executable authority**

- `src/canonical_kernel.py`
- `tests/test_canonical_kernel.py`
- `docs/canonical_spec_v0.4.md`
- `white_paper.md`

## What the platform can do

### Finite discrete computation

The canonical engine can:

- route and invert (mathbb Z_{108}) state transitions;
- apply interface, polarity, and reflection operators;
- encode and decode mixed-radix coordinates;
- compute 64-address projections and carry-aware deltas;
- enumerate routing cycles, polarity pairs, collisions, and synchronized lifts;
- exhaustively verify the current finite-kernel identities.

### Nested polarity and scale dynamics

Experimental modules support:

- polarity-sensitive routing;
- canonical 36-tick phase evolution;
- alternating scale orientation;
- nested self-similar layers;
- conservative adjacent-scale exchange;
- neutral-crossing transfer models;
- source and interaction channels across nested scales.

### Open-field and DEC solvers

The current open-field stack supports:

- discrete node, edge, and plaquette cochains;
- exact (d_1d_0=0) checks;
- open finite-volume Gauss constraints;
- nonzero enclosed charge;
- six-gate boundary flux accounting;
- matrix-free projected conjugate-gradient solving;
- manufactured-solution tests;
- source continuity and charge-balance diagnostics.

Representative modules:

- `src/open_gauge_dynamics.py`
- `src/open_boundary_solver.py`
- `src/open_polarity_sources.py`
- `src/unified_engine.py`

### U(1), SU(2), and SU(3) lattice research

The repository includes:

- compact U(1) links, plaquettes, Wilson actions, and Hamiltonian evolution;
- Gauss constraints and weak-field lattice dispersion;
- SU(2) and SU(3) matrix-valued link systems;
- analytic staple forces checked against reference calculations;
- fundamental matter coupling;
- gauge/matter backreaction;
- reciprocity-geometry weighting.

### Reciprocity geometry and coupled dynamics

Experimental reciprocity modules include:

- clock-space reciprocity;
- scalar geometry dynamics;
- stationary source-universality tests;
- static spherical vacuum solutions under the stated model;
- weak-field and higher-order correspondence calculations;
- light-deflection and circular-orbit diagnostics;
- matter, U(1), SU(2), and SU(3) geometry coupling;
- unified variational and backreaction studies.

These are model-derived research results under explicit assumptions. They are not presented as experimentally established replacements for General Relativity.

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
- Weyl bases, curvature, holonomy, and Stokes consistency;
- finite Weyl determinants;
- charged-U(1) anomaly diagnostics;
- SU(2)/SU(3) fundamental overlap fermions;
- (SU(3)	imes SU(2)	imes U(1)) product-representation overlap operators;
- perturbative product-group anomaly bookkeeping.

The code can test a supplied candidate representation spectrum. It does not currently derive the observed Standard Model spectrum or hypercharges from the finite kernel.

### Research API and SDKs

The secured research API in `src/api_server.py` provides:

- health reporting;
- Prometheus metrics;
- authenticated experimental matrix evaluation;
- authenticated 5-axis G-code compilation;
- cryptographic audit-ledger access.

No production or demo API credentials are embedded in source.

SDKs:

- `sdk/python/universal_matrix_sdk.py`
- `sdk/js/universalMatrixSdk.js`

The much larger `src/api.py` surface is retained for compatibility and experimental integration. It includes hardware, telemetry, cluster, spatial, optimization, and legacy routes and should not be exposed publicly by default without dedicated security review.

### Manufacturing and toolpaths

The platform includes:

- authenticated 5-axis G-code generation;
- parametric toolpath generation;
- toroidal/winding research paths;
- CNC/GRBL adapters;
- toolpath visualization;
- geometry optimization prototypes;
- stress/thermal digital-twin utilities.

Some older modules retain historical SO(13), 3/6/9, or toroidal terminology. Those labels are not canonical unless separately implemented and tested.

### Robotics and spatial operations

The repository already contains:

- 6-DoF robotics trajectory prototypes;
- spatial teleoperation packets;
- WebXR controller pose ingestion;
- ROS2-style command bridges;
- CAN and CNC adapters;
- swarm coordination prototypes;
- HIL mocks;
- tenant/hardware authorization;
- digital-twin state modules.

The productization branch adds `src/spatial_operations_control.py`, which provides:

- stale-command rejection;
- replay protection;
- deadman enforcement;
- workspace bounds;
- position, linear-speed, and angular-speed limiting;
- emergency-stop request propagation;
- deterministic bounded waypoint generation;
- explicit separation between command validation and real hardware execution.

This is the beginning of a coherent spatial-operations control layer for XR, robotics, digital twins, and industrial interfaces.

### XR / VR and spatial interfaces

Existing surfaces include:

- WebXR pose processing;
- spatial viewports;
- teleoperation packets;
- browser/WebSocket compatibility routes;
- haptic-command generation;
- 3D visualization;
- advanced VR laboratory prototypes;
- micro-to-macro visualization prototypes;
- digital-twin telemetry.

These can be developed into remote operations, training, scientific visualization, maintenance, and digital-twin products.

### Digital twins and predictive operations

The repository contains virtual-twin, telemetry, maintenance, stress/thermal, and sensor-ingestion modules that can be developed into:

- machine/equipment twins;
- robotics state mirrors;
- manufacturing process monitors;
- predictive-maintenance dashboards;
- research-instrument twins;
- fleet health analytics.

Derived estimates should be clearly separated from directly measured telemetry and validated against real datasets before production claims.

### Hardware and HIL integration

Compatibility and experimental adapters exist for areas including:

- CNC and motion control;
- CAN and field-bus messaging;
- sensor ingestion;
- SDR/RF adapters;
- FPGA tooling;
- external QPU adapters;
- photonic and CUDA adapters;
- ROS2-style bridges;
- WebXR/spatial teleoperation;
- swarm/edge orchestration;
- hardware-in-the-loop testing.

**Real hardware is fail-closed by default.**

Real hardware mode requires both:

```bash
export UNIVERSAL_MATRIX_SYSTEM_MODE=REAL
export UNIVERSAL_MATRIX_ALLOW_HARDWARE=1
```

Individual drivers may require additional ports, devices, libraries, credentials, executors, or independent hardware interlocks.

Software interlocks are not a substitute for physical safety systems.

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
- GitHub Actions verification;
- Python 3.12 and 3.14 core matrices;
- a full legacy compatibility suite;
- container smoke testing;
- CodeQL scanning;
- container provenance and SBOM generation.

## Licensable product families

The repository can be commercially licensed as a full platform or by product family. The detailed productization roadmap is in:

`docs/COMMERCIAL_PRODUCT_SURFACES.md`

| Product family | Scope |
| --- | --- |
| **Universal Matrix Core** | Canonical kernel, projection/routing logic, SDKs, and private embedding. |
| **Universal Matrix Spatial** | XR/VR, spatial command protocols, teleoperation, and digital-twin viewing. |
| **Universal Matrix Robotics** | Bounded commands, trajectory services, ROS2/CAN/CNC adapters, HIL, and swarm research tooling. |
| **Universal Matrix Manufacturing** | G-code, toolpaths, visualization, optimization, and machine adapters. |
| **Universal Matrix Research** | Gauge, reciprocity, Dirac, overlap/chiral, anomaly, and numerical research stack. |
| **Universal Matrix Edge** | HAL/device adapters, telemetry, orchestration, deployment, and audit infrastructure. |
| **Universal Matrix Enterprise** | Private APIs, tenancy, entitlements, metering, deployment support, and negotiated proprietary terms. |

The branch also contains `src/commercial_entitlements.py`, which models these families independently so a commercial agreement can authorize only the capabilities actually purchased.

These are packaging and engineering boundaries. Legal rights are defined by the governing public license or an executed commercial agreement.

## Scientific boundaries

The project does not currently claim to have experimentally established:

- a replacement for General Relativity;
- a replacement for quantum mechanics or quantum field theory;
- equivalence with string theory, M-theory, loop quantum gravity, or other external theories;
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

### Run verification

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

Configure an API key:

```bash
export UNIVERSAL_MATRIX_API_KEYS="replace-with-secret:RESEARCH"
```

Optional CORS origins:

```bash
export UNIVERSAL_MATRIX_CORS_ORIGINS="https://example.org"
```

Start:

```bash
uv run uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```

Authenticated requests use:

```text
X-API-Key: replace-with-secret
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

## Container deployment

```bash
export UNIVERSAL_MATRIX_API_KEYS="replace-with-secret:RESEARCH"
export GRAFANA_ADMIN_PASSWORD="replace-with-strong-password"

docker compose up --build
```

## Repository structure

```text
src/                    Core engine, research models, APIs, drivers, and adapters
tests/                  Canonical, numerical, physics-stack, compatibility, and property tests
docs/                   Technical notes, audits, derivations, and product documentation
sdk/python/             Python client
sdk/js/                 JavaScript client
scripts/                Analysis, verification, load-test, and maintenance utilities
config/                 Runtime/manufacturing configuration
k8s/                    Kubernetes deployment manifest
charts/                 Helm chart
grafana/                Grafana provisioning
white_paper.md          Single authoritative white paper
ARCHITECTURE.md         Current software architecture
CLA.md                  Contributor License Agreement
CONTRIBUTING.md         Contribution rules
LICENSE                 Licensing notice
```

## Documentation

Recommended starting points:

- `white_paper.md`
- `ARCHITECTURE.md`
- `docs/canonical_spec_v0.4.md`
- `docs/HOW_TO_USE.md`
- `docs/physics_stack_status_2026-09.md`
- `docs/repository_audit_2026-09.md`
- `docs/COMMERCIAL_PRODUCT_SURFACES.md`
- `docs/comparative_theory_bridge_audit_v0.1.md`

## Security and operational safeguards

The secured research API uses environment-provided credentials, constant-time API-key comparison, explicit credentialed CORS origins, metrics, and a cryptographic audit ledger.

The legacy API requires additional care and should remain private unless explicitly configured and reviewed.

The repository also uses CI verification, container smoke tests, and CodeQL analysis. These controls are not a complete production security certification.

## Commercial Licensing & Legal Framework

This project follows a dual-licensing strategy.

### Public open-source option

The project is offered under the GNU Affero General Public License, version 3 or later, subject to the repository's `LICENSE` file.

The AGPL permits commercial as well as noncommercial use. Users choosing the AGPL option must comply with its copyleft and network-source obligations where those obligations apply to the covered work.

### Enterprise commercial license

A separate proprietary commercial license is available from Waters Legacy Trust for organizations that want negotiated proprietary terms instead of the AGPL.

Typical cases include:

- proprietary SaaS/network deployments that do not want AGPL source-disclosure obligations for the covered work;
- OEM embedding;
- closed-source commercial products;
- proprietary hardware integration;
- private XR/robotics/manufacturing deployments;
- private scientific-compute integrations;
- enterprise redistribution;
- customer-specific derivatives;
- support and integration agreements.

Commercial licenses can cover the complete platform or selected product families.

**Commercial licensing contact:** waterslegacytrust@gmail.com

This README is an overview, not a substitute for the governing license or legal advice.

## Contributing

Contributions are welcome from developers, mathematicians, physicists, numerical researchers, robotics/XR engineers, documentation writers, and reviewers.

To preserve the project's dual-licensing structure, external contributors must agree to `CLA.md` before a contribution can be merged.

Under the current CLA:

- contributors retain ownership of their contributions;
- contributors grant Waters Legacy Trust the rights needed to use, distribute, sublicense, and dual-license accepted contributions;
- contributors represent that they have authority to submit the work.

Before opening a pull request:

1. Read `CLA.md` and `CONTRIBUTING.md`.
2. Create a focused branch.
3. Keep canonical, numerically verified, experimental, and legacy claims separate.
4. Add or update tests.
5. Run the relevant verification suite.
6. Document assumptions, units, calibration, and falsification criteria for new physical claims.
7. Do not describe simulated or unbenchmarked hardware behavior as certified production performance.

## Formal Academic Citations & Reference Framework

The older "114-node SO(13)" and "v93.0.0" citation language is superseded by the current canonical architecture and software release.

### Mathematical and physical framework

**Waters, Matthew. (2026). _The Universal Matrix: Canonical Finite Architecture, Reciprocity Field Dynamics, and Chiral Lattice Extensions_. Working Mathematical and Physical Preprint, Version 0.5. Waters Legacy Trust Research Program.**

Authoritative manuscript:

`white_paper.md`

### Software and computational platform

**Waters, Matthew. (2026). _Universal Matrix_ (Version 0.4.0) [Computer software]. QuantumInquisitor GitHub repository. https://github.com/QuantumInquisitor/universal-matrix**

### Suggested BibTeX

```bibtex
@misc{waters2026universalmatrix,
  author       = {Matthew Waters},
  title        = {The Universal Matrix: Canonical Finite Architecture, Reciprocity Field Dynamics, and Chiral Lattice Extensions},
  year         = {2026},
  version      = {0.5},
  note         = {Working Mathematical and Physical Preprint, Waters Legacy Trust Research Program}
}
```

```bibtex
@software{waters2026universalmatrixsoftware,
  author  = {Matthew Waters},
  title   = {Universal Matrix},
  year    = {2026},
  version = {0.4.0},
  url     = {https://github.com/QuantumInquisitor/universal-matrix}
}
```

## Contact

**Matthew Waters**  
**Waters Legacy Trust**  
Commercial licensing and project inquiries: **waterslegacytrust@gmail.com**

## Responsible use

This repository includes experimental physics, engineering, optimization, robotics, manufacturing, XR, and hardware-control research surfaces. Users are responsible for evaluating the suitability, legality, safety, and regulatory requirements of their deployments.

Do not connect unvalidated software directly to hazardous equipment without independent safety engineering, physical interlocks, and qualified supervision.
