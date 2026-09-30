# Folding adapter: inherited geometric domain

30 September 2026. Independent source audit for the proposed reduced coordinates
`q=(s,theta)`. This establishes how an existing clearance result can be reused;
it supplies no new material law or full solid deformation map.

## Source and conclusion

The pinned source is PR119 commit
`60a7fd60f57d73b89ea5397db58a3ff5d291556c`:

- [Relative motion](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_relative_motion_control.py): `reference_rays`, `compliant_rays`.
- [Finite panels](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_finite_panel_control.py): `pentagon_coefficients`, `panel_vertices`, `deformation_metrics`, `separation_bound`.
- [Connected specimen](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_connected_control.py): `bodies`, `contact_check`, `_intervals`, `audit_connected_cycle`, `scene`.
- [Breathing overlay](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_breathing_control.py): `BreathingCycle.state`, `BreathingCycle.panel`.

**The complete rectangle `s in [0.9,1.1]`, `theta in [0,pi/6]` inherits the
existing separation/contact classification, conditional on exact geometric
equivalence and successful reproduction of the pinned audit.** This follows
from surjectivity of the old angle path and positive similarity, rather than
from interpolating a sampled two-coordinate grid. It resolves the specific
domain question left open in `fold_material_mapping_audit.md`; arbitrary
two-coordinate extensions would not enjoy this implication.

## Why every angle is covered

`compliant_rays` uses the angle `theta(p)=(pi/6)*sin(pi*p)^2` on `p in [0,1]`.
It is continuous and increases from zero to `pi/6` on `[0,1/2]`. For any allowed
theta, one preimage is

```
p(theta) = asin(sqrt(6*theta/pi))/pi.
```

The inverse is only a coverage argument; its derivative is singular at the
endpoints and should not be used to compute adapter velocities. Differentiate
the direct sine/cosine rotation with respect to theta instead.

`compliant_rays` fixes rays 0,1,2 and writes ray 3 as
`c*a + R*(cos(theta)*u + sin(theta)*w)`. Here `a=ray0`, `c=ray3 dot a`,
`R=sqrt(1-c*c)`, `u` is the normalized transverse part of reference ray 3,
and `w` is the normalized component of reference ray 1 perpendicular to both
`a` and `u`. A new cross-product convention must reproduce this signed `w`;
an opposite rotation is outside this inherited angle path.

## Why independent positive size is covered

For each source body with coefficient vertices `C_b` and radius `r_b`, define

```
B_b(theta) = convex_hull(C_b * rays(theta)) + ball(r_b)
B_b(s,theta; ell) = ell*s*B_b(theta),  ell > 0.
```

The plus sign denotes a Minkowski sum. For any sets A and B and positive k,
`distance(k*A,k*B)=k*distance(A,B)`. Consequently each unscaled retained
clearance lower bound delta becomes `ell*s*delta`, bounded below by
`ell*0.9*delta` on the rectangle. This is a pointwise configuration result
and imposes no correlation between s and theta, nor a time speed limit.

The source `_intervals` first audits **unscaled** folding geometry, using
midpoint vertex support gaps minus analytic motion bounds and the sum of
offset radii. `audit_connected_cycle` only afterwards multiplies the minimum
accepted margin by `1-amplitude`. With amplitude 0.1 that factor is 0.9.
The source does not rely on the old breathing factor occurring at a particular
angle. Source speed bounds prove coverage between phase samples; a new time
trajectory need not have the old phase speed to stay in the certified set.

This implication fails if only vertex positions scale while radii, thickness,
hub balls, attachment balls, or some bodies remain fixed. It also fails for
nonuniform scale, extra relative motions, altered coefficients or radii,
negative theta, theta greater than `pi/6`, or an opposite signed rotation.

## Intended contacts remain localized

The 22 bodies comprise six radius-0.01 offset panel cores, four radius-0.05
hubs and twelve radius-0.008 bridge capsules of centerline length 0.17. Panel
coefficient collars are 0.15. The 231 pairs comprise 195 separated pairs and
three classes of 12 intended attachment pairs each:

- Bridge to its own hub: any intersection is inside that hub by definition.
- Bridges sharing a hub: each initial length 0.042 plus its radius-0.008
  offset lies in the radius-0.05 hub; their remaining tails are audited apart.
- Bridge to its own panel: a terminal length 0.072 plus radius 0.008 lies in
  the radius-0.08 ball around the bonded tip; the remaining prefix is audited
  apart from the panel. The attachment ball is a bounding region, not a body.

These inclusions and trimming fractions survive the same positive scaling.
There is no positive gap assertion for intentionally bonded whole bodies.
Bodies outside permitted contact regions retain their separation bounds.

## Numerical and material limits

The [pinned report](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/docs/lynchpin_connected_control_v0.1.md)
records 1,208 intervals and a smallest retained 3D bound after factor 0.9 of
`0.00003773014616157734` reference units. This document inspected source and
the published result; it does not itself claim to have rerun that computation.
The integrating experiment must record its own reproduced count, acceptance,
bound and source provenance before presenting a new validation result.

The integrating run subsequently executed the original auditor again in 3D,
with amplitude 0.1 and maximum depth 10. It reproduced acceptance, 231 pairs,
1,208 intervals and bound `3.773014616157734e-05` reference units. The result
and the 13 executed source/dependency hashes are saved in
`experiments/fold-original-source-fixture.json`. This is new numerical evidence
with the same floating-point limitations, not an upgrade to interval arithmetic.

Support gaps are valid geometric lower bounds in exact arithmetic regardless
of optimizer convergence. The implementation uses floating-point support and
speed calculations, accepts margins above `1e-10`, and does not use
outward-rounded interval arithmetic. Thus it is a continuous-path numerical
certificate with analytical bounds, not a machine-verified interval proof.

Fixed coefficient labels give a material-point correspondence for panel
midsurfaces, bridge centerlines and hub centers. They do not by themselves
assign every interior point in the offset solids, prevent incompatible maps
in overlapping bonded volumes, or define a through-thickness deformation
gradient. Positive similarity has Jacobian `s^3` when theta is held fixed;
this does not establish the Jacobian of an unspecified full folding map.

A surface/centerline lumped model must explicitly declare masses and their
ownership, avoid volume double counting, and limit its strain claims to the
mapped degrees of freedom. Clearance does not establish allowable material
strain, mechanical stability, contact forces, drive energy, autonomous motion
or the missing mapping to the separate 69-component flow assembly.
