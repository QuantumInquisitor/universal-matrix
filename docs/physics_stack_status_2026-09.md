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


---

## 13. September 21 update — reciprocity action and source universality

The gravity-like sector has advanced beyond the earlier status summary.

### Self-consistent scalar-geometry action

A common action now determines:

- complex scalar matter dynamics;
- the geometry-scalar equation;
- the stress-energy source of the geometry scalar.

The source is

[
ho+p_x+p_y+p_z
]

rather than an independently assigned matter charge.

### Stationary scalar source universality

For exact stationary localized time-harmonic scalar solutions,

[
G+3(V-K)=0
]

implies

[
oxed{
M_{m active}=E.
}
]

Equivalently,

[
M_{m active}-E
=
-Delta_{m virial}.
]

Thus integrated gravitational/source universality follows automatically for
this solution class when the virial equation is satisfied.

### Exact static spherical vacuum exterior

For the proposed scalar action,

[
dotpsi=0,
qquad
S_m=0
]

implies exactly

[

abla^2psi=0.
]

Spherical symmetry and asymptotic flatness give

[
oxed{
psi=mu/r.
}
]

Therefore the exponential static exterior is now derived within the proposed
action rather than treated only as a strong-field extrapolation.

### Updated highest-priority open problems

The primary remaining gravity-side questions are now:

1. derive the reciprocity premises themselves from the finite canonical kernel;
2. extend source-universality analysis to fermions, gauge-bound states, and
   non-Abelian composites;
3. confront the exact static exterior with strong-field observations;
4. derive the dimensional coupling (kappa) rather than calibrating it from
   measured (G).


---

## 14. September 21 update — action-level gravity/gauge unification

### Reciprocity metric conditional uniqueness

The exponential metric is now conditionally derived from explicit premises:

1. full six-gate spatial isotropy;
2. additive scalar-potential composition;
3. clock factor (N=e^{-psi});
4. local causal-speed reciprocity.

Together these imply

[
S=e^psi
]

and therefore

[
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}dmathbf x^2.
]

### Self-consistent matter + geometry-scalar action

A common action now gives both the matter equation and geometry-scalar equation.

The geometry source is

[
T^{00}+T^{11}+T^{22}+T^{33}.
]

For stationary isolated systems, stress-energy conservation plus the von Laue
condition gives

[
oxed{
M_{m active}=E.
}
]

Thus integrated source universality is no longer restricted to the scalar
soliton sector.

### Newton normalization

The weak Newton limit fixes

[
oxed{
kappa
=
rac{4pi G}{c_*^4}
}
]

for the current scalar-action convention.

The measured numerical value of (G) is still an external calibration, not a
kernel derivation.

### Exact static exterior

The static spherical vacuum equation is exactly

[

abla^2psi=0,
]

so

[
psi=mu/r
]

is the exact exterior solution within the proposed scalar action.

### Gauge fields on the reciprocity geometry

U(1) and generic Yang-Mills actions now give the same coordinate characteristic
speed as the geometry scalar and metric null cone:

[
oxed{
c_{m U(1)}
=
c_{m YM}
=
c_psi
=
c_{m null}
=
e^{-2psi}.
}
]

### Exact geometric difference from GR vacuum

The reciprocity exterior is not Ricci-flat:

[
R
=
-rac{2mu^2}{r^4}e^{-2mu/r}.
]

Thus

[
	ext{reciprocity scalar vacuum}

eq
	ext{Einstein vacuum}.
]

### Higher-order weak-field signature

The first-post-Newtonian parameters still satisfy

[
eta=gamma=1.
]

Using the isotropic 2PN spatial convention,

[
oxed{
delta_{m reciprocity}
=
rac43,
qquad
delta_{m GR}=1.
}
]

### Second-order light deflection

[
oxed{
alpha_{m reciprocity}
=
4rac{mu}{b}
+
4pi
left(
rac{mu}{b}
ight)^2
+cdots
}
]

versus

[
oxed{
alpha_{m GR}
=
4rac{mu}{b}
+
rac{15pi}{4}
left(
rac{mu}{b}
ight)^2
+cdots.
}
]

