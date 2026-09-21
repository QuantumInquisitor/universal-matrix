# Content-Gradient Propagation v0.1

## Purpose

This extension derives a propagation law from the experimental content-clock
lapse rather than inserting a force by hand.

Implementation:

`src/content_ray_propagation.py`

Tests:

`tests/test_content_ray_propagation.py`

## 1. Content-dependent index

The content-clock extension defines

[
n(mathbf x)
=
expleft[
g(mathcal C(mathbf x)-mathcal C_{m ref})
ight].
]

Under the hypothesis that one fixed physical link is crossed per local canonical
tick, (n) is a travel-time index.

## 2. Fermat/eikonal ray equation

Let

[
hat{mathbf u}
]

be the unit ray direction and (s) Euclidean arc length.

For an isotropic static index field,

[
rac{dmathbf x}{ds}
=
hat{mathbf u}
]

and

[
oxed{
rac{dhat{mathbf u}}{ds}
=

ablaln n
-
hat{mathbf u}
left(
hat{mathbf u}cdot
ablaln n
ight).
}
]

The longitudinal component of the index gradient changes travel time but does
not instantaneously bend the ray.

Only the transverse gradient changes direction.

## 3. Content form

Because

[
ln n
=
g(mathcal C-mathcal C_{m ref}),
]

we obtain

[
oxed{

ablaln n
=
g
ablamathcal C.
}
]

Therefore

[
oxed{
rac{dhat{mathbf u}}{ds}
=
g
left[

ablamathcal C
-
hat{mathbf u}
(hat{mathbf u}cdot
ablamathcal C)
ight].
}
]

The absolute reference content cancels from the local bending equation.

## 4. Weak-gradient behavior

For small excess content,

[
n
approx
1+g(mathcal C-mathcal C_{m ref}).
]

Thus the leading deflection is linear in the transverse content gradient.

## 5. Travel-time accumulation

The dimensionless optical/travel-time path integral is

[
oxed{
mathcal T
=
int n(mathbf x),ds.
}
]

Uniform content leaves the path straight but changes this travel-time integral.

Spatially varying content changes both travel time and trajectory.

## 6. Numerical method

The implementation integrates the ray equations with fourth-order Runge-Kutta
and renormalizes the direction vector after each stage.

The tests verify:

- uniform content gives a straight ray;
- transverse positive content gradient bends toward increasing content;
- longitudinal gradient produces no instantaneous transverse bending;
- the direction derivative remains transverse;
- the index composition law matches the content-clock exponential;
- uniform index gives the expected travel-time integral.

## 7. Gravity-like interpretation remains unproven

This mechanism produces two phenomena that are structurally interesting:

[
	ext{content}
	o
	ext{clock delay}
]

and

[

abla	ext{content}
	o
	ext{ray bending}.
]

Those are ingredients that a gravity-like theory would need.

They are not sufficient to establish gravity.

A physically viable gravity-like sector would still need to show:

1. universal coupling to matter;
2. massive-particle trajectory behavior from the same structure;
3. clock redshift from the same parameter set;
4. a correct weak-field limit;
5. compatibility with precision lensing constraints;
6. propagating field dynamics;
7. equivalence-principle behavior;
8. a falsifiable deviation from established gravitational theory.

## Status

The repository now contains a derived content-gradient propagation law:

[
oxed{
n=e^{g(mathcal C-mathcal C_{m ref})}
}
]

and

[
oxed{
rac{dhat{mathbf u}}{ds}
=
g
left[

ablamathcal C
-
hat{mathbf u}
(hat{mathbf u}cdot
ablamathcal C)
ight].
}
]

It is an experimental propagation adapter, not a gravitational field equation.
