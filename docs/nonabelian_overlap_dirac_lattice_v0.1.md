# Fundamental SU(2)/SU(3) Overlap Fermions v0.1

## Purpose

This extension generalizes the repository's compact-U(1) overlap-Dirac
correctness reference to fundamental non-Abelian gauge links.

Implementation:

`src/nonabelian_overlap_dirac_lattice.py`

Tests:

`tests/test_nonabelian_overlap_dirac_lattice.py`

The same dense small-lattice construction supports both SU(2) doublets and
SU(3) triplets.

## 1. Four-dimensional Euclidean links

The overlap construction remains a four-dimensional Euclidean reference.

For color dimension (N_c),

[
U_mu(x)in SU(N_c).
]

The local gauge transformation is exactly the convention already used
throughout the repository:

[
oxed{
U_mu(x)
ightarrow
G(x)
U_mu(x)
G^dagger(x+hatmu).
}
]

The new module simply extends that convention to the four Euclidean directions
required by the overlap operator.

## 2. Spin-color Wilson kernel

The site field lives in

[
mathbb C^4_{m spin}
otimes
mathbb C^{N_c}_{m color}.
]

The Wilson kernel is

[
D_W(x,y)
=
4r,delta_{xy}
-
rac12
sum_mu
left[
(r-gamma_mu)
otimes
U_mu(x)
,
delta_{x+hatmu,y}
+
(r+gamma_mu)
otimes
U_mu^dagger(x-hatmu)
,
delta_{x-hatmu,y}
ight].
]

The implementation uses explicit spin-color Kronecker products so the gamma
matrices act only on spin and the gauge links act only on color.

## 3. Hermitian Wilson kernel

Define

[
Gamma_5
=
I_{m sites}
otimes
gamma_5
otimes
I_{N_c},
]

and

[
oxed{
H_W
=
Gamma_5
(D_W-ho I).
}
]

The tests verify Hermiticity for both SU(2) and SU(3) identity backgrounds.

## 4. Overlap operator

For an admissible kernel,

[
oxed{
D_{m ov}
=
ho
left[
I+
Gamma_5,operatorname{sign}(H_W)
ight].
}
]

The same exact Hermitian matrix-sign routine used by the U(1) reference is
reused here.

## 5. Ginsparg-Wilson relation

The non-Abelian overlap operator satisfies

[
oxed{
Gamma_5 D
+
DGamma_5
=
rac1ho
DGamma_5 D.
}
]

The tests verify this independently for

[
N_c=2
]

and

[
N_c=3.
]

## 6. Gamma5 Hermiticity

The implementation also verifies

[
oxed{
D^dagger
=
Gamma_5
D
Gamma_5.
}
]

This is required for the overlap/Ginsparg-Wilson chiral structure.

## 7. Exact non-Abelian gauge covariance

A lattice gauge transformation acts on the spin-color site space as

[
mathcal G
=
igoplus_x
left(
I_4otimes G(x)
ight).
]

The overlap operator obeys

[
oxed{
D[U^G]
=
mathcal G
D[U]
mathcal G^dagger.
}
]

The tests verify this for random local SU(2) and SU(3) transformations applied
to spectrally safe pure-gauge backgrounds.

## 8. Free zero modes

For the free overlap operator, the color space simply multiplies the physical
spin zero-mode degeneracy.

The tests verify

[
4	imes2=8
]

zero modes for the SU(2) doublet reference and

[
4	imes3=12
]

for the SU(3) triplet reference on the small free test lattice.

No extra naive doublers appear.

## 9. What this closes

The repository now has overlap/Ginsparg-Wilson fermions for:

- compact U(1);
- fundamental SU(2);
- fundamental SU(3).

All three have tested:

- Wilson kernels;
- Hermitian overlap kernels;
- exact lattice gauge covariance;
- gamma5 Hermiticity;
- Ginsparg-Wilson chirality.

This closes the earlier purely algebraic gap labelled "SU(2)/SU(3) overlap
fermion extensions."

## 10. What remains open

This does not yet provide:

1. a combined SU(2)×U(1) chiral electroweak fermion representation;
2. simultaneous SU(3)×SU(2)×U(1) multiplets;
3. non-Abelian Weyl measure curvature and holonomy;
4. local non-Abelian anomaly densities;
5. SU(2) global anomaly diagnostics;
6. representation-level Standard Model anomaly cancellation;
7. second-quantized fermion dynamics;
8. continuum-limit renormalization.

## Status

The project now contains mathematically consistent small-lattice fundamental
SU(2) and SU(3) overlap-fermion reference operators.

They are gauge-covariant chiral lattice building blocks, not yet a completed
non-Abelian chiral quantum field theory.
