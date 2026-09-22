# Q-Ball Mapping Error Decomposition v0.1

## Purpose

The radial-to-Cartesian convergence audit showed that the near-threshold
Cartesian energy-per-charge estimate moves toward the radial value as the grid
is refined, but the threshold side is still not preserved at the tested
resolution.

This layer separates two numerical effects that were previously mixed:

1. lattice-spacing error;
2. finite-volume truncation error.

Implementation:

- `src/qball_mapping_error_decomposition.py`

Tests:

- `tests/test_qball_mapping_error_decomposition.py`

## Resolution series

The resolution series holds the physical half-width fixed at

[
L=6
]

while changing lattice spacing:

[
h=0.5, 0.4, 0.3, 0.25.
]

The corresponding centered odd grids are:

[
25^3, 31^3, 41^3, 49^3.
]

Because the physical box size is fixed, movement in Cartesian (E/Q) along
this series is primarily a spacing-resolution effect.

A linear diagnostic fit in (h^2),

[
E/Q(h)=c_0+c_2h^2,
]

is used only to estimate an (h	o0) intercept. It is not treated as a formal
continuum theorem.

## Volume series

The finite-volume series holds

[
h=0.3
]

fixed and varies the physical half-width:

[
L=4.8, 6.0, 7.2, 8.4.
]

The corresponding centered odd grids are:

[
33^3, 41^3, 49^3, 57^3.
]

Movement along this series isolates sensitivity to truncating the localized
profile at the box boundary.

## Interpretation

If the resolution span dominates while the volume series is nearly stationary,
the mapping discrepancy is mainly a lattice-spacing error.

If the volume span remains comparable, larger physical domains are also
required.

Only after both effects are controlled should the 3D persistence boundary be
compared directly with the radial (E/Q=m_{\rm free}) crossing.
