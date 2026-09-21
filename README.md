# Universal Matrix

**Author:** Malakhiyah  
**Status:** mathematical kernel v0.4 with experimental physical extensions

Universal Matrix is a research codebase built around a finite discrete kernel with a 108-state core, six external boundary orientations, and a 64-address projection. The repository also contains experimental gauge, polarity, source, and multi-scale adapters that are intentionally separated from the proven finite kernel.

The project does **not** currently claim an experimental replacement for General Relativity, quantum mechanics, string theory, M-theory, or Maxwell electromagnetism. Physical adapters are research hypotheses whose value depends on independent parameter identification and experimental testing.

## Canonical mathematical kernel

The executable authority is:

- `src/canonical_kernel.py`
- `tests/test_canonical_kernel.py`
- `docs/canonical_spec_v0.4.md`

The canonical architecture is

[
mathcal A=mathbb Z_{108}sqcup B_6
]

with

[
B_6={+X,-X,+Y,-Y,+Z,-Z}.
]

Important exact operators include:

[
E=T_9,qquad P=T_{54},qquad F(n)=107-n,
]

and the canonical routing convention

[
T=T_{21}
]

selected from the synchronized class

[
{21,57,93}
]

by the minimal-positive-lift convention.

The register projection is

[
pi(n)=7nmod64.
]

The 64-address register is a **64-state / 6-bit-style address layer where explicitly modeled as binary channels**, not a 64-bit physical spacetime claim.

## Experimental physical stack

The current experimental stack is layered so assumptions remain visible.

### Nested polarity dynamics

`src/nested_polarity_dynamics.py`

Explores polarity reversal, signed routing, phase evolution, self-similar scale layers, and conservative inter-layer exchange.

### Gauge theory bridge

`src/gauge_dynamics.py`  
`src/gauge_hamiltonian.py`  
`src/gauge_dispersion.py`

Implements compact U(1) link variables, Wilson-loop/plaquette structure, Hamiltonian evolution, Gauss constraints, and weak-field lattice dispersion.

### 3D and open-boundary field adapters

`src/gauge_3d.py`  
`src/open_gauge_dynamics.py`  
`src/open_boundary_solver.py`

The newest default physical adapter uses an open cubical discrete-exterior-calculus complex tied to the six signed boundary orientations. It supports open finite-volume Gauss solves, nonzero enclosed charge, and a matrix-free projected PCG solver.

### Source sectors

`src/polarity_sources.py`  
`src/open_polarity_sources.py`  
`src/source_channels.py`  
`src/source_interaction.py`

These distinguish:

- polarization-induced electric source,
- free electric charge,
- six-gate boundary exchange,
- compact U(1) topological magnetic defects.

Electric and topological magnetic source channels are not conflated.

### Unified engine

`src/unified_engine.py`

Synchronizes source continuity, open gauge evolution, six-gate flux accounting, Gauss projection, and topological diagnostics.

## Comparative theory adapters

`src/theory_bridge.py`

The repository contains mathematically limited bridges to structures used in:

- compact-mode / Kaluza-Klein-style Fourier decompositions,
- lattice gauge theory,
- causal histories,
- scale-network / tensor-network analogies,
- loop-quantum-gravity graph substrates,
- string/M-theory comparisons.

These adapters do not assert equivalence to the external theories. See:

`docs/comparative_theory_bridge_audit_v0.1.md`

## Scientific status

### Established inside the project

The following are finite mathematical or software results once the stated definitions are accepted:

- canonical (mathbb Z_{108}) operator identities,
- routing-cycle structure,
- 64-address projection/carry relations,
- mixed-radix decomposition,
- U(1) gauge invariance of the implemented link/plaquette system,
- discrete-exterior-calculus identity (d_1d_0=0),
- source continuity identities,
- open finite-volume Gauss compatibility,
- weak-field lattice dispersion.

### Experimental / unestablished

The following remain hypotheses or adapters:

- identification of Matrix layers with physical toroidal fields,
- interpretation of polarity as a measured physical quantity,
- mapping Matrix phase rate to physical clock frequency,
- mapping lattice units to SI distance/time/field strength,
- physical meaning of amplitude variables,
- identification with biological, chakra, meridian, consciousness, black-hole, or white-hole structures,
- physical replacement of General Relativity or quantum mechanics.

## Modern development workflow

The project uses `pyproject.toml` as the authoritative dependency/tool configuration.

Recommended development setup:

```bash
uv sync --group dev --extra scientific
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```

Property-based invariant tests are in:

`tests/test_property_invariants.py`

CI tests Python 3.12 and 3.14 for the canonical/open engine and keeps a Python 3.12 full-suite compatibility job for legacy modules.

## API security

`src/api_server.py` no longer ships hard-coded API credentials.

Set credentials with:

```bash
export UNIVERSAL_MATRIX_API_KEYS="your-secret-key:RESEARCH"
```

Optional allowed CORS origins:

```bash
export UNIVERSAL_MATRIX_CORS_ORIGINS="https://example.org"
```

Wildcard credentialed CORS is intentionally rejected.

## Documentation

Start with:

- `white_paper.md`
- `docs/canonical_spec_v0.4.md`
- `docs/physical_extension_v0.1.md`
- `docs/gauge_dynamics_v0.1.md`
- `docs/gauge_hamiltonian_v0.1.md`
- `docs/gauge_dispersion_v0.1.md`
- `docs/gauge_3d_v0.1.md`
- `docs/open_boundary_solver_v0.1.md`
- `docs/unified_engine_v0.1.md`

The repository keeps one authoritative white paper at `white_paper.md`. Technical notes in `docs/` document individual subsystems and should be read as supporting material. Where prose conflicts with the canonical specification or executable tests, the canonical specification and current tests take precedence.

## Repository policy

New physical claims should provide:

1. a precise mathematical definition,
2. units or a dimensionless observable,
3. independently fixed parameters,
4. an executable prediction,
5. uncertainty/error handling,
6. a falsification condition,
7. comparison with existing measurements or theories.

Calibration to a known result must be labeled as calibration, not derivation.
