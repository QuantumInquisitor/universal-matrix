# Matter Defect Structure v0.1

## Status

This note records two exact nonlinear consequences of the current default matter potential.

They are mathematical results inside the repository's classical scalar normalization. They are not claims that an observed particle or cosmological defect has been identified.

## Default potential factorization

For

\[
U(\rho)
=
\rho
-
2\rho^2
+
\rho^3,
\]

and a real amplitude \(f\),

\[
\rho=f^2,
\]

so

\[
\boxed{
U(f^2)
=
f^2(1-f^2)^2.
}
\]

The scalar therefore has degenerate zero-energy vacua at

\[
f=0
\]

and

\[
|f|=1.
\]

## Exact one-dimensional wall

A static real field satisfies

\[
f''
=
f(1-4f^2+3f^4).
\]

The first integral connecting the two degenerate vacua is

\[
(f')^2
=
U(f^2)
=
f^2(1-f^2)^2.
\]

Choosing the increasing branch,

\[
f'
=
f(1-f^2).
\]

The exact solution is

\[
\boxed{
f(x)
=
\frac{1}
{\sqrt{1+e^{-2(x-x_0)}}}.
}
\]

It connects

\[
f(-\infty)=0
\]

to

\[
f(+\infty)=1.
\]

## Exact wall tension

With the repository energy normalization

\[
E
=
\int dx
\left[
(f')^2
+
U(f^2)
\right],
\]

the first-order identity gives

\[
(f')^2=U.
\]

Therefore

\[
T_{\rm wall}
=
2\int_0^1
df\,
\sqrt{U(f^2)}
=
2\int_0^1
df\,
f(1-f^2)
=
\boxed{\frac12}.
\]

This is an exact nonlinear defect scale in native dimensionless units.

## Three-dimensional static localization constraint

The existence of a one-dimensional wall does not imply a stable static particle-like lump in three dimensions.

For a static scalar configuration define

\[
T
=
\int d^d x\,
|\nabla f|^2,
\]

and

\[
V
=
\int d^d x\,
U(f^2).
\]

Under

\[
f_\lambda(x)
=
f(\lambda x),
\]

the energy becomes

\[
E(\lambda)
=
\lambda^{2-d}T
+
\lambda^{-d}V.
\]

Stationarity at \(\lambda=1\) requires

\[
(2-d)T-dV=0.
\]

For \(d=3\),

\[
-T-3V=0.
\]

Because the default potential is nonnegative,

\[
T\ge0,
\qquad
V\ge0.
\]

The only static configuration satisfying the condition is therefore the trivial one with

\[
T=V=0.
\]

So the amplitude field alone cannot produce a nontrivial static finite-energy scalar particle in three dimensions.

## Consequence for the engine

This narrows the particle-emergence problem.

A stable 3D localized excitation must evade the static scalar Derrick constraint through at least one additional ingredient, for example:

* harmonic time dependence and conserved U(1) charge,
* dynamical gauge fields,
* topological winding,
* higher-derivative structure,
* multi-field coupling,
* or another nonredundant stabilizing mechanism.

The repository already contains the first two candidate routes: time-harmonic charged radial matter and fully coupled compact U(1) dynamics.

## Next creator question

> Which existing nonstatic or gauge-coupled branch actually survives long-time nonlinear evolution with bounded radius, bounded peak amplitude, conserved charge, and controlled energy drift?

That is now a sharper question than simply asking whether a localized profile can be written down.
