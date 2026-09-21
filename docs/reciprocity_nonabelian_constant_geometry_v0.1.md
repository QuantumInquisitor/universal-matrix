# Non-Abelian Reciprocity Background Bridge v0.1

## Purpose

The continuum reciprocity coupling for Yang-Mills fields was already derived,

[
mathcal H_{m YM}
=
rac12
e^{-2psi}
sum_a
left(
|D_a|^2+|B_a|^2
ight).
]

This extension connects that result to the actual dynamical SU(2) and SU(3)
lattice Hamiltonians.

Implementation:

`src/reciprocity_nonabelian_constant_geometry.py`

Tests:

`tests/test_reciprocity_nonabelian_constant_geometry.py`

## 1. Uniform reciprocity background

For constant

[
psi,
]

define

[
w(psi)=e^{-2psi}.
]

The complete Yang-Mills lattice Hamiltonian scales as

[
oxed{
H_{m YM}(psi)
=
w(psi)H_{m YM}(0).
}
]

## 2. Hamilton equations

Because every gauge Hamiltonian term receives the same constant multiplier,

[
dot U_i
=
w,dot U_i^{(0)},
]

[
dot E_i
=
w,dot E_i^{(0)}.
]

Therefore evolution for coordinate duration

[
Delta t
]

is exactly equivalent to flat-background evolution for

[
oxed{
Delta t_{m eff}
=
e^{-2psi}Delta t.
}
]

The implementation verifies this step-by-step for both SU(2) and SU(3).

## 3. Causal speed

The non-Abelian characteristic coordinate speed is therefore

[
oxed{
c_{m YM}
=
e^{-2psi}.
}
]

This matches the already derived speeds for:

- null rays;
- the reciprocity scalar;
- U(1);
- massless Dirac fields.

Thus all currently implemented relativistic field sectors share one causal
cone in a constant reciprocity background.

## 4. Geometry source

For

[
H(psi)
=
e^{-2psi}H_0,
]

[
-rac{partial H}{partialpsi}
=
2H.
]

Hence

[
oxed{
S_{m active}^{m YM}
=
2H_{m YM}
}
]

for free gauge fields, matching the continuum traceless-stress result

[
ho+sum_i p_i
=
2ho.
]

## 5. Why this is a bridge rather than the final geometry coupling

When

[
psi=psi(mathbf x),
]

a single global factor is no longer sufficient.

Then one needs:

- link-centered electric weights;
- plaquette-centered magnetic weights;
- weighted non-Abelian forces;
- a local geometry-source deposition rule;
- proof of gauge covariance with those weights.

Those are discretization choices that must be made explicitly and verified.

## Status

SU(2) and SU(3) now share the reciprocity redshift and causal cone exactly in
the uniform-background limit.
