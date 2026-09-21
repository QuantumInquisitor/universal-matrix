# Universal Matrix — Current Usage Guide

## Status

This guide describes the reconstructed v0.4 research stack.

The canonical mathematical kernel is stable relative to the current branch. Physical gauge, polarity, source, and boundary layers remain experimental. Legacy hardware, biological, quantum, SO(13), and enterprise modules are compatibility/demo surfaces unless explicitly migrated.

## 1. Recommended environment

Python 3.12 or newer is supported by project metadata. CI exercises the canonical/open engine on Python 3.12 and 3.14.

Recommended setup:

```bash
git clone https://github.com/QuantumInquisitor/universal-matrix.git
cd universal-matrix

uv sync --group dev --extra scientific
```

Run lint and tests:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```

For all optional legacy integrations:

```bash
uv sync --group test --all-extras
uv run pytest
```

`pyproject.toml` is the authoritative dependency configuration. `requirements.txt` remains only for legacy pip workflows.

## 2. Canonical kernel

Primary files:

- `src/canonical_kernel.py`
- `tests/test_canonical_kernel.py`
- `docs/canonical_spec_v0.4.md`

Quick verification:

```bash
uv run pytest -q tests/test_canonical_kernel.py tests/test_property_invariants.py
```

## 3. Open gauge engine

Current default experimental physical path:

- `src/open_gauge_dynamics.py`
- `src/open_boundary_solver.py`
- `src/open_polarity_sources.py`
- `src/unified_engine.py`

Focused verification:

```bash
uv run pytest -q \
  tests/test_open_boundary_solver.py \
  tests/test_open_gauge_dynamics.py \
  tests/test_open_polarity_sources.py \
  tests/test_unified_engine.py
```

## 4. Research API

Prefer the smaller API in:

`src/api_server.py`

No credentials are embedded in source.

Configure API keys:

```bash
export UNIVERSAL_MATRIX_API_KEYS="replace-with-secret:RESEARCH"
```

Optional CORS origins:

```bash
export UNIVERSAL_MATRIX_CORS_ORIGINS="https://example.org"
```

Start locally:

```bash
uv sync --extra api
uv run uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```

Send authenticated requests with:

```text
X-API-Key: replace-with-secret
```

Do not use wildcard credentialed CORS.

## 5. Legacy compatibility API

`src/api.py` is a large historical API surface with many experimental subsystems.

It should not be exposed publicly by default.

If it must be used, configure a process JWT secret:

```bash
export UNIVERSAL_MATRIX_JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
```

The legacy operator password route is disabled unless this is explicitly set:

```bash
export UNIVERSAL_MATRIX_OPERATOR_PASSWORD="choose-a-strong-local-password"
```

The operator token endpoint is:

```text
POST /api/v1/auth/operator-token
```

Hardware/control HTTP routes require bearer authorization.

The multi-tenant compatibility token endpoint remains separate:

```text
POST /api/v1/auth/token
```

## 6. Hardware safety

Do not connect experimental software outputs directly to hazardous physical hardware without an independent safety controller.

In particular:

- CNC,
- high voltage,
- RF transmitters,
- PEMF hardware,
- robotics,
- CAN buses,
- laser systems,
- swarm controllers

must have hardware-level interlocks independent of this repository.

A passing unit test is not a hardware safety certification.

## 7. Scientific experiments

The old repository instructions for hard-coded photon delays, exact speed-of-light derivation, 3/6/9 interferometer predictions, and General Relativity replacement have been superseded.

Current validation rules are in:

`docs/physics_proofs/falsifiable_predictions.md`

A physical benchmark should specify:

1. observable,
2. units,
3. initial conditions,
4. boundary conditions,
5. independently fixed parameters,
6. numerical convergence/error,
7. uncertainty,
8. predeclared falsification threshold.

## 8. Dispersion work

The current derived lattice relation is implemented in:

`src/gauge_dispersion.py`

It predicts a dimensionless lattice dispersion once (eta) and the discrete geometry are specified.

The repository does not currently derive the SI value of the speed of light.

## 9. Theory comparisons

Use:

`docs/comparative_theory_bridge_audit_v0.1.md`

for string, M-theory, LQG, causal-set, holographic/tensor-network, and lattice-gauge comparisons.

The theory bridge is deliberately conservative about equivalence claims.

## 10. Repository audit

The current technical migration backlog is recorded in:

`docs/repository_audit_2026-09.md`

That file should be consulted before extending older modules because many retain historical terminology or assumptions.
