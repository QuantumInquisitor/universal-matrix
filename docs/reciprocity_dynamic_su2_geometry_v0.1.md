# Dynamic Reciprocity Geometry + SU(2) Reference v0.1

## Purpose

Previous layers established:

- a dynamical reciprocity scalar;
- dynamical SU(2);
- spatially varying gauge-invariant geometry weights.

This extension closes the loop so the geometry scalar and SU(2) field
backreact on one another.

Implementation:

`src/reciprocity_dynamic_su2_geometry.py`

Tests:

`tests/test_reciprocity_dynamic_su2_geometry.py`

## 1. Combined Hamiltonian

The geometry sector is

[
H_psi
=
sum_x
left[
rac{kappa}{2}
e^{-4psi}
P_psi^2
+
rac{|
ablapsi|^2}{2kappa}
ight].
]

The SU(2) sector is

[
H_{SU(2)}
=
rac12
sum_ell
w_ell
E_ell^aE_ell^a
+
eta
sum_p
w_p
left[
1-rac12operatorname{ReTr}U_p
ight].
]

The total reference Hamiltonian is

[
oxed{
H=H_psi+H_{SU(2)}.
}
]

## 2. Geometry equations

[
oxed{
dotpsi
=
kappa e^{-4psi}P_psi
}
]

and

[
oxed{
dot P_psi
=
rac1kappa
abla^2psi
+
2kappa e^{-4psi}P_psi^2
+
S_{SU(2)}(x).
}
]

The gauge source is

[
S_{SU(2)}(x)
=
-rac{partial H_{SU(2)}}{partialpsi(x)}.
]

That source is the same exact site-deposition rule verified independently by
the spatial-geometry module.

## 3. Geometry-dependent link drift

Because the electric kinetic energy is

[
rac12w_ell E_ell^2,
]

Hamilton's equation for the group coordinate is

[
oxed{
dot U_ell
=
i,w_ell E_ell,U_ell.
}
]

The finite reference drift is

[
U_ell
	o
exp(
iDelta t,w_ell E_ell
)
U_ell.
]

## 4. Weighted magnetic force

The magnetic force is

[
dot E_ell^a
=
-
rac{partial H_B}{partial q_ell^a}.
]

This reference implementation evaluates the derivative directly with exact
left SU(2) group perturbations:

[
U_ell
	o
e^{pm iepsilon T_a}U_ell.
]

That is intentionally slower than a weighted analytic staple expression.

## 5. Verification

Tests verify:

- geometry momentum receives the exact previously derived SU(2) source;
- weighted magnetic force matches the group derivative of the weighted Wilson
  energy;
- the zero geometry/zero gauge state is exactly stationary;
- a small coupled geometry-gauge evolution has small total-energy drift.

## 6. Why this is a reference engine

The present purpose is mathematical verification.

The next optimized implementation should derive the weighted staple force
analytically and compare it directly against this group finite-difference
oracle.

That mirrors the successful workflow already used for flat-background SU(2).

## Status

The repository now contains a dynamical reference system in which reciprocity
geometry and a non-Abelian SU(2) gauge field mutually backreact through one
Hamiltonian.
