# Nonlinear Radial Matter Solver v0.1

## Purpose

The Gaussian matter search provides only trial profiles.

This extension solves the radial Euler-Lagrange equation directly for a
time-harmonic classical complex field.

Implementation:

`src/radial_matter_solver.py`

Tests:

`tests/test_radial_matter_solver.py`

## 1. Matter ansatz

Use

[
Phi(t,r)=e^{iomega t}f(r).
]

For

[
U(f)
=
m^2f^2
+
lambda_4f^4
+
lambda_6f^6,
]

the radial equation is

[
oxed{
f''
+
rac2r f'
=
(m^2-omega^2)f
+
2lambda_4 f^3
+
3lambda_6 f^5.
}
]

The boundary conditions are approximated numerically as

[
f(0)=A_0,
qquad
f'(0)=0,
qquad
f(R_{max})=0.
]

The central amplitude is fixed while (omega) is solved as a boundary-value
parameter.

## 2. Energy and charge

For a converged profile,

[
Q
=
2omega
int f^2 d^3x,
]

and

[
E
=
int
left[
omega^2f^2
+
|
abla f|^2
+
U(f)
ight]
d^3x.
]

## 3. Stronger stability diagnostic

A localized nonlinear solution is not automatically stable against decay into
free field quanta.

The same threshold remains

[
oxed{
rac{E}{Q}<m_{m free}.
}
]

The representative converged solutions currently tested satisfy localization
and the field equation but can have

[
rac{E}{Q}>m_{m free}.
]

Therefore they are not automatically energetically stable.

## 4. Correction to the Gaussian interpretation

The earlier Gaussian variational scan found trial profiles with

[
E/Q<m_{m free}.
]

The nonlinear solver shows that this alone is insufficient.

A variational profile can look energetically favorable while not lying on the
actual nonlinear solution branch selected by the field equation.

Therefore the Gaussian result should be treated only as a search heuristic.

## 5. What this tells us

The matter sector now distinguishes three levels:

1. **trial localized profile**;
2. **actual nonlinear localized solution**;
3. **energetically stable nonlinear solution**.

Only level 2 has currently been demonstrated numerically for the representative
branch tested here.

Level 3 remains open.

## 6. Next matter task

The next search should map solution branches over

[
omega,quad
A_0,quad
lambda_4,quad
lambda_6
]

and identify whether any nodeless nonlinear branch satisfies

[
E/Q<m_{m free}.
]

Only after that should the model treat the excitation as a serious stable
matter candidate.

## Status

The project now has a self-consistent nonlinear classical matter solver and an
explicit stability filter.
