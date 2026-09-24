# Toroidal inside-out inversion control v0.1

## Purpose

This is a first mathematical control for the proposed inside-out / outside-in
geometry. It defines a reversible endpoint map, checks existing collision
witnesses and flux transport, and identifies why simply blending to that map
does not provide a nonsingular motion. Existing geometry builders are unchanged.

## Map and domain

For center $c$ and positive radius $R$, spherical inversion is

$$
F(x)=c+\frac{R^2}{\lVert x-c\rVert^2}(x-c),\qquad x\ne c.
$$

It is its own inverse. Radial distances obey $r'=R^2/r$, so points inside and
outside the radius-$R$ sphere exchange places, and the sphere itself is fixed.
The center is excluded; it must not be silently mapped to a finite point.

Writing $n=(x-c)/\lVert x-c\rVert$ and $\alpha=R^2/\lVert x-c\rVert^2$ gives

$$
J=\alpha(I-2nn^T),\qquad \det J=-\alpha^3.
$$

The map is smooth and orientation reversing away from its pole. It is a new
diagnostic map, not a change to the positive-Jacobian contract of the existing
annular bend builder. Nonfinite and unrepresentable inputs/results are rejected.

## Flux and normal orientation

The default convention uses signed Piola transport $v'=Jv/\det J$ and
parametrized area transport $a'=\det J\,J^{-T}a$. Their pairing preserves
$v'\cdot a'=v\cdot a$.

For outward normals of a mapped volume, both formulas instead use
$|\det J|$. The API exposes this as `outward=True` on both `piola_current` and
`map_area`. Mixing the two conventions reverses the signed flux for inversion.
An orientation reversal is not a loss or creation of current.

The signed Piola convention follows [DefElement's mapping definitions](https://defelement.org/finite-elements.html#mapping-finite-elements).
The distinction between determinant conventions is also discussed in
[Aznaran, Farrell, and Kirby, Transformations for Piola-mapped elements](https://arxiv.org/abs/2110.13224).
The inversion Jacobian, pole bounds, and interpolation obstruction above and
below are derived directly for this control.

## Existing collision witnesses

The report uses the gap-3, margin-0.05 Vesica geometry and the half-step-shifted
`(13, 5, 24)` grid, with inversion center `(0, 0, 0)` and radius 100 in the
implementation's coordinate units.

Both known collision witnesses remain intersections after inversion. This is
expected: an injective common map satisfies

$$
F(A\cap B)=F(A)\cap F(B).
$$

The implementation evaluates membership in image volumes through $F^{-1}=F$.
It transports known witnesses; it is not an independent transformed-volume
collision search and does not certify other network pairs.

Before accepting a pair, conservative enclosing balls must exclude the pole.
The bend lies inside a ball at its corner of radius `bend_radius + outer_radius`.
The straight annulus lies inside a ball at its midpoint of radius
`hypot(length/2, outer_radius)`. A failed bound means exclusion is unresolved,
not that the pole has been proved to intersect the volume.

The reference report retains 2 of 2 witnesses, has a minimum pole-clearance
lower bound of about 12.7042, round-trip point error below $10^{-10}$, and local
flux-pairing residual below $10^{-12}$. The reported minimum absolute Jacobian
is evaluated at the witnesses only, not minimized over the volumes.

Tests additionally compare the analytic Jacobian with finite differences,
integrate flux on an independently differentiated transformed bend cross
section for both current signs and normal conventions, and check numerical
divergence of the transformed field at an interior point.

## Why a straight morph is singular

For the interpolation $F_t(x)=(1-t)x+tF(x)$, the radial Jacobian eigenvalue is
$1-t-t\alpha$. It vanishes at

$$
t_* = \frac{1}{1+\alpha},\qquad 0<t_*<1.
$$

The reference collision points reach this singularity at approximately 0.7763
and 0.7857. A continuous family of nonsingular maps on a fixed three-dimensional
volume cannot change its determinant sign from positive to negative. This
does not rule out every meaning of inside-out geometry; surface eversion with
self-intersections, topology changes, and relative path rearrangements have
different admissibility conditions that must be stated separately.

## Next gate

The control verifies a reversible endpoint transformation and exposes its
limits. It does not remove collisions, supply a safe deformation trajectory,
or add adaptive dynamics or physical units. A useful next geometry candidate
must change the relative paths or choose an orientation-preserving deformation,
then check intermediate geometry, Jacobians, and flux using the sampling
reliability controls. Common inversion alone is not a collision repair.

Run `python -m src.toroidal_inversion_control` for the deterministic report.
