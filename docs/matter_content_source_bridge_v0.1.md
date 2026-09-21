# Matter-to-Content Source Bridge v0.1

## Purpose

The unified variational energy couples the neutral content scalar to matter
through

[
-g_chichi|Phi|^2.
]

Variation with respect to the scalar gives

[
-
abla^2chi
=
kappa_chi g_chi|Phi|^2.
]

Therefore the integrated content source charge is

[
oxed{
Q_{mathcal C}
=
kappa_chi g_chi
int |Phi|^2,d^3x.
}
]

Implementation:

`src/matter_content_source_bridge.py`

Tests:

`tests/test_matter_content_source_bridge.py`

## 1. Gaussian candidate source charge

For the Gaussian localized matter ansatz,

[
int |Phi|^2 d^3x
=
I_2.
]

Thus

[
Q_{mathcal C}
=
kappa_chi g_chi I_2.
]

## 2. Universality test

A gravity-like source should ultimately couple almost universally to rest
energy.

Therefore inspect

[
oxed{
rac{Q_{mathcal C}}{E}.
}
]

If this ratio differs substantially between stable matter species or internal
states, the model predicts composition-dependent source strength.

The current variational candidates do show profile dependence in this ratio.

Therefore

[
oxed{
Q_{mathcal C}propto E
}
]

is **not** automatically guaranteed by the first scalar-matter coupling.

## 3. Why this is useful

This is a constructive failure.

It tells us that simply sourcing the scalar with (|Phi|^2) is not enough to
derive equivalence-principle behavior.

Possible deeper resolutions include:

- coupling the scalar to the full matter energy density rather than amplitude
  density;
- deriving both inertial energy and content charge from a common Noether or
  topological invariant;
- adding stress-energy dependence in the self-consistent action;
- showing that exact nonlinear stable solutions all approach one universal
  ratio.

Those possibilities must be tested rather than assumed.

## 4. Next step

The Gaussian ansatz is only variational.

The next calculation should solve the nonlinear radial matter equation itself
and measure

[
E,quad
Q,quad
Q_{mathcal C}/E
]

on actual field-equation solutions.

## Status

The repository now contains an explicit equivalence-principle diagnostic at the
matter-source level, and the first coupling does not yet guarantee universality.
