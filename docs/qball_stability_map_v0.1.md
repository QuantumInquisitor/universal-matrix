# Q-Ball Stability Evidence Map v0.1

## Purpose

This layer turns the continued charged-matter branch into an explicit evidence
map without reducing different diagnostics to one stability score.

Implementation:

- `src/qball_stability_map.py`

Tests:

- `tests/test_qball_stability_map.py`

## Evidence channels

The map keeps four questions separate.

1. Is the stationary radial solution accepted by the continuation checks?
2. Is (E/Q < m_{\rm free}), giving the current energetic binding diagnostic?
3. Do neighboring branch secants have the recorded (dQ/d\omega) sign?
4. Does the mapped 3D state survive the direct and perturbed finite-time tests?

A point can pass one channel and fail another. That disagreement is information
and must not be hidden by averaging the tests into one scalar score.

## Threshold refinement

The existing coarse continuation places an (E/Q=m_{\rm free}) crossing
between accepted branch points. The new helper identifies that bracket and
generates evenly spaced interior amplitudes for a denser continuation pass.

The next numerical batch should therefore resolve the threshold locally before
claiming its location more precisely.

## Persistence attachment

Direct and perturbed persistence results are attached to the exact branch point
that generated them. The map records them independently.

Passing both finite-time tests means only that the tested numerical state stayed
inside the explicit survival window for the simulated duration. It is not a
proof of spectral, asymptotic, quantum, or experimental stability.

## Intended stability diagram

For each accepted amplitude, record at minimum:

- central amplitude;
- frequency (omega);
- (E/Q);
- whether (E/Q<m_{\rm free});
- left and right (dQ/d\omega) secants when available;
- direct 3D survival result when run;
- perturbed 3D survival result when run.

The first useful diagram is therefore an evidence-alignment plot, not a binary
stable/unstable chart.

## Next creator question

> After refining the energetic threshold, do the branch-slope sign, the
> (E/Q=m_{\rm free}) crossing, and the direct perturbative survival boundary
> coincide, remain ordered, or separate?

If they separate, that separation is physically more informative than forcing a
single stability label.
