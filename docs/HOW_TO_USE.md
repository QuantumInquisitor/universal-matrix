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
