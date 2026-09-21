# Circular Orbits and ISCO in the Reciprocity Exterior v0.1

## Purpose

The exact reciprocity exterior predicts timelike circular-orbit structure that
differs from Schwarzschild in the strong-field regime.

Implementation:

`src/reciprocity_circular_orbits.py`

Tests:

`tests/test_reciprocity_circular_orbits.py`

## 1. Metric functions

In the equatorial plane,

[
A(r)=e^{-2mu/r},
]

[
C(r)=e^{2mu/r}r^2.
]

For a static spherical metric,

[
Omega^2
=
rac{A'}{C'}.
]

## 2. Circular-orbit frequency

For the reciprocity exterior,

[
oxed{
Omega^2
=
rac{
mu e^{-4mu/r}
}{
r^2(r-mu)
}.
}
]

## 3. Specific energy

The specific energy of a timelike circular orbit is

[
oxed{
E^2
=
e^{-2mu/r}
rac{
r-mu
}{
r-2mu
}.
}
]

## 4. Specific angular momentum

[
oxed{
L^2
=
rac{
mu e^{2mu/r}r^2
}{
r-2mu
}.
}
]

Timelike circular orbits therefore require

[
r>2mu.
]

The limiting radius

[
r=2mu
]

is the null circular orbit already found from the photon analysis.

## 5. Marginal stability

The ISCO occurs when

[
rac{dL^2}{dr}=0.
]

For the exponential exterior this reduces exactly to

[
oxed{
r^2-6mu r+4mu^2=0.
}
]

The root outside the photon orbit is

[
oxed{
r_{m ISCO}
=
(3+sqrt5)mu.
}
]

Numerically,

[
r_{m ISCO}
approx
5.23606798,mu.
]

## 6. Areal radius

The areal radius is

[
R
=
re^{mu/r}.
]

Therefore

[
oxed{
R_{m ISCO}
approx
6.337940264856347,mu.
}
]

Schwarzschild gives

[
R_{m ISCO}^{m GR}
=
6mu.
]

The reciprocity value is about 5.6 percent larger.

## 7. ISCO orbital frequency

The dimensionless reciprocity frequency is

[
oxed{
Omega_{m ISCO}mu
approx
0.06333263135.
}
]

Schwarzschild gives

[
oxed{
Omega_{m ISCO}^{m GR}mu
=
rac1{6sqrt6}
approx
0.06804138174.
}
]

The reciprocity value is about 6.9 percent lower.

## 8. Why this matters

ISCO location and frequency enter:

- accretion-disk inner-edge models;
- orbital energy extraction;
- extreme-mass-ratio inspirals;
- strong-field timing;
- gravitational-wave phasing.

Therefore this is another direct observational discriminator between the
reciprocity exterior and Schwarzschild geometry.

## 9. Interpretation warning

These formulas are exact predictions of the proposed static reciprocity
exterior.

They are not evidence that observed compact objects follow this geometry.

Spin, matter environment, disk physics, and radiation must be included in any
real observational comparison.

## Status

The reciprocity model now has exact circular-orbit and ISCO predictions in
addition to its photon-ring and lensing predictions.
