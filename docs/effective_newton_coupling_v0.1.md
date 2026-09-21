# Effective Newton-Like Coupling v0.1

## Purpose

The content potential and reciprocity metric together generate an inverse-square
weak acceleration.

This note makes the effective coupling explicit instead of hiding it inside a
symbol identified afterward with Newton's constant.

Implementation:

`src/effective_newton_coupling.py`

Tests:

`tests/test_effective_newton_coupling.py`

## 1. Point-source content potential

For source content charge

[
Q_{mathcal C},
]

the scalar field gives

[
chi(r)
=
rac{
kappa_{mathcal C}Q_{mathcal C}
}{
4pi r
}.
]

The dimensionless geometry/clock potential is

[
psi
=
g_chichi.
]

Therefore

[
psi(r)
=
rac{mu}{r},
]

where

[
oxed{
mu
=
rac{
g_chikappa_{mathcal C}Q_{mathcal C}
}{
4pi
}.
}
]

## 2. Source content proportional to mass

Suppose

[
Q_{mathcal C}
=
q_M M,
]

where

[
q_M
]

is content charge per unit source mass.

Then

[
mu
=
rac{
g_chikappa_{mathcal C}q_M M
}{
4pi
}.
]

## 3. Weak reciprocity acceleration

The reciprocity metric gives

[
mathbf a
=
c_*^2
ablapsi.
]

For the point source,

[
|mathbf a|
=
rac{
c_*^2g_chikappa_{mathcal C}q_M
}{
4pi
}
rac{M}{r^2}.
]

Define

[
oxed{
G_{m eff}
=
rac{
c_*^2g_chikappa_{mathcal C}q_M
}{
4pi
}.
}
]

Then

[
oxed{
|mathbf a|
=
rac{
G_{m eff}M
}{
r^2
}.
}
]

## 4. What this does and does not derive

This factorization explains how a Newton-like constant would arise from the
current extension.

It does **not** derive the measured value of Newton's constant.

The model still needs independent values for:

- causal speed (c_*);
- clock coupling (g_chi);
- scalar-field coupling (kappa_{mathcal C});
- source content charge per mass (q_M).

If their product is selected solely to reproduce measured (G), that is
calibration.

## 5. Equivalence-principle requirement

At test-particle level the metric acceleration is independent of the test
mass.

However, source universality requires

[
q_M
]

to be the same for different source compositions to very high precision in the
regimes where universal gravity is observed.

If

[
q_M^{(A)}

eq
q_M^{(B)},
]

different materials source different fields per unit inertial mass.

That would create equivalence-principle / fifth-force signatures.

The MICROSCOPE constraint ledger therefore places a strong empirical restriction
on any material dependence of (q_M).

## 6. A possible deeper identification

One future route is to derive

[
Q_{mathcal C}
propto
E_{m rest}
]

rather than assume proportionality to mass.

If

[
E_{m rest}=Mc_*^2,
]

then content charge universality could follow from the same localized field
energy that produces inertial mass.

That would be more unified than assigning an independent (q_M).

It has not yet been derived.

## 7. Next question

The strongest next matter-sector question is now

[
oxed{
	ext{Does a stable localized Matrix excitation carry }
Q_{mathcal C}
propto
E_{m rest}?
}
]

If yes, inertial mass, source content, clock response, and the inverse-square
field could become different manifestations of one conserved excitation.

## Status

The model now exposes the Newton-like coupling as a product of underlying
content-sector quantities instead of treating it as fundamental by definition.
