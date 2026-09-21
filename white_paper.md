# The Universal Matrix

## Canonical Finite Architecture, Reciprocity Field Dynamics, and Chiral Lattice Extensions

**Malakhiyah**  
*Working Mathematical and Physical Preprint, Version 0.5*  
*Waters Legacy Trust Research Program*  
*September 2026*

---

## Abstract

The Universal Matrix is a finite mathematical architecture built from a 108-state cyclic core together with six external oriented boundary gates,

[
oxed{
mathcal A=mathbb Z_{108}sqcup B_6
}
]

with

[
B_6={+X,-X,+Y,-Y,+Z,-Z}.
]

The canonical kernel contains exact routing, polarity, reflection, projection, and boundary-symmetry identities. Its principal operators are the order-12 interface translation (E=T_9), the polarity involution (P=T_{54}), the reflection (F(n)=107-n), and a selected routing translation (T=T_{21}) chosen from the synchronized class ({21,57,93}) by a minimal-positive-lift convention. A 64-address projection is defined on canonical core representatives by

[
pi(n)=7nmod 64.
]

Above this finite kernel, the repository contains an explicitly experimental physical stack. It includes alternating nested polarity dynamics, conservative scale transfer, a reciprocity metric and scalar-geometry action, compact U(1) and non-Abelian SU(2)/SU(3) lattice gauge sectors, dynamical matter backreaction, curved-background Dirac evolution, semiclassical Dirac geometry backreaction, overlap/Ginsparg-Wilson chiral fermions, Weyl projector curvature and holonomy, finite Weyl determinants, charged U(1) anomaly diagnostics, fundamental non-Abelian overlap fermions, product-group (SU(3)	imes SU(2)	imes U(1)) anomaly bookkeeping, and product-representation overlap operators.

The purpose of this paper is to state the current architecture cleanly while preserving a strict separation between exact finite mathematics, consequences derived from stated continuum or lattice assumptions, computational verification, and physical hypotheses requiring independent experiment. The repository does not yet derive the observed dimensional constants, the Standard Model spectrum, a complete renormalized second-quantized theory, or a unique emergence of the reciprocity premises from the finite kernel.

---

# Part I. Canonical Finite Architecture

## 1. Status Conventions

Every statement in this paper belongs to one of four categories.

**Exact finite result.** A theorem or exhaustive consequence of the canonical finite definitions.

**Model-derived result.** A consequence of an explicitly stated metric, action, Hamiltonian, or lattice operator.

**Numerically verified result.** A property checked by the executable reference implementation and regression tests.

**Physical hypothesis.** A proposed identification with nature that requires independent empirical validation.

The canonical kernel is not permitted to inherit assumptions from later physical extensions. Likewise, success of a numerical field model does not retroactively prove that the finite kernel uniquely implies that field model.

---

## 2. Core and Boundary

The internal routing space is

[
C=mathbb Z_{108}.
]

The six boundary orientations are separate:

[
B_6={pm e_x,pm e_y,pm e_z}.
]

The full labeled architecture therefore contains 114 positions, but the cyclic routing algebra is (mathbb Z_{108}), not (mathbb Z_{114}).

This distinction is foundational.

### 2.1 Boundary symmetry

The six oriented directions form the vertices of an octahedral configuration. Signed permutations of the three coordinate axes give

[
|G_B|=2^3,3!=48.
]

Thus the full abstract boundary symmetry is the three-dimensional hyperoctahedral group,

[
G_Bcong C_2^3times S_3.
]

The number 48 follows directly from the six-direction geometry.

---

## 3. Canonical Translations

For any integer (d),

[
T_d(n)=n+dpmod{108}.
]

Translations obey

[
T_aT_b=T_{a+b},
qquad
T_d^{-1}=T_{-d}.
]

### 3.1 Interface translation

Define

[
oxed{E=T_9}.
]

Since

[
rac{108}{gcd(108,9)}=12,
]

the operator has order 12:

[
oxed{E^{12}=I}.
]

### 3.2 Polarity translation

Define

[
oxed{P=T_{54}}.
]

Then

[
P^2=I
]

and