### Circular orbits and ISCO

[
oxed{
r_{m ISCO}
=
(3+sqrt5)mu
}
]

with

[
oxed{
R_{m ISCO}
approx
6.337940264856347,mu
}
]

and

[
oxed{
Omega_{m ISCO}mu
approx
0.06333263135.
}
]

These are direct strong-field predictions of the current reciprocity exterior.

### Updated central open questions

1. derive the reciprocity premises from the finite canonical kernel;
2. derive the dimensional coupling rather than calibrating it from (G);
3. extend the evolving reciprocity geometry into the fully coupled lattice
   matter + U(1) + SU(2) + SU(3) engines;
4. construct a consistent chiral fermion sector;
5. compare the 2PN, second-order lensing, ISCO, and strong-field predictions
   against current observations;
6. construct a genuine quantum theory rather than a classical field analogue.


---

## September 21 expansion checkpoint

The following layers have now been added after the original status map and pass
the repository verification stack together.

### Self-consistent reciprocity source

Status: **DERIVED-CLASSICAL + NUMERICALLY VERIFIED**

Modules:

- `src/self_consistent_reciprocity_action.py`
- `src/scalar_virial_source_universality.py`
- `src/stationary_source_universality.py`
- `src/reciprocity_unified_geometry_source.py`

The geometry scalar now couples through the stress-energy combination

[
sqrt{-g}
left(
T^{00}+T^{11}+T^{22}+T^{33}
ight).
]

For stationary localized isolated composites satisfying the von Laue condition,

[
int T^{ij}d^3x=0,
]

the integrated active source becomes

[
oxed{
M_{m active}=E_{m total}.
}
]

This includes matter, gauge-field energy, interaction energy, and binding
stress when the complete system is used.

### Static reciprocity Dirac sector

Status: **DERIVED-CORRESPONDENCE + NUMERICALLY VERIFIED**

Modules:

- `src/reciprocity_dirac_constant_background.py`
- `src/reciprocity_dirac_static_background.py`

For static isotropic reciprocity geometry,

[
H
=
eta_D m e^{-psi}
+
rac12
left{
oldsymbolalphacdotmathbf p,
e^{-2psi}
ight}.
]

The position-space discretization is Hermitian and contains the required
geometry-gradient/spin-connection contribution.

### Dynamical SU(2)

Status: **DERIVED-CLASSICAL + NUMERICALLY VERIFIED**

Modules:

- `src/su2_hamiltonian_reference.py`
- `src/su2_hamiltonian.py`
- `src/su2_matter_gauge_dynamics.py`

Capabilities now include:

- exact group-valued link drift;
- analytic Wilson staple force;
- finite-difference group-force oracle;
- non-Abelian electric field;
- Gauss constraint;
- classical fundamental matter backreaction;
- total Hamiltonian energy tests.

### Dynamical SU(3)

Status: **DERIVED-CLASSICAL + NUMERICALLY VERIFIED**

Modules:

- `src/su3_hamiltonian.py`
- `src/su3_matter_gauge_dynamics.py`

Capabilities now include:

- exact SU(3) group drift;
- eight-component electric algebra;
- analytic Wilson staple force;
- group finite-difference oracle;
- non-Abelian Gauss constraint;
- triplet matter backreaction;
- energy and local gauge-invariance tests.

### Reciprocity coupling of non-Abelian sectors

Status: **DERIVED-CORRESPONDENCE + NUMERICALLY VERIFIED**

Modules:

- `src/reciprocity_nonabelian_constant_geometry.py`
- `src/reciprocity_nonabelian_spatial_geometry.py`

For uniform geometry,

[
H_{m YM}(psi)
=
e^{-2psi}H_{m YM}(0).
]

For spatially varying geometry, gauge-invariant link and plaquette weights are

[
w_ell
=
e^{-2arpsi_ell},
qquad
w_p
=
e^{-2arpsi_p}.
]

The local geometry source satisfies the exact lattice identity

[
oxed{
sum_x S_psi(x)=2H_{m YM}.
}
]

