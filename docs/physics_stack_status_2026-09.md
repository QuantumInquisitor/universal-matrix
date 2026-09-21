# Universal Matrix Physics Stack Status — September 2026

## Purpose

The repository now contains several distinct layers of mathematics and physics
prototypes. This document prevents those layers from being conflated.

Status labels:

- **CANONICAL** — exact finite mathematics fixed by the v0.4 kernel.
- **DERIVED-CLASSICAL** — follows from an explicitly stated classical action,
  Hamiltonian, symmetry, or variational principle.
- **NUMERICALLY VERIFIED** — tested computationally against exact identities,
  conservation laws, manufactured solutions, or finite-difference derivatives.
- **CORRESPONDENCE BRIDGE** — standard external physics reproduced as a target
  or comparison, not derived from the Matrix kernel.
- **EXPERIMENTAL HYPOTHESIS** — internally coherent proposed physical
  interpretation not yet externally validated.
- **OPEN** — required structure not yet derived.

---

## 1. Canonical finite kernel

Status: **CANONICAL**

Primary modules:

- `src/canonical_kernel.py`
- `src/canonical_polarity_clock.py`

Core results:

[
mathbb Z_{108}sqcup B_6
]

[
E=T_9,
qquad
P=T_{54},
qquad
T=T_{21}
]

[
T^{18}=P,
qquad
T^{36}=I
]

[
Deltaphi_P=pi/18
]

per canonical routing tick.

---

## 2. Polarity / scale hierarchy

Status: **EXPERIMENTAL HYPOTHESIS + NUMERICALLY VERIFIED INTERNAL CONSERVATION**

Modules:

- `src/polarity_oscillator.py`
- `src/phase_roles.py`
- `src/scale_transfer.py`
- `src/nested_oscillatory_hierarchy.py`

Key ideas:

- polarity clock phase is separate from U(1) gauge phase;
- neutral crossings drive inter-scale transfer;
- transfer is an orthogonal rotation;
- global quadratic scale content is conserved.

---

## 3. Abelian U(1) gauge sector

Status: **DERIVED-CLASSICAL + NUMERICALLY VERIFIED**

Modules:

- `src/gauge_dynamics.py`
- `src/gauge_hamiltonian.py`
- `src/gauge_3d.py`
- `src/open_gauge_dynamics.py`
- `src/fully_coupled_compact_fields.py`

Capabilities:

- compact Wilson action;
- weak-field linearization;
- periodic and open DEC formulations;
- Gauss constraints;
- compact topological magnetic diagnostics;
- full classical matter/content/gauge backreaction.

---

## 4. Content scalar / gravity-like correspondence

Status: **EXPERIMENTAL HYPOTHESIS + CORRESPONDENCE BRIDGE**

Modules:

- `src/content_clock.py`
- `src/content_potential_field.py`
- `src/content_wave_dynamics.py`
- `src/content_ray_propagation.py`
- `src/clock_space_reciprocity.py`
- `src/exponential_metric_strong_field.py`
- `src/reciprocity_backreaction_audit.py`

Current chain:

[
ho_{mathcal C}
	o
chi
	o
psi
	o
	ext{clock response}
	o
	ext{spatial response}
]

with

[
-
abla^2chi
=
kappa_{mathcal C}ho_{mathcal C}
]

and under the reciprocity postulate

[
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}dmathbf x^2.
]

Weak-field correspondence:

[
eta_{m PPN}=1,
qquad
gamma_{m PPN}=1.
]

Strong-field continuation remains experimental and differs from Schwarzschild.

---

## 5. Classical localized matter

Status: **DERIVED-CLASSICAL + ACTIVE NUMERICAL SEARCH**

Modules:

- `src/unified_variational_action.py`
- `src/localized_matter_variational.py`
- `src/radial_matter_solver.py`
- `src/matter_branch_scan.py`
- `src/classical_matter_dynamics.py`
- `src/localized_matter_persistence.py`
- `src/matter_content_source_bridge.py`
- `src/coupled_matter_content_dynamics.py`
- `src/fully_coupled_classical_fields.py`
- `src/fully_coupled_compact_fields.py`