[
oxed{E^6=P}.
]

The polarity map has no fixed core state. It partitions the 108-state core into exactly 54 unordered antipodal pairs,

[
{n,n+54}.
]

The algebraic pairing is exact. Physical language such as inward and outward is an interpretation layered on top of it.

---

## 4. Routing Structure

A routing translation (T_t) is constrained by three requirements:

1. it preserves the three residue classes modulo 3;
2. each residue class forms one 36-state routing cycle;
3. three routing steps equal seven interface steps,

[
T^3=E^7.
]

Because

[
E^7=T_{63},
]

the synchronization condition is

[
3tequiv63pmod{108}.
]

The positive synchronized solutions below 108 are

[
oxed{
tin{21,57,93}.
}
]

Therefore (t=21) is not a uniqueness theorem.

The reference architecture adopts the smallest positive representative,

[
oxed{T=T_{21}},
]

as a canonical convention.

For this selected lift,

[
gcd(21,108)=3,
]

so there are exactly three routing cycles of length 36.

The exact identities are

[
oxed{
T^{36}=I,
}
]

[
oxed{
T^3=E^7,
}
]

and

[
oxed{
T^{18}=E^6=P.
}
]

The inverse routing operator is

[
T^{-1}=T_{87}.
]

---

## 5. Routing Winding

One selected routing step advances through the cyclic core by

[
rac{21}{108}=rac{7}{36}
]

of a full turn.

Its angular representation is

[
	heta=rac{2pi(21)}{108}
=rac{7pi}{18}
=70^circ.
]

A complete 36-step routing cycle therefore accumulates

[
36(70^circ)=2520^circ
=7(360^circ).
]

Thus the selected routing orbit has seven angular windings before closure.

This winding number is exact for the chosen angular representation. It is not automatically identical to unrelated sevenfold structures in physics, biology, symbolism, or spiritual systems.

---

## 6. The 64-Address Projection

For canonical representatives (0le n<108), define

[
oxed{
pi(n)=7nmod64.
}
]

Because

[
gcd(7,64)=1,
]

multiplication by 7 permutes the 64 register addresses.

The map is defined on canonical representatives. It is not a group homomorphism from (mathbb Z_{108}) to (mathbb Z_{64}).

### 6.1 Interface displacement

A nonwrapping (+9) interface step gives

[
7(9)=63equiv-1pmod{64}.
]

Thus the interface step corresponds locally to one reverse register displacement.

### 6.2 Carry theorem

For (0le d<108), define

[
w_d(n)=
egin{cases}
1,&nge108-d,\
0,&n<108-d.
end{cases}
]

Then

[
T_d(n)=n+d-108w_d(n).
]

Applying the register projection gives

[
oxed{
Deltapi
equiv
7d+12w_d(n)
pmod{64}.
}
]

The reference implementation checks this identity exhaustively over the finite state space.

### 6.3 Register multiplicities

Two canonical core states share a register address exactly when

[
nequiv mpmod{64}.
]

Within (0,ldots,107), the repeated pairs are

[
(n,n+64),
qquad
0le nle43.
]

Therefore there are

[
oxed{44	ext{ double-hit addresses}}
]

and

[
oxed{20	ext{ single-hit addresses}}.
]

No register address has three core representatives.

---

## 7. Reflection Symmetry

Define

[
oxed{
F(n)=107-npmod{108}.
}
]

Then

[
F^2=I
]

and, for every translation,

[
FT_dF=T_{-d}.
]

In particular,

[
FTF=T^{-1},
qquad
FEF=E^{-1},
qquad
FP=PF.
]

These relations give a dihedral-type reversal structure for the routing subsystem.

---

## 8. Mixed-Radix Coordinates

Every canonical core state can be written uniquely as

[
oxed{
n=r+3q+9s+27u
}
]

with

[
r,q,sin{0,1,2},
qquad
uin{0,1,2,3}.
]

Thus

[
108=3cdot3cdot3cdot4.
]

This is a mixed-radix coordinate representation. It does not imply a direct-product group isomorphism.

A coarser coordinate system is

[
n=a+9b,
]

with