### Current verification state

At this checkpoint the same branch head passes:

- Universal Matrix Verification;
- Python 3.12 core;
- Python 3.14 core;
- full legacy compatibility suite;
- container pipeline;
- CodeQL.

### Revised highest-priority open problems

The highest-priority gaps are now:

1. fully dynamical (psi) backreaction with spatially weighted SU(2)/SU(3);
2. time-dependent curved-space spin connection;
3. chiral fermion construction and anomaly constraints;
4. second quantization and genuine quantum state space;
5. derivation of the absolute dimensional scale rather than calibration;
6. experimental discrimination of the reciprocity geometry from GR in
   post-post-Newtonian and strong-field regimes.


---

## September 21 continuation — SU(3) geometry, full Dirac background, and chiral lattice reference

### Dynamic SU(3) reciprocity geometry

Status: **DERIVED-CLASSICAL + NUMERICALLY VERIFIED**

Modules:

- `src/reciprocity_dynamic_su3_geometry.py`

The spatially weighted SU(3) Hamiltonian now evolves jointly with the reciprocity
geometry scalar.

The gauge Hamiltonian is

[
H_{SU(3)}
=
rac12sum_ell
w_ell E_ell^aE_ell^a
+
etasum_p
w_p
left[
1-rac13operatorname{ReTr}U_p
ight].
]

The local source satisfies

[
S_psi(x)
=
-rac{partial H_{SU(3)}}{partialpsi(x)}
]

and the exact lattice identity

[
oxed{
sum_x S_psi(x)=2H_{SU(3)}.
}
]

The analytic weighted SU(3) staple force is checked against group-direction
finite differences.

### Unified SU(3) matter + gauge + reciprocity geometry

Status: **DERIVED-CLASSICAL + NUMERICALLY VERIFIED**

Modules:

- `src/reciprocity_su3_matter_geometry.py`

The matter Hamiltonian on the reciprocity geometry is

[
H_{m matter}
=
e^{-4psi}|Pi|^2
+
|D_iPsi|^2
+
e^{2psi}V.
]

The geometry source is additive:

[
oxed{
S_psi^{m total}
=
S_psi^{m matter}
+
S_psi^{SU(3)}.
}
]

The matter term is

[
oxed{
S_psi^{m matter}
=
4e^{-4psi}|Pi|^2
-
2e^{2psi}V.
}
]

The implementation verifies this full source against a direct finite-difference
derivative of the non-geometry Hamiltonian.

### Time-dependent and full prescribed reciprocity Dirac propagation

Status: **DERIVED-CORRESPONDENCE + NUMERICALLY VERIFIED**

Modules:

- `src/reciprocity_dirac_time_background.py`
- `src/reciprocity_dirac_spacetime_background.py`

For homogeneous time dependence,

[
chi=e^{3psi/2}Psi
]

removes the temporal volume-dilution spin-connection term.

For general prescribed

[
psi=psi(t,mathbf x),
]

the rescaled spinor evolves with the instantaneous Hermitian operator

[
oxed{
H(t)
=
eta m e^{-psi}
+
rac12
left{
oldsymbolalphacdotmathbf p,
e^{-2psi}
ight}.
}
]

The spatial anticommutator contains the geometry-gradient connection term,
while the local (e^{3psi/2}) rescaling handles the temporal volume term.

The tests verify Hermiticity and norm conservation for genuinely
time-and-space-dependent prescribed geometry.

### Chiral lattice reference

Status: **CORRESPONDENCE + NUMERICALLY VERIFIED**

Modules:

- `src/overlap_dirac_reference.py`
- `src/u1_overlap_dirac_lattice.py`

The overlap operator satisfies

[
oxed{
gamma_5D+Dgamma_5
=
rac1ho Dgamma_5D
}
]

and

[
oxed{
D^dagger=gamma_5Dgamma_5.
}
]

The finite-lattice U(1) implementation is locally gauge covariant and retains
one physical zero-momentum mode rather than the naive doubled set.

### Revised highest-priority open problems

