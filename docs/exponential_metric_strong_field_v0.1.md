# Strong-Field Exponential-Metric Diagnostics v0.1

## Purpose

Clock-space reciprocity leads to the effective exponential metric

[
ds^2
=
-e^{-2psi}c_*^2dt^2
+
e^{2psi}
(dr^2+r^2dOmega^2).
]

For the point-source continuation

[
psi(r)=rac{mu}{r},
]

this note derives exact strong-field consequences.

Implementation:

`src/exponential_metric_strong_field.py`

Tests:

`tests/test_exponential_metric_strong_field.py`

## 1. No finite-radius lapse zero

The lapse is

[
N(r)=e^{-mu/r}.
]

For every finite

[
r>0,
]

[
N(r)>0.
]

Therefore this effective metric has no finite isotropic radius where the lapse
vanishes.

It does not contain a Schwarzschild-like event horizon at finite (r).

## 2. Areal radius

The spatial metric gives

[
g_{	heta	heta}
=
e^{2mu/r}r^2.
]

Hence the areal radius is

[
oxed{
R(r)
=
r e^{mu/r}.
}
]

Differentiate:

[
rac{dR}{dr}
=
e^{mu/r}
left(
1-rac{mu}{r}
ight).
]

Thus

[
rac{dR}{dr}=0
]

at

[
oxed{
r_{m throat}=mu.
}
]

The minimum areal radius is

[
oxed{
R_{m throat}
=
emu.
}
]

This is the throat-like behavior noted in published analyses of exponential
metrics.

## 3. Null circular orbit

For a static isotropic metric, the squared null impact parameter is

[
b^2(r)
=
rac{C(r)}{A(r)}
]

with

[
A=e^{-2mu/r},
qquad
C=e^{2mu/r}r^2.
]

Therefore

[
b^2(r)
=
r^2 e^{4mu/r}.
]

Its extremum satisfies

[
rac{d}{dr}ln b^2
=
rac{2}{r}
-
rac{4mu}{r^2}
=
0.
]

Hence

[
oxed{
r_{m ph}=2mu.
}
]

The corresponding areal radius is

[
oxed{
R_{m ph}
=
2e^{1/2}mu.
}
]

## 4. Critical impact parameter

At the null circular orbit,

[
b_c
=
r e^{2mu/r}.
]

Thus

[
oxed{
b_c
=
2e,mu.
}
]

For Schwarzschild,

[
b_{c,m Schw}
=
3sqrt3,mu.
]

Therefore

[
rac{b_c}{b_{c,m Schw}}-1
=
rac{2e}{3sqrt3}-1
approx
0.046.
]

So the point-source reciprocity metric predicts a shadow/photon-ring scale about
4.6 percent larger than Schwarzschild for the same (mu=GM/c^2) mapping.

## 5. Why this matters

Weak-field agreement does not guarantee strong-field agreement.

The same reciprocity assumptions that produce

[
eta_{m PPN}=gamma_{m PPN}=1
]

also imply strong-field behavior that differs from Schwarzschild.

That gives the model a genuine discriminating target.

## 6. Important interpretation warning

The exponential metric is historically known and published analyses have
described its throat/wormhole-like strong-field structure.

The Universal Matrix project should not claim discovery of that geometry.

The project-specific question is instead:

> Does the Matrix derivation require this exact exponential continuation at
> strong field, or is the exponential relation only a weak-field effective law?

That distinction is unresolved.

## 7. Next validation targets

The strong-field candidate should be compared with:

- black-hole shadow/ring measurements;
- photon-ring location;
- stellar or gas orbital dynamics;
- binary inspiral phasing;
- ringdown spectra;
- horizon-sensitive observations.

If those data exclude the exact exponential continuation, the weak-field
reciprocity construction could still survive as an approximation while the
strong-field completion must change.

## Status

The model now has a quantitative strong-field prediction:

[
oxed{
b_c=2e,mu
}
]

for the simplest point-source exponential continuation.

This is testable and differs from Schwarzschild.