[
ain{0,ldots,8},
qquad
bin{0,ldots,11}.
]

In these coordinates,

[
pi(n)=7a-bpmod{64}.
]

---

## 9. Six Binary Boundary Channels

If each of the six oriented boundary gates is assigned an independent binary state,

[
b_iin{0,1},
]

then the boundary microstate space is

[
{0,1}^6
]

with

[
2^6=64
]

possible states.

This is a six-bit, 64-state boundary register model. It is not a 64-bit spacetime claim.

If the opposite directions on each spatial axis are instead reduced to a ternary resultant,

[
-1,0,+1,
]

the three-axis resultant space contains

[
3^3=27
]

states.

The two constructions are distinct.

---

# Part II. Experimental Dynamical Extensions

## 10. Canonical Polarity Clock and Nested Scale Dynamics

Because

[
T^{36}=I
]

and

[
T^{18}=P,
]

the canonical routing cycle defines a natural phase increment

[
oxed{
Deltaphi_P
=
rac{2pi}{36}
=
rac{pi}{18}.
}
]

The current nested-scale hypothesis assigns alternating orientation,

[
oxed{
epsilon_ell=(-1)^ell.
}
]

The corresponding polarity and transfer carriers are

[
p_ell(phi)
=
epsilon_ellcosphi
]

and

[
s_ell(phi)
=
epsilon_ellsinphi.
]

For a linear adjacent-scale exchange conserving

[
mathcal C
=
a_ell^2+a_{ell+1}^2,
]

the generator must be skew-symmetric and therefore exponentiates to a rotation.

The current canonical-locked transfer candidate is

[
oxed{
delta_ell(phi)
=
(-1)^ell
rac{pi}{18}
sinphi.
}
]

This model has zero inter-scale transfer at polarity extrema and maximum transfer at neutral crossings.

The alternating orientation rule and the identification of the maximum transfer angle with (pi/18) remain physical-model hypotheses rather than theorems of the finite kernel.

---

## 11. Reciprocity Geometry

The current gravity-like correspondence is based on four explicit premises:

1. six-gate spatial isotropy;
2. additive scalar-potential composition;
3. clock factor (N=e^{-psi});
4. local clock-space causal reciprocity.

Under those assumptions,

[
S=e^psi
]

and the isotropic line element becomes

[
oxed{
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}dmathbf x^2.
}
]

This metric is conditionally derived from the stated reciprocity premises. The premises themselves have not yet been uniquely derived from (mathbb Z_{108}sqcup B_6).

### 11.1 Self-consistent scalar geometry

A common action now determines matter evolution and the geometry-scalar equation.

The geometry source is tied to stress-energy rather than an independently assigned composition-dependent charge. In the current formulation, the relevant source combination is

[
T^{00}+T^{11}+T^{22}+T^{33}.
]

For stationary isolated systems satisfying the von Laue condition,

[
int T^{ij},d^3x=0,
]

the integrated active source reduces to total energy,

[
oxed{
M_{m active}=E_{m total}.
}
]

This is a model-derived universality statement for the complete stationary isolated system.

### 11.2 Static vacuum exterior

In the current scalar action, static spherical vacuum obeys

[

abla^2psi=0.
]

Asymptotic flatness gives

[
oxed{
psi=rac{mu}{r}.
}
]

The resulting reciprocity exterior is not Ricci-flat. Its scalar curvature is

[
oxed{
R
=
-rac{2mu^2}{r^4}e^{-2mu/r}.
}
]

Thus this model is not simply Einstein vacuum written in unusual coordinates.

### 11.3 Newton normalization and unresolved scale

The weak-field normalization gives

[
oxed{
kappa
=
rac{4pi G}{c_*^4}
}
]

for the current action convention.

The numerical value of (G) is still externally calibrated. It has not been derived from the finite kernel.

### 11.4 Distinguishing predictions

At first post-Newtonian order, the current reciprocity exterior gives

[
eta=gamma=1.
]

At the next spatial order, the current isotropic convention gives

[
oxed{
delta_{m reciprocity}=rac43,
}
]

rather than the GR value 1.

The model's second-order light-deflection expansion is