The next highest-priority gaps are now:

1. Dirac stress-energy backreaction into the dynamical reciprocity scalar;
2. chiral projectors, Weyl determinants, and anomaly accounting;
3. SU(2)/SU(3) overlap-fermion gauge coupling;
4. genuine second quantization and quantum state space;
5. derivation of the absolute dimensional scale and couplings from the finite
   kernel rather than experimental calibration;
6. observational testing of the post-post-Newtonian and strong-field
   reciprocity predictions.


---

## September 21 continuation — analytic and dynamical Dirac backreaction

### Analytic Dirac geometry source

Status: **DERIVED-CORRESPONDENCE + ORACLE-VERIFIED**

Modules:

- `src/reciprocity_dirac_geometry_source.py`
- `tests/test_reciprocity_dirac_geometry_source.py`

The local geometry source for the Hermitian reciprocity Dirac Hamiltonian now
has an explicit lattice form,

[
S_psi(x)
=
m e^{-psi(x)}
operatorname{Re}!left[
chi^dagger(x)etachi(x)
ight]
+
2e^{-2psi(x)}
sum_i
operatorname{Re}!left[
chi^dagger(x)alpha_i p_ichi(x)
ight].
]

This is the exact derivative of the existing finite-lattice Dirac energy with
respect to the local reciprocity scalar.

The prior finite-difference source remains in the repository as an independent
small-lattice oracle. Random nonuniform-field tests compare the analytic source
pointwise against that oracle.

### Coupled Dirac + reciprocity geometry dynamics

Status: **SEMICLASSICAL HAMILTONIAN PROTOTYPE**

Modules:

- `src/reciprocity_dirac_backreaction.py`
- `tests/test_reciprocity_dirac_backreaction.py`

The prescribed-background loop is now closed at the one-particle /
semiclassical level with

[
H_{m total}
=
H_{m geometry}
+
operatorname{Re}
langlechi|H_D[psi]|chiangle.
]

The coupled equations are

[
idotchi
=
H_D[psi]chi,
]

[
dotpsi
=
kappa e^{-4psi}P_psi,
]

and

[
dot P_psi
=
rac{
abla^2psi}{kappa}
+
2kappa e^{-4psi}P_psi^2
+
S_psi.
]

The same Hamiltonian therefore controls both the geometry acting on the spinor
and the spinor source acting back on the geometry.

The tests verify:

- correct source sign for a positive-energy rest spinor;
- vanishing Dirac source when the spinor is zero;
- spinor-norm conservation over short coupled evolutions;
- small total-Hamiltonian drift under RK4 evolution.

### Revised highest-priority open problems

The Dirac backreaction gap is no longer first on the list.

The current highest-priority gaps are now:

1. replace the one-particle semiclassical fermion source with a genuine
   second-quantized stress-energy expectation value;
2. construct chiral projectors, Weyl determinants, and anomaly accounting on
   the reciprocity-coupled lattice;
3. extend overlap/chiral fermions to SU(2) and SU(3) gauge backgrounds;
4. derive the absolute dimensional scale and couplings from the finite kernel
   instead of calibrating them from experiment;
5. derive the reciprocity premises themselves from the canonical
   (mathbb Z_{108}sqcup B_6) structure;
6. confront the 2PN, second-order lensing, ISCO, compact-object, and
   strong-field reciprocity predictions with current observational constraints.

The project remains a classical/semiclassical research architecture rather than
a complete quantum fundamental theory.


---

## September 21 continuation — Weyl measure geometry and determinant

### Ginsparg-Wilson chiral projectors

Status: **DERIVED-ALGEBRAIC + NUMERICALLY VERIFIED**

Modules:

- `src/ginsparg_wilson_chirality.py`
- `tests/test_ginsparg_wilson_chirality.py`

The overlap operator now feeds the exact modified chirality operator

[
\widehat{\gamma}_5
=
\gamma_5
\left(
I-\frac{D}{\rho}
\right),
]

with

[
\widehat{\gamma}_5^2=I.
]

This gives exact finite-lattice chiral projectors

