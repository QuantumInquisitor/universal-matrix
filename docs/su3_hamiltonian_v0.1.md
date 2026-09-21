# SU(3) Hamiltonian Gauge Dynamics v0.1

## Purpose

The SU(3) sector previously had exact static Wilson geometry and a classical
triplet matter representation, but no electric Hamiltonian dynamics.

This extension adds the non-Abelian electric sector.

Implementation:

`src/su3_hamiltonian.py`

Tests:

`tests/test_su3_hamiltonian.py`

## 1. Canonical variables

Each link carries

[
U_i(x)in SU(3)
]

and an eight-component left-electric momentum

[
E_i(x)
=
E_i^a(x)T_a,
qquad
a=1,dots,8.
]

The generators are

[
T_a=rac{lambda_a}{2}
]

with (lambda_a) the Gell-Mann matrices.

## 2. Hamiltonian

[
oxed{
H
=
rac12
sum_{m links,a}
(E_i^a)^2
+
eta
sum_p
left[
1-rac13operatorname{ReTr}U_p
ight].
}
]

## 3. Exact group drift

[
dot U_i=iE_iU_i.
]

The finite step is

[
oxed{
U_i
	o
e^{iDelta t E_i}
U_i.
}
]

The matrix exponential is evaluated on the traceless Hermitian algebra matrix,
so the drift remains in SU(3) up to numerical precision.

## 4. Analytic Wilson force

For staple sum (K_i(x)),

[
oxed{
F_i^a
=
-rac{eta}{3}
operatorname{ImTr}
left[
T_aU_iK_i
ight].
}
]

The factor (1/3) follows from the normalized SU(3) Wilson action.

## 5. Force oracle

A slow reference force is retained inside the module for small-lattice
verification.

Each link is perturbed along an exact SU(3) group direction:

[
U_i
	o
e^{pm iepsilon T_a}U_i.
]

The resulting finite-difference force is compared directly with the analytic
staple force.

## 6. Non-Abelian Gauss generator

At each site,

[
oxed{
G(x)
=
sum_i
left[
E_i(x)
-
U_i^dagger(x-hat i)
E_i(x-hat i)
U_i(x-hat i)
ight].
}
]

The incoming electric matrix is parallel transported into the destination
site's algebra frame before subtraction.

## 7. Verification

Tests cover:

- SU(3) preservation under group drift;
- analytic/reference force agreement;
- zero covariant divergence of the pure gauge force;
- Gauss preservation from source-free initial data;
- small energy drift under leapfrog evolution.

## 8. Current non-Abelian status

The repository now has dynamical Hamiltonian sectors for both

[
SU(2)
]

and

[
SU(3).
]

The remaining non-Abelian gap is no longer pure gauge dynamics.

It is matter backreaction:

- SU(2) doublet current and Gauss source;
- SU(3) triplet current and Gauss source;
- coupled matter-gauge energy conservation.

## Status

SU(3) now has an executable non-Abelian Hamiltonian electric sector with
group-preserving evolution and Gauss constraint.
