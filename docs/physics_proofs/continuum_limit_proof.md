# Continuum-Limit Note for the Current Discrete Field Extensions

## Status

This document replaces an earlier invalid claim that a Taylor expansion of a finite-difference operator directly recovered the Einstein-Hilbert action or Einstein field equations.

A finite-difference Laplacian approaching a continuum Laplacian does **not** by itself derive General Relativity.

## 1. One-dimensional central difference

For a smooth scalar field (psi(x)), define

[
D_hpsi(x)
=
rac{psi(x+h)-2psi(x)+psi(x-h)}{h^2}.
]

Taylor expansion gives

[
psi(xpm h)
=
psi(x)
pm hpsi'(x)
+
rac{h^2}{2}psi''(x)
pm
rac{h^3}{6}psi'''(x)
+
rac{h^4}{24}psi^{(4)}(x)
+
O(h^5).
]

Therefore

[
D_hpsi(x)
=
psi''(x)
+
rac{h^2}{12}psi^{(4)}(x)
+
O(h^4).
]

Hence

[
oxed{
D_hpsi	opsi''
}
]

as (h	o0), with second-order truncation error under the stated smoothness assumptions.

## 2. Routing-step interpretation

If a discrete coordinate uses a step corresponding to (21Delta x), then

[
rac{
psi(x+21Delta x)
-2psi(x)
+psi(x-21Delta x)
}{
(Delta x)^2
}
=
441,psi''(x)
+
O(Delta x^2).
]

If instead the denominator is the physical squared displacement

[
(21Delta x)^2,
]

then the operator tends directly to

[
psi''(x).
]

This distinction is dimensional and must be stated explicitly.

## 3. Open 3D gauge extension

The current open gauge engine uses a cubical discrete-exterior-calculus structure rather than a (mathbb Z_{114}) manifold.

Its weak field energy is

[
H_h
=
rac12langle E_h,E_hangle
+
rac{eta}{2}
langle d_1A_h,d_1A_hangle.
]

Under an independently specified physical lattice spacing (a), smooth-field assumptions, and an appropriate refinement sequence, the discrete exterior derivative can approximate the continuum exterior derivative.

The weak lattice dispersion

[
omega^2
=
4eta
sum_i
sin^2left(rac{q_i}{2}ight)
]

has the small-wave-number expansion

[
omega^2
=
eta|mathbf q|^2
+
O(|mathbf q|^4).
]

This provides a defensible Maxwell-like linear continuum target for the Abelian gauge adapter.

## 4. What is not derived

The current continuum analysis does not derive:

- the Einstein-Hilbert action,
- an Einstein tensor,
- a spacetime metric,
- Newton's constant,
- General Relativity,
- physical SI lattice spacing,
- the measured value of the speed of light.

Deriving any of those would require additional independently justified physical structure and a separate convergence analysis.

## 5. Required future convergence study

A rigorous continuum program should define a family of meshes indexed by (h	o0) and measure:

1. consistency error,
2. stability,
3. convergence rate,
4. discrete energy conservation,
5. boundary-condition convergence,
6. gauge-invariant observable convergence,
7. comparison against a known continuum solution.

The current repository has the algebraic ingredients for such a numerical study but has not yet completed it.
