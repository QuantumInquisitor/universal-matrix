# Localized Matter Persistence v0.1

## Purpose

A static or time-harmonic field-equation solution is not automatically a
long-lived object.

This extension maps radial matter profiles into the 3D real-time lattice and
tracks whether they persist, disperse, or radiate.

Implementation:

`src/localized_matter_persistence.py`

Tests:

`tests/test_localized_matter_persistence.py`

## 1. Radial-to-Cartesian map

A radial profile

[
f(r)
]

is interpolated onto

[
r(mathbf x)
=
sqrt{x^2+y^2+z^2}.
]

The time-harmonic initial data are

[
Phi(mathbf x,0)
=
f(r),
]

[
Pi(mathbf x,0)
=
iomega f(r).
]

## 2. Persistence diagnostics

The evolution records:

- initial/final energy;
- initial/final U(1) charge;
- peak field amplitude;
- RMS radius.

The RMS radius is

[
R_{m rms}
=
sqrt{
rac{
sum_{mathbf x}
r^2|Phi|^2
}{
sum_{mathbf x}
|Phi|^2
}
}.
]

## 3. Interpretation

A long-lived classical lump should approximately maintain:

[
Q
]

and

[
E
]

while keeping its peak amplitude and RMS size within a bounded range.

A rapidly increasing RMS radius indicates dispersion.

A rapidly collapsing peak may indicate dissolution.

Strong oscillation or radiation may indicate an excited/metastable state.

## 4. CI policy

Normal CI tests:

- mapping correctness;
- diagnostic correctness;
- energy/charge conservation on controlled free evolution.

Large nonlinear persistence runs are intentionally not executed on every
commit because they are research simulations rather than unit tests.

## 5. Strong matter criterion

A serious classical matter candidate should eventually satisfy all of:

1. converged nonlinear branch;
2. nodeless localization;
3. finite energy and charge;
4. favorable (E/Q);
5. bounded long-time RMS radius;
6. bounded long-time peak amplitude;
7. small conserved-quantity drift;
8. robustness to small perturbations.

## Status

The repository now has a complete path from radial nonlinear matter solution to
3D time-domain survival testing.