[
oxed{
alpha_{m reciprocity}
=
4rac{mu}{b}
+
4pi
left(rac{mu}{b}ight)^2
+cdots.
}
]

The current circular-orbit calculation gives

[
oxed{
r_{m ISCO}
=
(3+sqrt5)mu.
}
]

These are model predictions that create possible empirical discrimination. They are not yet experimental confirmations.

---

## 12. Gauge and Matter Sectors

The repository contains compact U(1), SU(2), and SU(3) lattice gauge constructions.

Implemented structures include:

- link variables;
- plaquettes and Wilson actions;
- electric-field Hamiltonian dynamics;
- Gauss constraints;
- group-valued link evolution;
- analytic staple forces checked against finite-difference oracles;
- fundamental matter coupling;
- gauge-field and matter backreaction;
- reciprocity-geometry weighting.

For the non-Abelian sectors, the local gauge rule is

[
oxed{
U_mu(x)
ightarrow
G(x)U_mu(x)G^dagger(x+hatmu).
}
]

The current reciprocity coupling assigns geometry-dependent weights to link and plaquette energies while preserving local gauge invariance.

For the implemented gauge sectors, the characteristic propagation speed on the reciprocity background matches the geometry/null-cone speed,

[
oxed{
c_{m gauge}
=
c_psi
=
c_{m null}
=
e^{-2psi}
}
]

in the coordinate convention used by the model.

---

## 13. Dirac Sector and Geometry Backreaction

For static isotropic reciprocity geometry, the rescaled Dirac Hamiltonian is