Current state:

- nonlinear localized solutions can be solved;
- energetic stability is not automatic;
- source charge per energy is not automatically universal;
- real-time survival tests are now possible.

No real particle identity has been assigned.

---

## 6. SU(2) non-Abelian sector

Status: **DERIVED-CLASSICAL MATHEMATICAL GAUGE PROTOTYPE**

Modules:

- `src/su2_lattice_gauge.py`
- `src/su2_matter_doublet.py`

Capabilities:

- exact SU(2) links;
- local gauge transformations;
- plaquettes;
- Wilson action;
- classical doublet matter;
- covariant hopping energy.

Not yet:

- electroweak theory;
- chiral fermions;
- W/Z dynamics.

---

## 7. SU(3) non-Abelian sector

Status: **DERIVED-CLASSICAL MATHEMATICAL GAUGE PROTOTYPE**

Modules:

- `src/su3_lattice_gauge.py`
- `src/su3_matter_triplet.py`

Capabilities:

- exact SU(3) links;
- local gauge transformations;
- Wilson action;
- classical triplet matter.

Not yet:

- QCD;
- confinement;
- quarks;
- hadrons;
- running coupling.

---

## 8. Electroweak bridge

Status: **CORRESPONDENCE BRIDGE**

Module:

- `src/electroweak_mass_bridge.py`

Reproduces the standard tree-level reference identities:

[
m_W=gv/2
]

[
m_Z=vsqrt{g^2+g'^2}/2
]

[
m_W=m_Zcos	heta_W
]

with one massless photon direction.

These are targets, not Matrix derivations.

---

## 9. Fermion lattice correctness

Status: **CORRESPONDENCE BRIDGE + NUMERICALLY VERIFIED**

Modules:

- `src/wilson_dirac_reference.py`
- `src/u1_wilson_dirac_lattice.py`

Capabilities:

- demonstrates naive 3D spatial fermion doubling;
- Wilson term lifts the doublers;
- U(1)-gauge-covariant Wilson-Dirac operator;
- local gauge covariance;
- Hermiticity.

Not yet:

- second quantization;
- chiral Standard Model fermions;
- anomaly cancellation;
- physical spin/statistics derivation.

---

## 10. External experimental constraints

Status: **REQUIRED FOR PHYSICAL CLAIMS**

Document:

- `docs/real_world_constraint_ledger_v0.1.md`

Current constraints include:

- GW170817 causal-speed bound;
- MICROSCOPE weak equivalence-principle bound;
- Cassini PPN gamma;
- EHT strong-field image/shadow tests.

---

## 11. Highest-priority open derivations

### OPEN A — self-consistent geometry action

Need one action whose variation determines both

[
psi
]

and its effective geometry rather than assigning the exponential metric after
the fact.

### OPEN B — universal matter source

Need to derive why stable matter should satisfy an effectively universal

[
Q_{mathcal C}/E.
]

### OPEN C — stable matter branch

Need a converged nodeless nonlinear matter branch with demonstrated long-time
stability.

### OPEN D — non-Abelian dynamics

Need dynamical SU(2) and SU(3) electric sectors, Gauss constraints, and matter
backreaction.

### OPEN E — chiral fermions

Need a lattice formulation compatible with chiral gauge structure and anomaly
constraints.

### OPEN F — quantum theory

Need an actual quantum state space, Born probabilities, entanglement, Bell
correlations, and measurement framework.

### OPEN G — dimensional scale

Need to derive or independently determine physical length, time, energy, and
charge scales.

---

## 12. Current strongest statement

The project now contains a broad internally tested **classical discrete field
architecture** with:

- a fixed finite kernel;
- Abelian and non-Abelian gauge prototypes;
- nonlinear matter;
- reciprocal scalar interactions;
- compact gauge backreaction;
- lattice fermion correctness tools;
- explicit experimental constraint tracking.

It does not yet constitute a complete experimentally validated fundamental
theory.

That distinction should remain explicit in all future public materials.
