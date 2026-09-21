# Weak-Field Spatial Response Bridge v0.1

## Purpose

The content-clock sector gives a weak dimensionless potential

[
psi>0
]

near a positive source with local clock-rate ratio

[
rac{r_{m local}}{r_{m ref}}
=
e^{-psi}
approx
1-psi.
]

A clock-only travel-time index gives

[
n=e^psi.
]

For a point source

[
psi=rac{mu}{r},
]

that produces the leading deflection

[
alpha_{m clock}
=
rac{2mu}{b}.
]

That is only half the General Relativistic weak-field light deflection.

This document introduces an explicit spatial-response coefficient rather than
hiding that discrepancy.

Implementation:

`src/weak_field_ppn_bridge.py`

Tests:

`tests/test_weak_field_ppn_bridge.py`

## 1. Spatial-response factor

Define

[
S(psi)
=
e^{gamma_Mpsi}.
]

Here

[
gamma_M
]

is the Matrix spatial-response coefficient.

The effective optical/travel-time index becomes

[
oxed{
n
=
rac{S}{r_{m local}/r_{m ref}}
=
e^{(1+gamma_M)psi}.
}
]

## 2. Point-source deflection

For

[
psi(r)=rac{mu}{r},
]

the leading weak-field ray deflection is

[
oxed{
alpha
=
2(1+gamma_M)rac{mu}{b}.
}
]

Therefore:

### Clock-only sector

[
gamma_M=0
]

gives

[
alpha
=
rac{2mu}{b}.
]

### Symmetric clock/space response

[
gamma_M=1
]

gives

[
alpha
=
rac{4mu}{b}.
]

That matches the standard General Relativistic leading coefficient.

## 3. Relation to PPN gamma

At this weak-field correspondence level,

[
oxed{
gamma_M
leftrightarrow
gamma_{m PPN}.
}
]

This does not prove that the full Matrix theory is metric gravity.

It only identifies what coefficient the spatial sector would have to reproduce
in the solar-system weak-field regime.

## 4. Experimental requirement

Solar-system measurements constrain

[
gamma_{m PPN}
]

very close to 1.

The Cassini time-delay measurement is commonly summarized as

[
gamma-1
=
(2.1pm2.3)	imes10^{-5}.
]

Therefore a gravity-like Matrix interpretation requires

[
oxed{
gamma_Mapprox1
}
]

to high precision in the tested regime.

## 5. Important failure result

The existing scalar clock sector corresponds to

[
gamma_M=0.
]

Therefore

[
oxed{
	ext{the scalar clock sector alone cannot reproduce observed weak-field light bending.}
}
]

This is a useful falsification of an incomplete version of the model.

## 6. What must be derived next

A real completion needs a spatial mechanism that produces

[
S(psi)
]

from the Matrix architecture.

The coefficient (gamma_M) should not simply be set to 1 because General
Relativity requires it.

Candidate structural origins to test include:

- content-dependent deformation of six-gate link lengths;
- isotropic rescaling of the three signed axis pairs;
- scale-transfer-induced spatial dilation;
- gauge-field backreaction on the spatial adjacency metric;
- a derived effective spatial metric on the open cubical complex.

## 7. Strong design requirement

The same content potential should control, with one parameter set:

1. clock-rate shift;
2. spatial-link response;
3. light propagation;
4. massive-particle motion;
5. source field dynamics.

If different ad hoc coefficients are needed for each observable, the model is
not yet unified.

## Status

The weak-field audit now has a quantitative failure criterion and a precise
missing sector:

[
oxed{
gamma_M
=
	ext{spatial response that the Matrix must derive.}
}
]