[
oxed{
H_D
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

The anticommutator form contains the geometry-gradient contribution required for Hermiticity.

For time-dependent geometry, the local rescaling

[
chi=e^{3psi/2}Psi
]

removes the temporal volume-dilution term in the chosen representation.

### 13.1 Analytic geometry source

The local source obtained from the Dirac energy is

[
oxed{
S_psi(x)
=
m e^{-psi}
operatorname{Re}
left(
chi^daggeretachi
ight)
+
2e^{-2psi}
sum_i
operatorname{Re}
left(
chi^daggeralpha_i p_ichi
ight).
}
]

The implementation verifies this analytic expression against an independent finite-difference derivative of the lattice energy.

### 13.2 Coupled semiclassical backreaction

The current one-particle backreaction model uses

[
H_{m total}
=
H_{m geometry}
+
operatorname{Re}
langlechi|H_D[psi]|chiangle.
]

Thus

[
idotchi
=
H_D[psi]chi
]

and the same Hamiltonian drives the geometry source.

This closes the one-particle semiclassical feedback loop. It is not yet a second-quantized fermion theory.

---

# Part III. Chiral Lattice Program

## 14. Overlap and Ginsparg-Wilson Fermions

The repository contains overlap-Dirac reference operators for compact U(1), fundamental SU(2), and fundamental SU(3) gauge backgrounds.

The overlap operator satisfies

[
oxed{
Gamma_5D+DGamma_5
=
rac1ho
DGamma_5D
}
]

and

[
oxed{
D^dagger
=
Gamma_5DGamma_5.
}
]

The modified chirality operator is

[
oxed{
widehatGamma_5
=
Gamma_5
left(
I-rac{D}{ho}
ight)
}
]

with

[
widehatGamma_5^2=I.
]

Therefore the exact finite-lattice chiral projectors are

[
oxed{
widehat P_pm
=
rac12
left(
IpmwidehatGamma_5
ight).
}
]

The overlap index is represented by

[
oxed{
operatorname{index}(D)
=
operatorname{Tr}
left[
Gamma_5
left(
I-rac{D}{2ho}
ight)
ight].
}
]

---

## 15. Weyl Measure Geometry

A Weyl basis (V) spans the image of one modified chiral projector,

[
V^dagger V=I,
qquad
VV^dagger=widehat P.
]

The basis itself is not unique. Internal rotations (V	o VU) leave the physical subspace unchanged.

### 15.1 Projector curvature

For a smooth family of gauge backgrounds, the basis-independent projector curvature is

[
oxed{
mathcal F_{ab}
=
i,operatorname{Tr}
left[
P
left(
partial_aP,partial_bP
-
partial_bP,partial_aP
ight)
ight].
}
]

### 15.2 Discrete holonomy

Between neighboring Weyl frames, the unitary polar factor of the frame overlap defines discrete parallel transport.

The product around a closed loop gives a holonomy (mathcal H), and

[
oxed{
Theta_{m loop}
=
argdetmathcal H
}
]

is invariant under arbitrary internal Weyl-basis rotations.

Small-loop tests verify agreement between the local projector curvature and the closed-loop holonomy phase in the shrinking-loop limit.

### 15.3 Weyl determinant

For a modified Weyl basis (V) and the opposite ordinary barred chiral basis (overline V), the finite Weyl block is

[
oxed{
M
=
overline V^dagger D V.
}
]

Under internal frame rotations,

[
V	o VU,
qquad
overline V	ooverline V,overline U,
]

the determinant transforms as

[
oxed{
det M
	o
det(overline U)^*
det M
det(U).
}
]

Therefore (|det M|) is basis independent, while its phase requires a fermion-measure prescription.

---

## 16. Charged U(1) Index and Gauge-Orbit Measure

For a U(1) fermion of charge (q), the overlap kernel sees the compact phase (qA_mu).

The local overlap index density is

[
oxed{
q_{m index}(x)
=
operatorname{tr}_{m spin}
left[
gamma_5
left(
I-rac{D_q}{2ho}
ight)
ight]_{x,x}.
}
]

Its lattice sum reproduces the overlap index.

The repository also constructs a basis-independent Weyl measure holonomy along a gauge orbit. The endpoint is identified with the start through the exact charge-(q) site gauge transformation.

The resulting determinant phase is an infinitesimal chiral-measure response diagnostic.

It is not yet equated with the complete consistent anomaly, because the full measure prescription and barred-sector contribution must be treated consistently.

---

## 17. Non-Abelian and Product-Group Overlap Fermions

The small-lattice overlap construction has been extended to matrix-valued fundamental links for SU(2) and SU(3).

For color dimension (N_c), the fermion lives in

[
mathbb C^4_{m spin}
otimes
mathbb C^{N_c}_{m color}.
]

The implementation verifies:

- Hermiticity of the Wilson kernel;
- Ginsparg-Wilson chirality;
- (Gamma_5)-Hermiticity;
- exact local non-Abelian gauge covariance;
- the expected free color-multiplied physical zero-mode degeneracy.

The repository also contains a product-representation overlap operator for

[
oxed{
SU(3)	imes SU(2)	imes U(1).
}
]

For a multiplet with representations (R_3,R_2) and Abelian charge (Y), the internal link is

[
oxed{
U_{{m rep},mu}(x)
=
e^{iYA_mu(x)}
left[
R_3(U_{3,mu}(x))
otimes
R_2(U_{2,mu}(x))
ight].
}
]

Supported first-stage representations include SU(3) singlet, fundamental and antifundamental, together with SU(2) singlet and doublet.

This is a correctness layer for candidate chiral multiplets. It does not mean the Universal Matrix has derived the observed particle spectrum.

---

## 18. Product-Group Anomaly Ledger

For Weyl species with explicit handedness, color representation, weak representation, U(1) charge, and multiplicity, the repository computes the supported perturbative anomaly coefficients.

These include

[
oxed{
C_{SU(3)^3}
}
]

[
oxed{
C_{SU(3)^2U(1)}
}
]

[
oxed{
C_{SU(2)^2U(1)}
}
]

[
oxed{
C_{U(1)^3}
}
]

and

[
oxed{
C_{{m grav}^2U(1)}.
}
]

The SU(2) fundamental global mod-2 doublet condition is tracked separately.

A one-generation Standard Model representation set is included only as a known correspondence benchmark. The code verifies its familiar anomaly cancellations, but the spectrum and hypercharges are supplied externally.

This is a test target, not a derivation of the Standard Model from the finite Matrix kernel.

---

# Part IV. Verification and Scientific Status

## 19. Executable Authority

The canonical executable specification is centered on

`src/canonical_kernel.py`

with regression coverage in

`tests/test_canonical_kernel.py`.

The broader physical stack has dedicated tests for the gauge, geometry, Dirac, overlap, Weyl-measure, anomaly-ledger, and product-group layers.

At the branch state used for this revision, the repository passes:

- Universal Matrix Verification;
- Python 3.12 core tests;
- Python 3.14 core tests;
- the full legacy compatibility suite;
- the container pipeline;
- CodeQL security analysis.

The executable tests take precedence over descriptive prose if a conflict is discovered.

---

## 20. What Has Been Derived and What Has Not

### 20.1 Strongest established internal statements

The following are currently among the strongest internally established results:

- the exact (mathbb Z_{108}sqcup B_6) finite architecture;
- the routing, polarity, reflection, projection, carry, and collision identities;
- the order-48 boundary symmetry;
- conservative nested transfer under the stated alternating-scale model;
- local gauge invariance of U(1), SU(2), and SU(3) lattice constructions;
- self-consistent reciprocity scalar sourcing under the stated action;
- exact static spherical vacuum solution (psi=mu/r) within that model;
- one-particle Dirac geometry backreaction from a shared Hamiltonian;
- overlap/Ginsparg-Wilson chirality for U(1), SU(2), SU(3), and supported product representations;
- basis-independent Weyl projector curvature and holonomy diagnostics;
- explicit finite Weyl determinant basis-phase covariance;
- product-group perturbative anomaly bookkeeping and the supported SU(2) global parity condition.

### 20.2 Open derivations

The following remain unresolved:

1. derive the reciprocity premises uniquely from the canonical finite architecture;
2. derive the alternating nested-scale orientation rule rather than postulate it;
3. derive the absolute dimensional scale and measured couplings from the finite kernel;
4. derive the observed chiral representation spectrum and charge assignments;
5. construct a globally consistent lattice fermion measure in all supported gauge sectors;
6. complete local and global anomaly analysis beyond the current ledgers and diagnostics;
7. construct a genuine second-quantized interacting quantum theory;
8. establish continuum-limit renormalization and running couplings;
9. derive quantum measurement probabilities and state reduction, if those are to be part of the theory;
10. confront the reciprocity geometry's post-post-Newtonian and strong-field predictions with current observational constraints.

---

## 21. Empirical Program and Falsification

A physical extension is not considered established merely because it reproduces an already known result after parameter fitting.

A serious test requires:

1. a precisely defined observable;
2. a dimensional map from lattice or Matrix variables to measured units;
3. independently fixed parameters;
4. initial and boundary conditions;
5. a numerical prediction made before comparison;
6. an uncertainty budget;
7. a falsification criterion;
8. comparison with the appropriate established theory and experiment.

The reciprocity geometry is especially suitable for discrimination because it agrees with familiar weak-field parameters at first post-Newtonian order while differing at higher order and in strong-field behavior.

The chiral lattice sector is similarly falsifiable internally: inconsistent gauge covariance, Ginsparg-Wilson violation, nonunitary Weyl transport, failed anomaly cancellation for a proposed spectrum, or lack of a consistent continuum limit would invalidate the corresponding extension.

---

# Conclusion

The Universal Matrix now has two clearly separated layers.

The first is an exact finite mathematical kernel,

[
oxed{
mathcal A
=
mathbb Z_{108}
sqcup
B_6,
}
]

with exact routing, polarity, reflection, projection, carry, collision, mixed-radix, and boundary-symmetry structure.

The second is a growing experimental dynamical program built on top of that kernel. It now reaches from alternating polarity and conservative scale transfer through reciprocity geometry, Abelian and non-Abelian gauge dynamics, matter and Dirac backreaction, overlap chiral fermions, Weyl measure geometry, anomaly bookkeeping, and product-group overlap representations.

The most important scientific distinction remains unchanged:

[
oxed{
	ext{internal mathematical consistency}

eq
	ext{experimental confirmation}.
}
]

The repository is therefore best understood as a progressively constrained research architecture. Its value will ultimately depend on whether the currently assumed physical bridges can themselves be derived from the finite kernel and whether the resulting independently fixed predictions survive experimental comparison.
