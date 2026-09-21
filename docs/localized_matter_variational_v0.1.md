# Localized Classical Matter Candidates v0.1

## Purpose

This extension asks whether the nonlinear matter sector can support localized
finite-charge configurations before assigning any real particle name.

Implementation:

`src/localized_matter_variational.py`

Tests:

`tests/test_localized_matter_variational.py`

## 1. Time-harmonic ansatz

Use

[
Phi(t,r)
=
e^{iomega t}f(r)
]

with a Gaussian trial profile

[
f(r)
=
A
e^{-r^2/(2R^2)}.
]

This is a classical variational ansatz.

## 2. Matter potential

The search uses

[
U(f)
=
m^2f^2
+
lambda_4f^4
+
lambda_6f^6
]

with

[
lambda_6>0.
]

A representative attractive/interacting choice used in the tests is

[
m^2=1,
qquad
lambda_4=-2,
qquad
lambda_6=1.
]

## 3. Analytic Gaussian integrals

In three dimensions,

[
I_2
=
A^2pi^{3/2}R^3,
]

[
I_{
abla}
=
rac32
A^2pi^{3/2}R,
]

[
I_4
=
rac{
A^4pi^{3/2}R^3
}{
2^{3/2}
},
]

and

[
I_6
=
rac{
A^6pi^{3/2}R^3
}{
3^{3/2}
}.
]

The classical U(1) charge is

[
Q
=
2omega I_2.
]

The energy is

[
E
=
omega^2I_2
+
I_
abla
+
m^2I_2
+
lambda_4I_4
+
lambda_6I_6.
]

## 4. Localization diagnostic

A useful classical energetic diagnostic is

[
oxed{
rac{E}{Q}
<
m_{m free}
}
]

where

[
m_{m free}=sqrt{m^2}.
]

The deterministic scan contains trial configurations satisfying this
inequality.

That means the nonlinear field has candidate localized states whose energy per
charge lies below the free-field threshold in this variational approximation.

## 5. What this does not prove

It does not yet establish:

- an exact nonlinear solution;
- dynamical stability;
- quantum stability;
- spin;
- fermionic statistics;
- any Standard Model particle identity.

Those require additional equations and tests.

## 6. Next step

The next matter calculation should solve the nonlinear radial field equation
rather than restricting the profile to a Gaussian.

The variational candidate provides initial data and parameter ranges for that
solver.

## Status

The repository now contains a concrete classical localized-matter candidate
sector rather than a particle analogy.


## 7. Nonlinear-solver update

A subsequent boundary-value calculation solves the radial Euler-Lagrange
equation directly.

Representative converged nonlinear solutions can have

[
E/Q>m_{m free}.
]

Therefore the Gaussian (E/Q<m_{m free}) configurations are search
heuristics only and must not be cited as proof of a stable localized matter
state.

See:

`docs/radial_matter_solver_v0.1.md`
