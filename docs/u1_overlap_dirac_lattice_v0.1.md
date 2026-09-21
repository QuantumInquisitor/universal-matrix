# Gauge-Covariant U(1) Overlap Dirac Lattice v0.1

## Purpose

The free overlap reference establishes exact Ginsparg-Wilson chirality but does
not test local gauge coupling.

This extension constructs the overlap operator on a finite periodic 4D lattice
with compact U(1) links.

Implementation:

`src/u1_overlap_dirac_lattice.py`

Tests:

`tests/test_u1_overlap_dirac_lattice.py`

## 1. Gauge-covariant Wilson kernel

The massless Wilson kernel is

[
D_W(x,y)
=
4r,delta_{xy}
-
rac12
sum_mu
left[
(r-gamma_mu)
U_mu(x)delta_{x+hatmu,y}
+
(r+gamma_mu)
U_mu^dagger(x-hatmu)
delta_{x-hatmu,y}
ight].
]

For zero gauge field this reduces to

[
D_W(p)
=
isum_mu
gamma_musin p_mu
+
rsum_mu
(1-cos p_mu).
]

## 2. Hermitian Wilson operator

Define

[
oxed{
H_W
=
Gamma_5
(D_W-ho)
}
]

where (Gamma_5) acts as (gamma_5) independently at every lattice site.

The implementation verifies

[
H_W^dagger=H_W.
]

## 3. Matrix sign function

For the small-lattice correctness implementation,

[
H_W
=
VLambda V^dagger
]

is diagonalized directly and

[
operatorname{sign}(H_W)
=
Voperatorname{sign}(Lambda)V^dagger.
]

Configurations whose Hermitian Wilson kernel contains an eigenvalue too close
to zero are rejected as spectrally inadmissible for this reference
implementation.

## 4. Overlap operator

[
oxed{
D_{m ov}
=
ho
left[
I+
Gamma_5operatorname{sign}(H_W)
ight].
}
]

## 5. Ginsparg-Wilson relation

The finite-lattice operator satisfies

[
oxed{
Gamma_5D
+
DGamma_5
=
rac1ho
DGamma_5D.
}
]

The complete dense matrix residual is checked numerically.

## 6. Local U(1) covariance

Under

[
psi(x)	o e^{ialpha(x)}psi(x)
]

and

[
A_mu(x)
	o
A_mu(x)
+
alpha(x)
-
alpha(x+hatmu),
]

the site-spinor gauge matrix (G) gives

[
oxed{
D_{m ov}[A^alpha]
=
G
D_{m ov}[A]
G^dagger.
}
]

The tests verify this for random weak compact gauge backgrounds.

## 7. Gamma5 Hermiticity

[
oxed{
D_{m ov}^dagger
=
Gamma_5D_{m ov}Gamma_5.
}
]

This remains true in the gauge background.

## 8. Free zero-mode count

On a periodic

[
2^4
]

lattice with zero gauge field, the overlap operator has one physical lattice
momentum zero,

[
p=0,
]

times four spin components.

The dense singular-value test therefore finds exactly

[
oxed{
4
}
]

zero singular values rather than the naive doubled set.

## 9. Why this matters

The repository now has a chiral lattice fermion operator that simultaneously
has:

- local compact U(1) gauge covariance;
- doubler removal;
- Ginsparg-Wilson chirality;
- gamma5 Hermiticity.

This is a substantially stronger fermion foundation than a Wilson-only
single-particle operator.

## 10. Remaining chiral gaps

A physical chiral gauge theory still requires:

- chiral projectors and Weyl determinants;
- anomaly calculation;
- anomaly cancellation across the full matter representation;
- SU(2) and SU(3) overlap coupling;
- locality bounds under admissible gauge fields;
- reciprocity-geometry coupling;
- second quantization.

## Status

The project now contains a finite-lattice compact-U(1) overlap-fermion
correctness implementation.