[
\widehat P_\pm
=
\frac12
\left(
I\pm\widehat{\gamma}_5
\right).
]

The repository also computes the finite-lattice overlap index in the equivalent
forms

[
\operatorname{index}(D)
=
\operatorname{Tr}
\left[
\gamma_5
\left(
I-\frac{D}{2\rho}
\right)
\right]
=
\frac12
\operatorname{Tr}\widehat{\gamma}_5.
]

### Weyl projector-bundle curvature

Status: **DERIVED-GEOMETRIC + NUMERICALLY VERIFIED**

Modules:

- `src/weyl_measure_curvature.py`
- `tests/test_weyl_measure_curvature.py`

For a family of admissible gauge backgrounds, the modified Weyl projector
defines a vector bundle over gauge-field configuration space.

The local basis-independent curvature is

[
\boxed{
\mathcal F_{ab}
=
i\operatorname{Tr}
\left[
P
\left(
\partial_aP\,\partial_bP
-
\partial_bP\,\partial_aP
\right)
\right].
}
]

The implementation verifies gauge covariance of the Weyl subspace and gauge
invariance, antisymmetry, and numerical reality of this curvature diagnostic.

### Discrete Weyl holonomy

Status: **DERIVED-GEOMETRIC + NUMERICALLY VERIFIED**

Modules:

- `src/weyl_measure_holonomy.py`
- `tests/test_weyl_measure_holonomy.py`

Neighboring Weyl frames are connected through the unitary polar factor of their
overlap.

The closed-loop transport product

[
\mathcal H
=
Q_{0,N-1}\cdots Q_{2,1}Q_{1,0}
]

changes only by conjugation under arbitrary internal frame rotations.

Therefore

[
\boxed{
\Theta_{\rm loop}
=
\arg\det\mathcal H
}
]

is independent of arbitrary eigensolver basis choices.

The tests verify frame invariance, orientation reversal, unitarity, and the
contractible-loop limit.

### Curvature-holonomy consistency

Status: **NUMERICALLY VERIFIED**

Modules:

- `src/weyl_measure_stokes.py`
- `tests/test_weyl_measure_stokes.py`

For sufficiently small rectangular loops,

[
\boxed{
\Theta_{\rm loop}
\simeq
\mathcal F_{ab}
\,\Delta\lambda^a
\,\Delta\lambda^b.
}
]

The independently constructed differential curvature and discrete loop
holonomy agree in the shrinking-loop limit.

This supplies a finite-lattice Stokes consistency check for the chiral measure
geometry.

### Finite Weyl determinant

Status: **DERIVED-ALGEBRAIC + NUMERICALLY VERIFIED**

Modules:

- `src/weyl_determinant.py`
- `tests/test_weyl_determinant.py`

For a GW-modified Weyl basis (V) and opposite ordinary barred chiral basis
(overline V),

[
M
=
\overline V^\dagger D V.
]

Under internal basis rotations,

[
V\to VU,
\qquad
\overline V\to\overline V\overline U,
]

the finite Weyl block transforms as

[
M
\to
\overline U^\dagger M U.
]

Thus

[
|\det M|
]

is basis independent, while

[
\arg\det M
]

shifts by the internal basis determinant phases.

The code verifies this transformation law explicitly.

This makes the remaining measure problem precise rather than hiding it.

### Revised chiral frontier

The repository has now advanced through:

[
D_{\rm overlap}
\rightarrow
\widehat P_\pm
\rightarrow
\text{Weyl subspace}
\rightarrow
\mathcal F
\rightarrow
\mathcal H
\rightarrow
\det M.
]

The next genuinely unresolved chiral tasks are:

1. construct a globally consistent fermion-measure section over admissible
   gauge-field configuration space;
2. compute the infinitesimal gauge variation of that measure;
3. extract local anomaly coefficients;
4. test anomaly cancellation for complete chiral representation sets;
5. investigate global/topological anomalies;
6. extend the overlap/Weyl construction to SU(2) and SU(3).

No current repository result should yet be described as a completed anomaly-free
chiral gauge theory.
