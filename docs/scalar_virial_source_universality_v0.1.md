# Scalar Virial Source Universality v0.1

## Purpose

The self-consistent reciprocity action sources the geometry scalar with

[
ho+p_x+p_y+p_z.
]

The remaining question is whether the **integrated** source of a localized
stationary matter state equals its total rest energy.

For the time-harmonic complex scalar sector, the answer is yes whenever the
exact stationary solution satisfies its virial identity.

Implementation:

`src/scalar_virial_source_universality.py`

Tests:

`tests/test_scalar_virial_source_universality.py`

## 1. Stationary localized field

Take

[
Phi(t,mathbf x)
=
e^{-iomega t}f(mathbf x).
]

Define

[
K
=
int
|dotPhi|^2
,d^3x,
]

[
G
=
int
|
ablaPhi|^2
,d^3x,
]

and

[
V
=
int
U(|Phi|^2)
,d^3x.
]

The total energy is

[
oxed{
E=K+G+V.
}
]

## 2. Geometry source

From variation of the reciprocity matter action,

[
M_{m active}
=
int
left(
ho+p_x+p_y+p_z
ight)
d^3x.
]

For this complex scalar,

[
oxed{
M_{m active}
=
4K-2V.
}
]

Spatial-gradient contributions cancel from the local active-source
combination.

## 3. Virial identity

For an exact stationary localized solution in three spatial dimensions,
Derrick scaling of the reduced time-harmonic action gives

[
oxed{
G+3(V-K)=0.
}
]

Equivalently,

[
K-V=rac{G}{3}.
]

## 4. Universal source result

Using the virial identity,

[
M_{m active}
=
4K-2V
=
2K+rac{2G}{3}.
]

The total energy becomes

[
E
=
K+G+V
=
2K+rac{2G}{3}.
]

Therefore

[
oxed{
M_{m active}=E.
}
]

This equality is independent of the detailed radial profile and potential,
provided an exact stationary localized solution exists and satisfies the
virial relation.

## 5. Stronger identity

Away from the stationary virial shell,

[
M_{m active}-E
=
3K-G-3V.
]

But

[
G+3(V-K)
=
G+3V-3K.
]

Hence

[
oxed{
M_{m active}-E
=
-
left[
G+3(V-K)
ight].
}
]

So the failure of source universality is exactly the negative virial residual.

This gives a useful numerical diagnostic.

## 6. Interpretation

For stationary localized scalar matter in the weak-background regime, the
geometry source is not an arbitrary charge.

It equals the total rest energy automatically:

[
oxed{
Q_{m geometry}
propto
E_{m rest}.
}
]

This is a much stronger result than assuming

[
Q_{mathcal C}=q_M M.
]

## 7. Limits of the theorem

The result currently applies to:

- the complex scalar matter sector;
- stationary time-harmonic localized states;
- three spatial dimensions;
- weak/background-flat virial analysis;
- fields with boundary behavior sufficient for the Derrick scaling argument.

It does not automatically establish the same result for:

- strongly self-gravitating solutions;
- radiating/time-dependent systems;
- fermions;
- gauge-field dominated bound states;
- non-Abelian composite matter.

Those sectors require their own stress-energy/virial analysis.

## 8. Connection to the equivalence principle

The result removes composition/profile dependence **within the stationary
scalar solution class** at the level of integrated source strength.

That is encouraging for equivalence-principle behavior.

It is not yet a complete proof of the weak equivalence principle for all forms
of matter.

## Status

For exact stationary localized complex-scalar solutions,

[
oxed{
M_{m active}=E
}
]

follows from the action plus the virial identity rather than being imposed as a
separate gravitational-charge postulate.
