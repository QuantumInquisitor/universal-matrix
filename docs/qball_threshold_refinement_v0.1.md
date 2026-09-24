# Q-Ball Threshold Refinement v0.1

## Purpose

This layer narrows the energetic binding threshold on the already accepted
continued charged-matter branch.

Implementation:

- `src/qball_threshold_refinement.py`

Tests:

- `tests/test_qball_threshold_refinement.py`

The target condition is

$$
E/Q = m_{\rm free}.
$$

The crossing is an energetic diagnostic only. It is not treated as a universal
nonlinear stability boundary.

## Adaptive refinement

The procedure begins from the coarse accepted amplitudes

$$
A_0 = 0.5,0.6,0.7,0.8,0.9,1.0.
$$

After solving the full ordered branch, the code identifies the first accepted
neighboring pair that brackets the threshold. It then inserts evenly spaced
interior amplitudes only inside that bracket, resolves the complete ordered
continuation, and repeats.

This preserves branch continuity while concentrating numerical work where the
energetic transition actually occurs.

## Reported quantities

The refinement result records:

- all continuation records from the final pass;
- the interpolated threshold crossing;
- final accepted bracket width;
- number of completed refinement rounds.

A companion diagnostic extracts the branch secant containing the crossing and
reports:

- $dQ/d\omega$;
- $dE/dQ$;
- midpoint $\omega$;
- relative error of $dE/dQ\approx\omega$;
- sign of $dQ/d\omega$.

These are retained as separate measurements.

## Current numerical target

Two rounds with four interior amplitudes per round reduce the original
$[0.9,1.0]$ central-amplitude bracket to a width of at most approximately
$0.004$, subject to the same continuation acceptance criteria.

The exact interpolated crossing is intentionally produced by the solver and is
not hard-coded into the implementation.

## Interpretation boundary

A refined $E/Q=m_{\rm free}$ location establishes where the present
classical energetic binding diagnostic changes sign along this branch.

It does not establish:

- spectral stability;
- asymptotic nonlinear stability;
- quantum stability;
- robustness against arbitrary perturbations;
- stability after coupling to dynamical gauge fields;
- correspondence to an observed particle.

## Next step

Use selected points on both sides of the refined energetic crossing as inputs to
direct and perturbed 3D evolution. Then compare the resulting persistence
boundary against the energetic crossing and the local branch-slope behavior.
