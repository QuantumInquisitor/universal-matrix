# Universal Matrix Architecture

**Author:** Malakhiyah  
**Architecture status:** canonical kernel v0.4 plus experimental open-field extensions

This file describes the current software architecture. Historical cosmological and physical interpretations are not treated as canonical unless they are also defined in \`docs/canonical_spec_v0.4.md\` and exercised by tests.

## 1. Canonical layer

The canonical state architecture is

\[
\mathcal A=\mathbb Z_{108}\sqcup B_6.
\]

The six boundary orientations are

\[
B_6=\{+X,-X,+Y,-Y,+Z,-Z\}.
\]

They are external to the \(\mathbb Z_{108}\) routing core.

Primary operators:

\[
E=T_9,
\qquad
T=T_{21},
\qquad
P=T_{54},
\qquad
F(n)=107-n.
\]

Important exact relations include

\[
E^{12}=I,
\]

\[
T^{36}=I,
\]

\[
T^{18}=P,
\]

and

\[
P^2=I.
\]

The synchronized routing class satisfying the current algebraic synchronization condition is

\[
\{21,57,93\}.
\]

The canonical routing step \(21\) is selected by a minimal-positive-lift convention. It is not claimed as a uniqueness theorem.

The register projection is

\[
\pi(n)=7n\bmod64.
\]

Executable authority:

- \`src/canonical_kernel.py\`
- \`tests/test_canonical_kernel.py\`

## 2. Boundary symmetry layer

The six orientations form the signed three-axis set

\[
\{\pm e_x,\pm e_y,\pm e_z\}.
\]

Its abstract signed-permutation symmetry has order

\[
2^3 3!=48.
\]

The six external directions are used as the orientation scaffold for later 3D gauge adapters. This is an adapter construction, not proof that the finite kernel alone derives physical Euclidean space.

## 3. Nested polarity layer

The experimental layer state is

\[
X_\ell=(n_\ell,\sigma_\ell,\phi_\ell,A_\ell).
\]

The polarity-flip operator is

\[
Q(n,\sigma)=(n+54,-\sigma),
\]

so

\[
Q^2=I.
\]

Routing is polarity sensitive:

\[
\sigma=+1\Rightarrow T_{21},
\]

\[
\sigma=-1\Rightarrow T_{-21}.
\]

This layer also contains experimental self-similar scaling and conservative inter-layer exchange.

Implementation:

\`src/nested_polarity_dynamics.py\`

## 4. Gauge layer

The gauge bridge uses compact U(1) link variables

\[
U_{ij}=e^{i\theta_{ij}}.
\]

Gauge-invariant plaquette curvature is generated from oriented link sums.

The compact Wilson action is

\[
S_W
=
\beta
\sum_p
(1-\cos F_p).
\]

In the weak-field limit,

\[
S_W
\approx
\frac{\beta}{2}
\sum_pF_p^2.
\]

Implementation:

- \`src/gauge_dynamics.py\`
- \`src/gauge_hamiltonian.py\`
- \`src/gauge_dispersion.py\`

## 5. Open discrete-exterior-calculus field layer

The current default physical adapter uses an open cubical complex.

The cochain sequence is

\[
C^0\xrightarrow{d_0}C^1\xrightarrow{d_1}C^2
\]

with

\[
d_1d_0=0.
\]

The weak Hamiltonian is

\[
H
=
\frac12\langle E,E\rangle
+
\frac{\beta}{2}\langle d_1A,d_1A\rangle.
\]

The magnetic force is

\[
-\beta d_1^\ast d_1A.
\]

Implementation:

\`src/open_gauge_dynamics.py\`

## 6. Six-gate open Gauss layer

The open finite-volume field satisfies

\[
\nabla_{\rm open}\cdot E+b_{\partial V}=\rho.
\]

Global compatibility is

\[
\sum_x\rho(x)
=
\sum_{g\in B_6}\Phi_g^{E,\mathrm{outward}}.
\]

The scalar-potential solve uses a matrix-free Neumann Laplacian and projected preconditioned conjugate gradients.

Implementation:

\`src/open_boundary_solver.py\`

## 7. Source layer

The engine distinguishes four source mechanisms.

### 7.1 Polarization-induced source

\[
P=A\sigma\hat u,
\]

\[
\rho_{\rm pol}=-\nabla\cdot P.
\]

### 7.2 Free electric source

\[
\dot\rho_{\rm free}
+
\nabla\cdot J_{\rm free}
=
0.
\]

### 7.3 Six-gate boundary exchange

The internal total electric charge changes only through explicit boundary exchange:

\[
\Delta Q
=
\Delta t
\sum_{g\in B_6}\Phi_g.
\]

### 7.4 Topological magnetic source

Compact plaquette winding can generate integer-valued magnetic/topological defects.

These are kept separate from ordinary electric charge.

Implementations:

- \`src/polarity_sources.py\`
- \`src/open_polarity_sources.py\`
- \`src/source_channels.py\`
- \`src/source_interaction.py\`

## 8. Unified engine

\`src/unified_engine.py\` synchronizes:

\[
P,
\rho_{\rm pol},
\rho_{\rm free},
J,
E,
B,
B_6\text{ flux},
m_{\rm topo}.
\]

The default mode is \`boundary_mode="open"\`.

The legacy periodic mode exists only for comparison and regression compatibility.

## 9. Theory-bridge layer

\`src/theory_bridge.py\` contains optional mappings to mathematical structures used in other theories.

The strongest current bridges are:

- discrete Fourier modes on finite cycles,
- routing winding numbers,
- U(1) link variables and Wilson loops,
- time-unwrapped causal histories,
- multi-scale network adjacency.

M-theory, string theory, loop quantum gravity, and holography are not claimed as equivalent descriptions of the engine.

## 10. Legacy modules

Several older modules predate the v0.4 reconstruction and may contain terminology such as:

- SO(13) physical spacetime,
- 64-bit physical grid,
- fixed 3/6/9 physical control laws,
- M-theory/string/brane labels,
- toroidal physical geometry,
- geodesic or optical effects based on hand-authored potentials,
- biological/chakra/meridian mappings.

These should be treated as historical or visualization/experimental adapters unless they have been explicitly migrated to the current canonical/open-field stack.

No legacy module overrides \`src/canonical_kernel.py\` or the current canonical specification.

## 11. Verification hierarchy

The repository uses three levels of verification.

### Level A: exact finite identities

Deterministic algebraic tests for the canonical kernel.

### Level B: numerical structural invariants

Gauge invariance, DEC exactness, Gauss consistency, continuity, energy behavior, and solver residuals.

### Level C: physical validation

External experimental comparison with units, independently fixed parameters, uncertainties, and falsification criteria.

A result at Level A or B must not be presented as Level C evidence.

## 12. Software architecture

Authoritative project metadata:

\`pyproject.toml\`

Current developer workflow:

\`\`\`bash
uv sync --group dev --extra scientific
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
\`\`\`

CI runs the canonical/open engine on Python 3.12 and 3.14, with a separate compatibility run for the larger legacy dependency surface.

## 13. Authority order

When repository files disagree, use this order:

1. \`src/canonical_kernel.py\`
2. \`tests/test_canonical_kernel.py\`
3. \`docs/canonical_spec_v0.4.md\`
4. \`docs/white_paper.md\`
5. current experimental extension documents
6. legacy documentation and historical modules

This order prevents older speculative material from silently redefining the canonical mathematics.
