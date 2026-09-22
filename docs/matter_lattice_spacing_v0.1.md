# Matter Lattice Spacing Consistency v0.1

## Status

This change corrects a numerical consistency gap between the radial matter solver and the three-dimensional real-time matter dynamics.

It does not introduce a new physical scale. The lattice spacing remains a model input.

## Problem

The radial-to-Cartesian mapper already accepted a spacing parameter

\[
h.
\]

That spacing was used to place the radial profile on a Cartesian coordinate grid and to measure RMS radius.

However, the real-time matter dynamics still used the unit-spacing lattice Laplacian

\[
\Delta_{\rm lat}
\]

and unweighted site sums for energy and charge.

Therefore a profile mapped with

\[
h\ne1
\]

was geometrically sampled at one scale but dynamically evolved at another.

## Correct lattice operator

For cubic spacing \(h\), the gauge-covariant lattice Laplacian is

\[
\Delta_A\Phi(x)
=
\frac{1}{h^2}
\sum_i
\left[
e^{iA_i(x)}\Phi(x+\hat i)
+
e^{-iA_i(x-\hat i)}\Phi(x-\hat i)
-
2\Phi(x)
\right].
\]

The unit-spacing implementation is recovered exactly at

\[
h=1.
\]

## Volume normalization

Each lattice site represents volume

\[
h^3.
\]

Therefore the discrete charge is

\[
Q
=
2h^3
\operatorname{Im}
\sum_x
\Phi_x^*\Pi_x.
\]

The energy is

\[
E
=
h^3
\sum_x
\left[
|\Pi_x|^2
+
U(|\Phi_x|^2)
+
\sum_i
\frac{
|e^{iA_i(x)}\Phi_{x+\hat i}-\Phi_x|^2
}{h^2}
\right].
\]

Equivalently, each raw nearest-neighbor gradient sum carries an overall factor \(h\) in three dimensions.

## Persistence mapping

When a radial solution is mapped with spacing \(h\), the resulting
`ClassicalMatterDynamics` object now stores the same \(h\).

The persistence diagnostic uses that stored spacing by default.

If a caller supplies a separate diagnostic spacing that disagrees with the dynamics spacing, the calculation is rejected instead of silently mixing scales.

## Backward compatibility

The default remains

\[
h=1.
\]

Existing unit-spacing calls therefore retain their previous equations and numerical normalization.

## Why this matters

A continuum radial solution has a definite radial coordinate.

If it is sampled onto a three-dimensional lattice with spacing \(h\), then its finite-difference derivatives, integrated energy, integrated charge, and radius must all use that same \(h\).

Without this correction, a mapped charged lump can appear to change its energy-per-charge ratio or dynamics simply because the coordinate mapping and lattice operator use different scales.

## Verification targets

The implementation tests:

* the lattice plane-wave eigenvalue scales as \(1/h^2\),
* uniform charge scales as \(h^3\),
* uniform non-gradient energy scales as \(h^3\),
* nonunit-spacing free evolution conserves energy and charge,
* radial mapping transfers its spacing into the dynamics object,
* persistence rejects inconsistent diagnostic spacing.

## Next creator question

After this correction is merged, the continued below-threshold charged solution can be mapped into 3D without a hidden scale mismatch.

The next direct test is:

> Does the continued \(A_0\approx1\), \(\omega\approx0.80015\) solution remain localized under long-time three-dimensional evolution and under small perturbations when the radial and Cartesian discretizations use one consistent spatial scale?
