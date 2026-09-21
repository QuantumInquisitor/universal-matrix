# Source Interaction and Force Observable v0.1

## Purpose

This extension asks whether attraction and repulsion can emerge from the Matrix gauge field energy without inserting a Coulomb or gravitational potential.

Implementation:

`src/source_interaction.py`

Tests:

`tests/test_source_interaction.py`

## 1. Starting point

The 3D gauge adapter already supplies a Gauss constraint

[

abla_{m lat}cdot E=ho.
]

For a fixed static charge distribution, the lowest-energy longitudinal field is obtained by minimizing

[
U_E=rac12sum_{	ext{links}}E^2
]

subject to that constraint.

Writing

[
E_i(x)=phi(x)-phi(x+hat i)
]

reduces the constrained minimization to the periodic discrete Poisson problem

[
Lphi=ho,
]

where

[
Lphi(x)
=
sum_i
left[
2phi(x)-phi(x+hat i)-phi(x-hat i)
ight].
]

No (1/r) potential is inserted.

## 2. Spectral solution

On a periodic lattice, the positive lattice-Laplacian eigenvalue is

[
lambda(mathbf k)
=
4sum_{i=x,y,z}
sin^2left(rac{k_i}{2}ight).
]

For every nonzero mode,

[
phi(mathbf k)
=
rac{ho(mathbf k)}
{lambda(mathbf k)}.
]

The zero mode must vanish for a periodic Poisson solution. For non-neutral source sets, the implementation subtracts the uniform mean charge. This is equivalent to adding a uniform compensating background and is explicitly labeled as such.

## 3. Interaction observable

The field energy is

[
oxed{
U[ho]
=
rac12sum_{	ext{links}}E^2
}
]

with (E) obtained from the Poisson solution.

For two sources, the quadratic energy can be decomposed into

[
U_{12}
=
U_1+U_2+U_{m cross}.
]

The pair interaction cross-term is therefore

[
oxed{
U_{m int}
=
U_{12}-U_1-U_2.
}
]

This observable is produced from the Gauss constraint and field energy, not from an assumed pair potential.

## 4. Like versus opposite source signs

For equal-magnitude localized sources, the solver gives

[
U_{m int}<0
]

for opposite signs and

[
U_{m int}>0
]

for like signs.

Moreover, on lattices large compared with the separation:

- opposite-sign pair energy is lower when the sources are closer;
- like-sign pair energy is higher when the sources are closer.

Thus the energy gradient has the expected qualitative behavior:

[
oxed{	ext{opposite signs attract}}
]

[
oxed{	ext{like signs repel}}.
]

This behavior is not an independent new force law. It is the interaction implied by the Abelian Gauss constraint plus quadratic field energy.

## 5. Discrete force proxy

A radial finite-difference observable is defined by

[
F_r(r)
=
-rac{U(r+1)-U(r-1)}{2}
]

in lattice units.

Its sign reverses when the relative source sign reverses.

The precise magnitude is lattice-dependent at short distance and affected by periodic images at large distance.

## 6. Continuum expectation

The Fourier-space kernel

[
rac{1}
{4sum_isin^2(k_i/2)}
]

approaches

[
rac{1}{|mathbf k|^2}
]

at long wavelength because

[
4sin^2(k_i/2)approx k_i^2.
]

Therefore the large-distance infinite-volume Green function approaches the usual three-dimensional Laplace Green function.

This means that a Coulomb-like (1/r) interaction is expected in the continuum limit of this U(1) gauge sector. That behavior is a consequence of the lattice Poisson operator, not evidence that the Universal Matrix has replaced electromagnetism.

## 7. Relation to polarity

The source/current extension still has to specify how a localized Matrix polarity configuration determines the sign and magnitude of physical (ho).

Once that mapping is fixed, the gauge sector already supplies the qualitative interaction rule:

[
ho_1ho_2<0
Rightarrow
	ext{lower energy at smaller separation},
]

[
ho_1ho_2>0
Rightarrow
	ext{higher energy at smaller separation}.
]

The next task is therefore not to add attraction/repulsion manually. It is to derive the source map

[
(A,sigma,phi,	ext{nested state})
longrightarrow
ho
]

from the polarity dynamics.

## 8. Tests

The regression suite checks:

1. the spectral Poisson solution satisfies the lattice Gauss constraint;
2. periodic zero-mode neutralization is exact;
3. opposite-sign source energy rises with separation over the tested range;
4. like-sign source energy falls with separation over the tested range;
5. the discrete force proxy reverses sign between opposite and like sources;
6. the interaction cross-term changes sign with the source product.

## Status

The engine now derives attraction/repulsion behavior from the gauge field-energy minimum without inserting either a Coulomb or gravitational pair potential.

This is a structural result of the U(1) gauge sector. It is not yet a derivation of gravity and does not yet determine the physical strength or SI units of the interaction.
