# Radial Matter Continuation v0.1

## Status

This is a numerical reliability upgrade for the existing time-harmonic charged matter solver.

It does not by itself prove nonlinear stability.

## Problem with isolated solves

The existing radial boundary-value solver is mathematically valid for a single initial guess, but solving every central amplitude independently from a generic Gaussian can converge to different branches.

A converged solver status therefore does not guarantee branch continuity.

## Continuation strategy

The continuation layer performs the following sequence:

1. solve a trusted initial central amplitude,
2. interpolate that converged radial profile onto the next grid,
3. rescale the profile to the neighboring central amplitude,
4. seed the next solve with the previous frequency,
5. require solver convergence,
6. require a nodeless profile,
7. require the analytic Q-ball frequency window,
8. require a small relative virial residual,
9. only then allow the point to seed the next solve.

This makes branch identity explicit.

## Analytic branch filter

For the default potential, the previous existence-window result requires

$$
0<\omega<1.
$$

A converged point outside that interval is rejected as a continuation seed.

## Default branch result

Using the ordered amplitudes

$$
A_0
=
0.5,,
0.6,,
0.7,,
0.8,,
0.9,,
1.0,
$$

the continuation remains converged, nodeless, and inside the analytic frequency window.

The solved frequency decreases continuously along this branch, reaching approximately

$$
\omega(A_0=1)
\approx
0.80015.
$$

At the final point,

$$
\frac{E}{Q}
<
m_{\rm free}=1.
$$

In the current normalization the representative value is approximately

$$
E/Q
\approx
0.9873.
$$

This is stronger than the earlier isolated representative solve at $A_0=0.5$, which lies above the free-mass threshold.

## What this establishes

The repository now has a controlled nodeless charged branch containing at least one point that satisfies the energetic diagnostic

$$
E/Q<m_{\rm free}.
$$

That is a classical stability candidate.

It is not yet a proof of dynamical persistence.

## What remains required

The next test is direct real-time evolution of the continued below-threshold point after mapping it into the 3D lattice.

The relevant diagnostics already exist:

* charge drift,
* energy drift,
* RMS-radius change,
* peak-amplitude change.

The continued point should also be perturbed, because mere survival of an exactly prepared profile is weaker than nonlinear stability.

## Next creator question

> Does the continued below-threshold charged solution at approximately
> $A_0=1$, $\omega\approx0.80015$ remain localized under long-time
> 3D evolution and small perturbations?

That is now the highest-value particle-emergence test.
