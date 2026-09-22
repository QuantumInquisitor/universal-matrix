# Q-Ball Mapping Convergence Audit v0.1

## Purpose

Near the refined charged-matter energetic threshold, the first 3D persistence
scan found that a radial point with (E/Q>m_{\rm free}) mapped to a Cartesian
state with (E/Q<m_{\rm free}).

The relative mapping error was small, but the point was close enough to the
threshold that the energetic classification changed.

This audit measures that effect directly across increasingly resolved Cartesian
grids.

Implementation:

- `src/qball_mapping_convergence.py`

Tests:

- `tests/test_qball_mapping_convergence.py`

## Audit target

The executable audit reconstructs the refined continuation and selects the
accepted radial branch point immediately above the (E/Q=m_{\rm free})
crossing.

It then maps that exact radial solution to several centered odd Cartesian grids
and records for each grid:

- spacing;
- physical half-width;
- Cartesian (E/Q);
- relative difference from radial (E/Q);
- radial threshold side;
- Cartesian threshold side;
- whether the threshold side is preserved.

## Current grid sequence

The initial audit sequence is:

[
25^3, h=0.5,
]

[
33^3, h=0.4,
]

[
41^3, h=0.3.
]

This changes both resolution and box size moderately while keeping the origin
exactly centered.

The first goal is diagnostic, not a formal continuum extrapolation.

## Interpretation

If finer mappings preserve the radial threshold side, the earlier flip is a
coarse discretization effect.

If the classification continues to flip, the mapping procedure or finite-box
energy estimator requires further improvement before radial and 3D energetic
thresholds can be compared directly.

## Next step

Once a threshold-preserving mapping regime is identified, rerun direct and
perturbed persistence on that regime and only then compare the persistence
boundary with the radial energetic crossing.
