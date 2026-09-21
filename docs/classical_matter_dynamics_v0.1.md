# Classical Gauge-Covariant Matter Dynamics v0.1

## Purpose

The static variational matter sector can identify candidate field profiles, but
a persistent matter state must also survive time evolution.

This extension adds real-time classical complex-field dynamics in a fixed
compact U(1) spatial gauge background.

Implementation:

`src/classical_matter_dynamics.py`

Tests:

`tests/test_classical_matter_dynamics.py`

## 1. State

The dynamical variables are

[
Phi(mathbf x,t)inmathbb C
]

and its canonical velocity/momentum variable

[
Pi=partial_tPhi.
]

Spatial U(1) link phases are

[
A_i(mathbf x).
]

This first version uses temporal gauge

[
A_0=0.
]

## 2. Gauge-covariant lattice Laplacian

The discrete covariant Laplacian is

[
Delta_APhi(x)
=
sum_i
left[
e^{iA_i(x)}Phi(x+hat i)
+
e^{-iA_i(x-hat i)}
Phi(x-hat i)
-
2Phi(x)
ight].
]

## 3. Matter equation

For

[
U(ho)
=
m^2ho
+
lambda_4ho^2
+
lambda_6ho^3,
qquad
ho=|Phi|^2,
]

the real-time field equation is

[
oxed{
partial_t^2Phi
=
Delta_APhi
-
left[
m^2
+
2lambda_4|Phi|^2
+
3lambda_6|Phi|^4
ight]
Phi.
}
]

This is a classical nonlinear field equation.

## 4. Energy

The implemented conserved-energy candidate is

[
E
=
sum_x
left[
|Pi|^2
+
sum_i|D_i^+Phi|^2
+
U(|Phi|^2)
ight].
]

## 5. Classical U(1) charge

The charge convention is

[
oxed{
Q
=
2,mathrm{Im}
sum_x
Phi^*Pi.
}
]

This matches the positive

[
Q=2omegaint f^2d^3x
]

convention used by the time-harmonic radial solver.

## 6. Numerical integration

The field evolves using a kick-drift-kick / velocity-Verlet integrator.

The tests verify:

- gauge invariance of energy;
- gauge invariance of charge;
- approximate energy conservation for a small free mode;
- charge conservation to tight numerical tolerance;
- exact persistence of the zero solution.

## 7. Why this matters for matter identification

A candidate localized profile must eventually satisfy all of:

1. nonlinear field equation;
2. nodeless localized profile;
3. finite energy;
4. finite conserved U(1) charge;
5. energetic stability criterion;
6. long-time dynamical persistence.

The repository can now test items 1–5 separately and has the time-evolution
machinery needed for item 6.

## 8. Next matter experiment

The next direct test is to map a radial nonlinear solution onto a 3D lattice,
evolve it under this dynamical equation, and measure:

- charge drift;
- energy drift;
- core amplitude;
- radial width;
- radiated energy;
- survival time.

That will distinguish a true long-lived classical lump from a boundary-value
solution that rapidly disperses.

## Status

The matter sector now has both static nonlinear solutions and real-time
classical dynamics.
