# Conditional Uniqueness of the Reciprocity Metric v0.1

## Purpose

The exponential reciprocity metric should not be presented as an unexplained
guess.

This note isolates the assumptions that select it.

Implementation:

`src/reciprocity_metric_uniqueness.py`

Tests:

`tests/test_reciprocity_metric_uniqueness.py`

## Assumptions

### A1 — Six-gate isotropy

The signed-permutation symmetry of

[
B_6={pm X,pm Y,pm Z}
]

forces a symmetry-preserving linear spatial response to be isotropic.

Therefore

[
h_{ij}
=
S(psi)^2delta_{ij}.
]

### A2 — Additive scalar composition

Assume scalar potential increments add,

[
psi_{m total}
=
psi_1+psi_2,
]

while spatial responses compose multiplicatively,

[
S(psi_1+psi_2)
=
S(psi_1)S(psi_2),
]

with continuity and

[
S(0)=1.
]

Then the continuous solutions are

[
oxed{
S(psi)=e^{gammapsi}.
}
]

### A3 — Clock response

The clock sector gives

[
N(psi)=e^{-psi}.
]

Therefore the local tick-duration lapse is

[
L_t=e^psi.
]

### A4 — Local causal reciprocity

Assume one local causal propagation unit remains one responded spatial unit per
one responded local tick.

Then

[
rac{S}{L_t}=1
]

for arbitrary (psi).

Using

[
S=e^{gammapsi},
qquad
L_t=e^psi,
]

gives

[
e^{(gamma-1)psi}=1
]

for arbitrary (psi), so

[
oxed{
gamma=1.
}
]

## Result

The spatial scale is therefore

[
oxed{
S(psi)=e^psi.
}
]

Together with

[
N(psi)=e^{-psi},
]

the static isotropic metric is

[
oxed{
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}dmathbf x^2.
}
]

## What is actually unique

The exponential metric is unique **conditional on A1-A4**.

The canonical finite kernel directly supports the six-gate symmetry used in A1.

A2-A4 remain physical/modeling principles that must be independently justified
or experimentally tested.

Therefore the correct statement is

[
oxed{
A1+A2+A3+A4
Longrightarrow
	ext{exponential reciprocity metric}.
}
]

It is not

[
mathbb Z_{108}sqcup B_6
Longrightarrow
	ext{metric}
]

without additional assumptions.

## Status

The metric map is now conditionally derived from an explicit short list of
premises rather than being left as an opaque ansatz.
