# Stationary Source Universality from the von Laue Condition v0.1

## Purpose

The reciprocity matter action sources the geometry scalar with

[
T^{00}+T^{11}+T^{22}+T^{33}.
]

For scalar solitons, the virial theorem showed that the integrated source equals
the total energy.

This note generalizes that result to any stationary isolated system satisfying
stress-energy conservation and suitable boundary falloff.

Implementation:

`src/stationary_source_universality.py`

Tests:

`tests/test_stationary_source_universality.py`

## 1. Stress-energy conservation

Assume

[
partial_mu T^{mu
u}=0.
]

For a stationary system,

[
partial_0T^{0j}=0,
]

so

[
partial_kT^{kj}=0.
]

## 2. von Laue identity

Consider

[
partial_k
left(
x^iT^{kj}
ight).
]

Using stress conservation,

[
partial_k
left(
x^iT^{kj}
ight)
=
T^{ij}.
]

Integrating over all space,

[
int
T^{ij},d^3x
=
oint
x^iT^{kj}n_k,dA.
]

For a sufficiently localized isolated system, the boundary term vanishes.

Therefore

[
oxed{
int T^{ij}d^3x=0.
}
]

This is the von Laue condition.

## 3. Reciprocity source

The integrated geometry source is

[
M_{m active}
=
int
left(
T^{00}
+
T^{11}
+
T^{22}
+
T^{33}
ight)
d^3x.
]

Using the von Laue condition,

[
int T^{ii}d^3x=0.
]

Hence

[
oxed{
M_{m active}
=
int T^{00}d^3x
=
E.
}
]

## 4. Interpretation

For stationary isolated systems,

[
oxed{
	ext{geometry source}
=
	ext{total rest energy}
}
]

independent of the internal distribution of:

- pressure;
- tension;
- scalar gradients;
- electromagnetic/gauge field stress;
- binding stress;

provided the total conserved system satisfies the stationary Laue condition.

## 5. Why internal pressure does not break universality

A subsystem may have

[
int T^{ii}d^3x
eq0.
]

For example, radiation or gauge-field energy alone carries positive stress.

But a truly stationary isolated composite must include the stresses that confine
or bind that subsystem.

The total system satisfies

[
int T^{ij}d^3x=0,
]

not necessarily each component considered separately.

This prevents incorrectly assigning a factor-of-two gravitational source to a
confined radiation field while ignoring the stresses that confine it.

## 6. Relation to the scalar virial theorem

For the stationary complex scalar,

[
G+3(V-K)=0
]

is the scalar-sector realization of the same global stress-balance principle.

The identity

[
M_{m active}=E
]

derived from the scalar virial theorem is therefore a special case of the
broader stationary stress theorem.

## 7. Limits

The theorem does not automatically apply to:

- freely escaping radiation;
- explicitly time-dependent systems;
- systems with nonzero stress flux at infinity;
- externally supported configurations where the external support is omitted;
- nonconserved effective stress tensors.

Those cases require the complete system and boundary flux to be included.

## 8. Equivalence-principle implication

This substantially strengthens the universality argument.

The reciprocity coupling does not require a composition-specific gravitational
charge for stationary isolated matter.

Instead,

[
oxed{
Q_{m geometry}
propto
E_{m total}
}
]

follows from stress-energy conservation and stationarity.

This still does not by itself prove all aspects of the equivalence principle,
but it removes a major source-composition ambiguity.

## Status

The source-universality result now applies to a broad stationary isolated
stress-energy system, not only to the scalar soliton model.
