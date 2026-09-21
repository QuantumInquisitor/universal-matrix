# Massive-Motion Branch Ambiguity v0.1

## Purpose

The content-clock law fixes a travel-time index,

[
n=e^{g(mathcal C-mathcal C_{m ref})},
]

and therefore fixes the direction of ray bending in the Fermat propagation
adapter.

That does **not** by itself determine the equation of motion for massive test
bodies.

Implementation:

`src/content_massive_motion_candidates.py`

Tests:

`tests/test_content_massive_motion_candidates.py`

## 1. Minimal scalar-potential family

A broad minimal specific-potential family is

[
rac{U}{m}
=
s,v_*^2ln n,
]

where

[
s=pm1.
]

Since

[
ln n
=
g(mathcal C-mathcal C_{m ref}),
]

we have

[
rac{U}{m}
=
s,v_*^2 g
(mathcal C-mathcal C_{m ref}).
]

The acceleration is

[
oxed{
mathbf a
=
-s,v_*^2 g,
ablamathcal C.
}
]

## 2. Two physically different branches

For

[
s=-1,
]

[
mathbf a
=
+v_*^2g
ablamathcal C,
]

so test bodies accelerate toward increasing content.

For

[
s=+1,
]

[
mathbf a
=
-v_*^2g
ablamathcal C,
]

so they accelerate toward decreasing content.

The content-clock law itself does not choose between these.

## 3. Universal test-particle acceleration

If

[
U=mV,
]

then

[
mathbf F
=
-m
abla V,
]

so

[
rac{mathbf F}{m}
=
mathbf a
]

is independent of the test body's inertial mass.

Thus either branch has a weak equivalence-principle-like feature at the
test-particle level.

That is not sufficient to establish gravitational physics.

## 4. Why this ambiguity matters

The model currently determines:

- canonical clock phase;
- content-dependent tick duration;
- content-dependent ray travel time;
- ray bending toward increasing travel-time index.

But massive-particle motion requires an additional action principle.

Therefore the step

[
	ext{clock gradient}
ightarrow
	ext{universal attraction}
]

is not yet derived.

## 5. Strong next question

A deeper principle must determine the sign and normalization of the massive
action.

Possible criteria include:

1. consistency of massive and massless trajectories in a common effective
   geometry;
2. stability of localized matter states;
3. Hamiltonian boundedness;
4. conservation laws;
5. a relativistic variational principle;
6. a measured weak-field limit.

The preferred branch should emerge from one of these requirements rather than
being selected because it resembles gravity.

## Status

The repository now encodes the ambiguity rather than hiding it.

That is a constraint on future theory development:

[
oxed{
	ext{content clock alone does not derive universal attraction.}
}
]
