# Matter Amplitude Modes v0.1

## Status

This note derives the first independent amplitude branch directly from the repository's existing classical complex scalar matter dynamics.

It does not add a new matter field.

The derivation uses the same potential and lattice equation already implemented in `src/classical_matter_dynamics.py`.

## Existing matter equation

The matter potential is

\[
U(\rho)
=
m^2\rho
+
\lambda_4\rho^2
+
\lambda_6\rho^3,
\qquad
\rho=|\Phi|^2.
\]

The current fixed-link matter equation is

\[
\ddot\Phi
=
\Delta_A\Phi
-
U'(\rho)\Phi.
\]

For a uniform zero-link nonzero stationary background,

\[
\Phi_0=R,
\qquad
\rho_0=R^2>0,
\]

stationarity requires

\[
U'(\rho_0)=0.
\]

## Radial and phase decomposition

Write a small perturbation around a real background as

\[
\Phi
=
R+h+i y.
\]

At a nonzero stationary density, the linearized tangential mode is

\[
\ddot y
=
\Delta y,
\]

while the radial mode is

\[
\ddot h
=
\Delta h
-
m_R^2 h,
\]

with

\[
\boxed{
m_R^2
=
2\rho_0 U''(\rho_0).
}
\]

Therefore the exact unit-spacing cubic-lattice branches are

\[
\boxed{
\omega_{\mathrm{phase}}^2(\mathbf{k})
=
4
\sum_a
\sin^2\frac{k_a}{2}
}
\]

and

\[
\boxed{
\omega_{\mathrm{radial}}^2(\mathbf{k})
=
4
\sum_a
\sin^2\frac{k_a}{2}
+
2\rho_0U''(\rho_0).
}
\]

The radial amplitude mode is a genuinely independent degree of freedom. It cannot be removed by the canonical polarity-to-phase identity.

## Default repository potential

The current default potential is

\[
U(\rho)
=
\rho
-
2\rho^2
+
\rho^3.
\]

Its nonzero stationary densities satisfy

\[
1-4\rho+3\rho^2=0,
\]

giving

\[
\rho=\frac13,
\qquad
\rho=1.
\]

At

\[
\rho=\frac13,
\]

the radial gap squared is

\[
m_R^2=-\frac43,
\]

so that stationary point is radially unstable.

At

\[
\rho=1,
\]

the radial gap squared is

\[
m_R^2=4,
\]

and the radial gap is

\[
\omega_R(0)=2.
\]

Thus the current default matter potential already contains a stable nonzero background with two distinct linear branches:

* a gapless phase branch,
* a gapped radial amplitude branch.

## Exact rotor reduction of the phase branch

For fixed amplitude

\[
\Phi=R e^{i\theta},
\qquad
\rho=R^2,
\]

the kinetic energy is

\[
|\dot\Phi|^2
=
\rho\dot\theta^2.
\]

A unit-coefficient spatial matter link contributes

\[
\left|
e^{iA_{xy}}\Phi_y-\Phi_x
\right|^2
=
2\rho
\left[
1-\cos\Delta_{xy}
\right].
\]

Matching this to

\[
H_{\mathrm{rotor}}
=
\frac{p_\theta^2}{2I}
+
\kappa
\left[
1-\cos\Delta
\right]
\]

gives

\[
\boxed{
I=2\rho,
\qquad
\kappa=2\rho.
}
\]

Therefore

\[
\frac{\kappa}{I}=1
\]

in the scalar field's native lattice units.

This completes the fixed-amplitude reduction more fully than the earlier coupling-only bridge: both the rotor coupling and rotor inertia follow from the same matter density.

## Why this matters

The previous polarity-dispersion result showed that canonical polarity alone does not generate a second stable linear band once the exact pi offset is compensated.

Amplitude motion does.

This gives the first minimal nonredundant extension with a mathematically distinct stable branch.

## What remains open

This does not yet establish a particle spectrum.

The next questions are:

1. whether the stable radial branch supports localized nonlinear defects,
2. whether charged time-dependent lumps are dynamically stable rather than only variationally favored,
3. how compact gauge dynamics modify the phase and radial branches,
4. whether the phase mode is converted into a gauge-mass mode when the gauge field is dynamical,
5. whether scale coupling changes the radial gap,
6. whether any dimensionless gap can be tied to an observed mass without calibration.

## Next creator question

> Can the stable nonzero matter background and its radial amplitude mode support long-lived localized excitations under the full nonlinear lattice dynamics, without assigning particle species by hand?
