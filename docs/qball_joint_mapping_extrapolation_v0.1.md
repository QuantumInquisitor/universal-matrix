# Q-Ball Joint Mapping Extrapolation v0.1

## Purpose

The separate spacing and volume audits showed that both effects move the
Cartesian (E/Q) estimate upward toward the refined radial value.

This layer fits both effects simultaneously instead of extrapolating one while
holding the other fixed.

Implementation:

- `src/qball_joint_mapping_extrapolation.py`

Tests:

- `tests/test_qball_joint_mapping_extrapolation.py`

## Model

For a localized branch point with asymptotic decay rate

[
mu=sqrt{m_{m free}^2-omega^2},
]

the Cartesian mapping data are fit to

[
rac{E}{Q}(h,L)
=
c_0+c_h h^2+c_L T(L;mu),
]

where (h) is lattice spacing, (L) is physical box half-width, and

[
T(L;mu)
=
e^{-2mu L}
left(
rac{L^2}{2mu}
+
rac{L}{2mu^2}
+
rac{1}{4mu^3}
ight).
]

The tail basis is the integrated leading (r^2e^{-2mu r}) form expected for
a localized radial tail.

The fitted intercept (c_0) is the joint (h	o0), (L	oinfty) diagnostic.

## Grid family

The initial joint fit uses

[
hin{0.5,0.375,0.3,0.25}
]

and

[
Lin{6.0,7.5,9.0},
]

giving twelve centered Cartesian grids.

## Safeguards

The report includes:

- fitted intercept;
- distance from the radial (E/Q);
- spacing coefficient;
- tail coefficient;
- RMS residual;
- maximum absolute residual;
- design-matrix condition number.

A close fit is numerical evidence of a consistent extrapolation model, not a
proof that higher-order lattice and boundary corrections vanish.
