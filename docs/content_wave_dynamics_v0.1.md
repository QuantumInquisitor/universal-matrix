# Dynamical Content Field v0.1

## Purpose

The static content-potential equation

[
-
abla^2chi
=
kappa_{mathcal C}ho_{mathcal C}
]

is instantaneous and therefore cannot by itself describe causal propagation.

This extension adds a finite-speed dynamical scalar field whose static limit is
the same Poisson equation.

Implementation:

`src/content_wave_dynamics.py`

Tests:

`tests/test_content_wave_dynamics.py`

## 1. Dynamical equation

The experimental field equation is

[
oxed{
partial_t^2chi
+
gamma(mathbf x)partial_tchi
=
c_chi^2
left[

abla^2chi
+
kappa_{mathcal C}ho_{mathcal C}
ight].
}
]

Here:

- (c_chi) is the scalar-field propagation speed;
- (gamma(mathbf x)) is an optional damping/sponge profile;
- (ho_{mathcal C}) is the nonnegative conserved-content source density.

## 2. Static limit

For

[
partial_tchi=0,
qquad
partial_t^2chi=0,
]

the equation reduces to

[

abla^2chi
+
kappa_{mathcal C}ho_{mathcal C}
=
0,
]

or

[
oxed{
-
abla^2chi
=
kappa_{mathcal C}ho_{mathcal C}.
}
]

Thus the static (1/r) potential is the stationary limit of the same field.

## 3. Finite propagation

The equation is hyperbolic.

A localized disturbance propagates at finite characteristic speed (c_chi)
in the continuum model.

The discrete implementation therefore cannot alter arbitrarily distant cells in
a single timestep.

## 4. Numerical method

The implementation uses:

- second-order centered finite differences in space;
- kick-drift-kick time integration;
- exact half-step damping factors;
- a CFL guard.

For the 3D six-neighbor stencil,

[
oxed{
rac{c_chiDelta t}{h}
le
rac1{sqrt3}
}
]

is enforced.

## 5. Six-face sponge

An optional damping profile grows toward the six outer faces.

This allows outgoing scalar disturbances to be attenuated before they encounter
the finite computational edge.

The sponge is a numerical boundary treatment, not a fundamental physical law.

## 6. Source-free field energy

With no source and no damping, the diagnostic energy is

[
mathcal E_chi
=
rac12
int
left[
rac{(partial_tchi)^2}{c_chi^2}
+
|
ablachi|^2
ight]
d^3x.
]

The numerical tests verify approximate conservation under the explicit
time-stepper.

## 7. Physical implications if the scalar field is real

The architecture would then contain the chain

[
ho_{mathcal C}
ightarrow
chi
ightarrow
	ext{clock lapse}
ightarrow
	ext{ray travel time}.
]

Changes in the source would propagate through (chi) at finite speed rather
than updating the entire domain instantaneously.

## 8. What this still does not reproduce

A single scalar field has one scalar degree of freedom.

Observed gravitational radiation in General Relativity has tensor structure.

Therefore this scalar field cannot simply be identified with the full
gravitational field without additional structure and experimental evidence.

It could at most be:

- an experimental scalar interaction;
- one sector of a larger theory;
- an effective approximation.

## 9. Next question

The next strong constraint is whether

[
c_chi
]

must equal the gauge-sector causal speed or can differ.

If all fundamental information shares one causal cone, the model should derive

[
c_chi=c_{m gauge}.
]

If not, the theory predicts multiple propagation speeds and must confront
experimental bounds.

## Status

The content sector now has both:

[
oxed{
-
abla^2chi
=
kappa_{mathcal C}ho_{mathcal C}
}
]

as its static limit and

[
oxed{
chi_{tt}
+
gammachi_t
=
c_chi^2
(
abla^2chi+kappa_{mathcal C}ho_{mathcal C})
}
]

as its finite-speed experimental dynamics.
