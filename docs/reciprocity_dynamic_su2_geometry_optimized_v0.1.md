# Optimized Dynamic Reciprocity Geometry + SU(2) v0.1

## Purpose

The reference dynamic geometry-SU(2) engine computes the weighted magnetic
force by exact group finite differences.

This extension derives the analytic geometry-weighted staple force and checks
it directly against that oracle.

Implementation:

`src/reciprocity_dynamic_su2_geometry_optimized.py`

Tests:

`tests/test_reciprocity_dynamic_su2_geometry_optimized.py`

Reference:

`src/reciprocity_dynamic_su2_geometry.py`

## 1. Weighted staple

For a target link

[
U_mu(x),
]

each plaquette touching the link contributes its ordinary SU(2) staple
multiplied by that plaquette's reciprocity weight.

The weighted staple sum is

[
oxed{
K_mu^{(psi)}(x)
=
sum_{
u
emu}
left[
w_p(x;mu,
u)K_{m forward}
+
w_p(x-hat
u;mu,
u)K_{m backward}
ight].
}
]

## 2. Analytic force

The weighted Wilson contribution containing the target link is

[
V_{m link}
=
	ext{constant}
-
rac{eta}{2}
operatorname{ReTr}
left[
U_mu K_mu^{(psi)}
ight].
]

Under

[
U_mu
	o
e^{iepsilon T_a}U_mu,
]

the electric force is

[
oxed{
F_mu^a
=
-rac{eta}{2}
operatorname{ImTr}
left[
T_a
U_mu
K_mu^{(psi)}
ight].
}
]

## 3. Reference verification

The test suite compares the analytic force on random spatially varying
(psi) configurations against the reference definition

[
F_mu^a
=
-
rac{
H_B(e^{+iepsilon T_a}U_mu)
-
H_B(e^{-iepsilon T_a}U_mu)
}{
2epsilon
}.
]

The two force fields must agree pointwise.

## 4. Dynamic equations

The optimized system retains the same geometry equations as the reference:

[
dotpsi
=
kappa e^{-4psi}P_psi,
]

[
dot P_psi
=
rac1kappa
abla^2psi
+
2kappa e^{-4psi}P_psi^2
+
S_{SU(2)}.
]

Gauge drift remains

[
dot U_ell
=
i w_ell E_ell U_ell.
]

Only the expensive magnetic force calculation has been replaced.

## 5. Energy test

A small coupled geometry-SU(2) evolution is evolved for many steps and the
combined Hamiltonian drift is monitored.

This is a numerical integration check, not a proof of long-time symplectic
accuracy.

## Status

Spatially varying reciprocity geometry and dynamical SU(2) now have both a
finite-difference correctness oracle and an analytic weighted-staple
implementation.
