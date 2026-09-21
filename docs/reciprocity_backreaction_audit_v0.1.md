# Reciprocity Backreaction Audit v0.1

## Purpose

The reciprocity construction gives an effective geometry

[
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}dmathbf x^2.
]

The scalar content field was initially evolved on a fixed Euclidean background.

That is sufficient for a weak/static prototype but is not a complete
strong-field theory because the same scalar is also being used to define an
effective geometry.

This note checks what survives when a scalar is propagated on the prescribed
reciprocity geometry and identifies what remains missing.

Implementation:

`src/reciprocity_backreaction_audit.py`

Tests:

`tests/test_reciprocity_backreaction_audit.py`

## 1. Determinant

For

[
g_{mu
u}
=
mathrm{diag}
left(
-c_*^2e^{-2psi},
e^{2psi},
e^{2psi},
e^{2psi}
ight),
]

the determinant is

[
oxed{
g
=
-c_*^2e^{4psi}.
}
]

Therefore

[
oxed{
sqrt{-g}
=
c_*e^{2psi}.
}
]

## 2. Spatial inverse metric

The inverse spatial metric is

[
g^{ij}
=
e^{-2psi}delta^{ij}.
]

Hence

[
oxed{
sqrt{-g},g^{ij}
=
c_*,delta^{ij}.
}
]

The (psi)-dependence cancels exactly.

## 3. Static covariant scalar operator

For a static test scalar (f),

[
Box_g f
=
rac1{sqrt{-g}}
partial_i
left(
sqrt{-g},g^{ij}partial_j f
ight).
]

Using the cancellation above,

[
oxed{
Box_g f
=
e^{-2psi}

abla^2 f.
}
]

Therefore a static harmonic field satisfying

[

abla^2 f=0
]

also satisfies

[
Box_g f=0.
]

If (f=psi) is treated only as a test scalar on the already specified
geometry, the exterior

[
psiproptorac1r
]

profile remains covariantly harmonic away from the source.

## 4. Why this is not yet self-consistent gravity

The previous calculation treats the geometry as already given.

But here

[
g_{mu
u}
=
g_{mu
u}(psi).
]

A true self-coupled theory must start from an action and vary with respect to
the actual independent degrees of freedom.

If the metric depends on the same scalar being varied, additional terms arise
through that dependence.

Therefore

[
oxed{
Box_gpsi=0
}
]

cannot simply be declared the final self-field equation without deriving the
action.

## 5. What the current audit establishes

It establishes:

1. the exponential reciprocity geometry has a simple exact determinant;
2. the static spatial scalar operator has a strong cancellation;
3. the (1/r) vacuum profile is compatible with the prescribed geometry at
   the test-field level;
4. the current flat-background scalar wave equation is only a prototype.

## 6. Next theoretical requirement

The next non-negotiable derivation is a self-consistent action

[
S[psi,	ext{matter},	ext{gauge},ldots]
]

whose variation determines:

- the scalar field equation;
- the effective geometry response;
- source coupling;
- conservation laws;
- stress-energy exchange.

The action must reproduce the already successful weak-field limits without
inserting them separately.

## Status

The repository now explicitly distinguishes

[
oxed{
	ext{effective geometry audit}
}
]

from

[
oxed{
	ext{complete self-coupled field theory}.
}
]

The latter does not yet exist.
