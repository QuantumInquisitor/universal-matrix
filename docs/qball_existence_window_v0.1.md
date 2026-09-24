# Q-Ball Existence Window v0.1

## Status

This note derives a necessary analytic frequency window for the repository's existing time-harmonic charged scalar matter ansatz.

It does not prove that a numerical branch is stable or that a particle has been identified.

## Time-harmonic ansatz

The radial matter solver uses

$$
\Phi(t,r)
=
e^{i\omega t}f(r).
$$

For

$$
U(\rho)
=
m^2\rho
+
\lambda_4\rho^2
+
\lambda_6\rho^3,
\qquad
\rho=f^2,
$$

the radial equation is

$$
f''
+
\frac{2}{r}f'
=
(m^2-\omega^2)f
+
2\lambda_4 f^3
+
3\lambda_6 f^5.
$$

## Necessary localization window

Exponential decay toward the zero-field vacuum requires

$$
\omega^2<m^2.
$$

A nontrivial interior region requires the effective radial potential to dip below its zero-field value, giving the necessary condition

$$
\boxed{
\min_{\rho>0}
\frac{U(\rho)}{\rho}
<
\omega^2
<
m^2.
}
$$

Because

$$
\frac{U(\rho)}{\rho}
=
m^2
+
\lambda_4\rho
+
\lambda_6\rho^2,
$$

the lower edge is analytic.

When

$$
\lambda_6>0,
\qquad
\lambda_4<0,
$$

the minimizing density is

$$
\rho_*
=
-\frac{\lambda_4}{2\lambda_6},
$$

and

$$
\left(
\frac{U}{\rho}
\right)_{\min}
=
m^2
-
\frac{\lambda_4^2}{4\lambda_6}.
$$

## Default repository potential

For

$$
m^2=1,
\qquad
\lambda_4=-2,
\qquad
\lambda_6=1,
$$

the minimizing density is

$$
\rho_*=1,
$$

and

$$
\left(
\frac{U}{\rho}
\right)_{\min}
=
0.
$$

Therefore the necessary time-harmonic localization interval is

$$
\boxed{
0<\omega^2<1.
}
$$

Equivalently,

$$
0<\omega<1.
$$

The asymptotic decay constant is

$$
\mu_\infty
=
\sqrt{1-\omega^2}.
$$

## Why this matters numerically

The current radial boundary-value solver can converge to different mathematical branches depending on its initial guess.

The analytic window provides a hard branch filter:

* solutions with $\omega\le0$ are outside the intended positive-charge branch,
* solutions with $\omega\ge1$ do not have the required exponential zero-vacuum tail,
* convergence alone is not sufficient,
* nodelessness, virial residual, $E/Q$, and time persistence must still be checked.

## Relation to the exact wall

The same default potential has

$$
U(f^2)=f^2(1-f^2)^2
$$

and a degenerate nonzero vacuum at $f=1$.

That fact drives the lower frequency bound to zero.

The domain wall and the charged Q-ball are different objects:

* the wall interpolates between degenerate vacua,
* the Q-ball uses time-dependent phase rotation to localize charge while approaching the zero vacuum at spatial infinity.

## Next numerical requirement

A branch scan should not solve each central amplitude independently from a generic Gaussian.

It should use numerical continuation so that each converged nodeless solution seeds its neighbor, while rejecting points outside

$$
0<\omega<1.
$$

That is the next solver-quality upgrade before any claim of a stable localized particle-like branch.
