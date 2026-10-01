# Geometry-derived reduced elasticity

This checkpoint advances P04/P07 without making stable breathing a prerequisite.
It replaces an unspecified modal restoring law with a separately callable,
geometry-dependent potential for six panel midsurfaces and twelve bridge axial
elements. It does not yet replace the restoring law in the dynamics experiments.
The old quadratic-law results remain intact as independent comparisons.

## Geometry, ownership and reference

The geometry is the pinned 22-body specimen used by `fold_kinematics.md`:
six panels, four hub markers and twelve bridges with stable body IDs. All panel
vertices and bridge endpoints are replayed against the original-source fixture.
The chosen reference is `q0=(1,pi/12)`, not the original path's zero-angle endpoint.
It is declared stress-free for this law; no measured rest stress is inferred.

Each panel and bridge owns one reduced elastic energy. The four hubs have no
constitutive energy in this version. Existing lumped masses are unchanged.
These are reduced elements, not an integration over a disjoint solid volume:
there is no new density-derived mass or duplicated overlapping-envelope mass.
The two coordinates still impose compatible movement of the whole specimen and
suppress other deformation modes. Free-joint motion or its stability is not
established by this reduction.

## Declared surface law and virtual work

For panel ray pair `(i,j)`, define `A=ell*s*[r_i(theta),r_j(theta)]`, a 3-by-2
map from the original clipped polygon's coefficient coordinates into metres.
Let `A0=A(q0)`, `B=(A0^T A0)^(-1/2)` and

```
Egreen = (B A^T A B - I)/2
Aref = coefficient_polygon_area * sqrt(det(A0^T A0))
lambda = Young * nu/(1-nu^2)
mu = Young/(2*(1+nu))
Vpanel = Aref * t0 * [lambda*tr(Egreen)^2/2 + mu*tr(Egreen^2)]
```

This is a specified quadratic Green-strain membrane model using effective
plane-stress coefficients. The implementation computes strain from
`B*(A^T A-A0^T A0)*B/2`, giving exact zero at its reference. Analytic ray
derivatives give each coordinate's strain derivative and potential gradient.
The restoring generalized force is **minus** that gradient. Its components
have units J per unit scale and J/radian; they are not two Cartesian forces.
An independent energy difference checks virtual work rather than reusing the
gradient to generate the expected answer.

The potential is invariant under rigid spatial rotations. At fixed unit scale,
folding stretches panels 13 and 23; panel 03 rotates without metric strain,
while panels 01, 02 and 12 are unchanged. Uniform scaling gives
`Egreen=(s^2-1)I/2`, supplying a separate analytic energy/force control.

## Axial bridges and missing mechanisms

Each original bridge runs from `ell*s*0.5*r_i` to
`ell*s*(0.5*r_i+0.17*r_j)`. Its length is `L=0.17*ell*s`, independent of theta.
With reference length `L0=0.17*ell`, the optional axial energy is
`Vbridge=EA*(L-L0)^2/(2*L0)`. It gives scale stiffness and zero fold stiffness.
It cannot stand in for bridge bending, torsion or joint compliance.

The example uses synthetic values: `ell=0.1 m`, Young=1000 Pa, nu=0.3,
effective reference membrane thickness `t0=1e-4 m`, and bridge `EA=0.1 N`.
The thickness is an independent constitutive input; it is not the collision
envelope radius. Neither modulus nor bridge EA is measured material data.
The model omits bending, plasticity, buckling, fracture, contact/friction,
hub constitutive behavior and a through-thickness material map. Supports and
constraints remain those implicit in the prescribed two-coordinate kinematics.

## Validation

Thirty-three tests passed. Nine original fixture configurations give 198 body
vertex-set comparisons with maximum position error 2.776e-17 m. Reference
energy and gradient are exactly zero; the uniform-scale formula differs by
3.05e-20 J. Independent finite differences agree with the analytic gradient
within 1.35e-13 per coordinate in the sampled controls.

The reference tangent in the declared scale/angle coordinates is approximately

```
[[ 0.04476790617, -0.00060096303],
 [-0.00060096303,  0.00100212111]]
```

It is symmetric within 3.07e-13 and positive definite. Its numerical eigenvalues
are coordinate-dependent stiffness diagnostics, not physical modal frequencies.
Membrane-only, axial-only and zero-law controls expose which element supplies
each restoring term. These results validate this static reduced law, not a
complete material specimen or autonomous motion.

## Reproduction and next integration

```sh
uv run python scripts/report_fold_constitutive.py --output artifacts/fold-constitutive/report.json
uv run --extra visualization python scripts/plot_fold_constitutive.py --input docs/experiments/fold-constitutive-summary.json --output artifacts/fold-constitutive/geometry-energy.png
```

Next, connect this potential's negative gradient to the existing owned inertia
and geometric inertial terms as an explicit alternative to the old quadratic
potential. Verify conservative/passive/driven energy accounts before expanding
joint laws or recursive coupling. Do not add both restoring potentials silently.
The static plot exposes actual midsurfaces, bridge centerlines and omitted hubs;
it is not integration with the XR viewer or a new collision certificate.
