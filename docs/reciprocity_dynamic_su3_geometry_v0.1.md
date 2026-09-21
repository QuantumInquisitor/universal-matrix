# Dynamic SU(3) Reciprocity Geometry v0.1

## Purpose

The repository already contains dynamic SU(2) gauge fields coupled to the
reciprocity geometry scalar.

This extension closes the corresponding SU(3) gap.

Implementation:

`src/reciprocity_dynamic_su3_geometry.py`

Tests:

`tests/test_reciprocity_dynamic_su3_geometry.py`

## 1. Combined Hamiltonian

[
H
=
H_psi
+
H_{SU(3)}[psi].
]

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

The SU(3) sector is

[
H_{SU(3)}
=
rac12
sum_{ell}
w_ell
E_ell^aE_ell^a
+
eta
sum_p
w_p
left[
1-rac13operatorname{ReTr}U_p
ight].
]

## 2. Geometry weights

Link weight:

[
w_ell
=
e^{-2arpsi_ell}.
]

Plaquette weight:

[
w_p
=
e^{-2arpsi_p}.
]

These are the same gauge-invariant scalar weights already used by the generic
SU(N) reciprocity geometry module.

## 3. Geometry source

The scalar momentum equation contains

[
oxed{
S_psi(x)
=
-rac{partial H_{SU(3)}}{partialpsi(x)}.
}
]

The exact lattice identity remains

[
oxed{
sum_x S_psi(x)
=
2H_{SU(3)}.
}
]

This is verified in the tests.

## 4. Gauge-coordinate drift

The left-electric link evolution becomes

[
oxed{
U_ell
ightarrow
exp
left[
iDelta t,
w_ell
E_ell^aT_a
ight]
U_ell.
}
]

Therefore the local reciprocity geometry scales the gauge propagation rate
without changing the internal SU(3) transformation law.

## 5. Weighted magnetic force

For a target link, each forward and backward staple carries the plaquette
weight of its own face.

The analytic force is

[
oxed{
F_ell^a
=
-rac{eta}{3}
operatorname{ImTr}
left[
T_aU_ell K_ell^{(psi)}
ight].
}
]

The test suite compares this directly with a slow symmetric finite-difference
variation along all eight SU(3) Lie-algebra directions.

## 6. Constant-geometry limit

When

[
psi=0,
]

all weights reduce to one and the Hamiltonian returns to the previously tested
unweighted SU(3) lattice Hamiltonian.

## 7. Numerical integration

The reference evolution uses a symmetric sequence:

1. geometry half-kick;
2. SU(3) electric half-kick;
3. geometry coordinate drift;
4. weighted group-valued link drift;
5. second electric half-kick;
6. second geometry half-kick.

Small-step tests monitor total energy.

## 8. What this closes

The repository now has dynamical reciprocity-geometry backreaction for:

- U(1);
- SU(2);
- SU(3).

That means the three current gauge sectors all have a route for sourcing and
responding to the same geometry scalar.

## 9. Remaining gaps

The major next gaps are now:

- dynamical matter + SU(3) + reciprocity geometry in one engine;
- chiral fermions and anomaly constraints;
- a time-dependent curved-space spin connection;
- second quantization / genuine quantum state space;
- derivation of dimensional scales from the canonical kernel;
- direct confrontation of the strong-field reciprocity predictions with data.

## Status

Dynamic SU(3) reciprocity backreaction is now implemented as a classical
lattice Hamiltonian extension and verified against exact group finite
differences.
