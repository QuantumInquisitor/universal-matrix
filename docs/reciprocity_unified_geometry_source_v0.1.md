# Unified Reciprocity Geometry Source v0.1

## Purpose

Matter, U(1), and Yang-Mills sectors now have separate metric-coupling
derivations. This note assembles them into one geometry-source principle.

Implementation:

`src/reciprocity_unified_geometry_source.py`

Tests:

`tests/test_reciprocity_unified_geometry_source.py`

## 1. Total action

Take

[
S_{m total}
=
S_psi
+
S_{m matter}
+
S_{U(1)}
+
S_{m YM}
+
S_{m binding}
+cdots.
]

Because every non-geometry sector depends on the same reciprocity metric

[
g_{mu
u}(psi),
]

the source of (psi) is additive:

[
oxed{
rac{delta S_{m total}}{deltapsi}
=
sqrt{-g}
left(
T^{00}_{m total}
+
T^{11}_{m total}
+
T^{22}_{m total}
+
T^{33}_{m total}
ight).
}
]

## 2. Scalar matter

For the complex scalar sector,

[
S_{m active}^{m scalar}
=
sqrt{-g}
(ho+sum_i p_i).
]

For a free homogeneous rest mode,

[
S_{m active}=E.
]

For a stationary localized nonlinear scalar satisfying its virial identity,
the integrated relation is also

[
oxed{
M_{m active}=E.
}
]

## 3. Free gauge fields

For U(1) or classical Yang-Mills radiation,

[
T^mu{}_mu=0.
]

Therefore locally

[
sum_i p_i=ho
]

and

[
oxed{
S_{m active}^{m gauge}
=
2ho.
}
]

Equivalently,

[
M_{m active}^{m free gauge}
=
2E
]

for a freely propagating isolated gauge-field packet when integrated over a
slice without additional binding stresses.

This does not violate the stationary universality theorem because a free
radiation packet is not a stationary localized bound object.

## 4. Stationary composite theorem

For a stationary isolated system with conserved total stress energy,

[
partial_mu T^{mu
u}=0,
]

and adequate spatial falloff, the von Laue condition gives

[
oxed{
int T^{ij}d^3x=0.
}
]

Therefore

[
M_{m active}
=
int
left(
T^{00}
+
sum_iT^{ii}
ight)d^3x
]

reduces to

[
oxed{
M_{m active}
=
int T^{00}d^3x
=
E_{m total}.
}
]

This result is independent of how the rest energy is partitioned among:

- scalar matter;
- electromagnetic field;
- non-Abelian gauge field;
- gradient energy;
- interaction energy;
- binding stress.

## 5. Why binding stress matters

Individual subsystems need not satisfy

[
M_{m active}=E.
]

For example, a gauge-field subsystem has

[
M_{m active}=2E.
]

A stationary bound object containing that gauge energy must also contain
confining or binding stresses.

Those stresses contribute to

[
sum_iT^{ii}
]

and restore the total von Laue condition.

Therefore universality belongs to the **complete isolated composite**, not to
each bookkeeping sector separately.

## 6. Equivalence-principle significance

The earlier amplitude-density source

[
Q_{mathcal C}proptoint|Phi|^2d^3x
]

was profile dependent and did not automatically track rest energy.

The metric-derived source instead gives, for stationary isolated composites,

[
oxed{
Q_{m geometry}
propto
E_{m rest,total}.
}
]

This removes the need for an independently assigned
"content charge per unit mass" for stationary matter, conditional on:

1. universal metric coupling;
2. conserved total stress energy;
3. stationarity;
4. localization / vanishing boundary moment flux.

## 7. Limits

The theorem does not automatically apply to:

- escaping radiation;
- externally supported systems with boundary stresses;
- rapidly time-dependent configurations;
- cosmological fluids occupying all space;
- systems that violate total stress-energy conservation.

Those regimes require the full local field equations.

## Status

The repository now has an action-based route from total stationary rest energy
to universal geometry-source strength across matter and gauge sectors.

This is a substantially stronger universality result than the previous
(|Phi|^2)-source model.
