# Toroidal uniform-scale similarity audit v0.1

## Purpose

The spacing and clearance audits vary shell gap and bend margin while the other
geometric lengths remain fixed. Before deriving a recursive or scale-consistent
clearance law, the engine must first pass the simpler geometric requirement of
uniform similarity covariance.

This checkpoint scales the complete routed construction by one positive factor.

## Length set

The similarity factor is applied to:

- base channel inner radius;
- shell width and shell gap;
- axial shell separation;
- junction length and inner/outer radii;
- junction separation gap;
- connector length;
- channel length;
- global node gap;
- global edge-routing gap;
- smooth-bend radius margin.

The graph, signed currents, topology, and angular collision-sampling grid remain
unchanged.

## Similarity contract

For a reference geometry with scale factor $s=1$, a uniformly scaled geometry
uses

$$
L_i(s)=sL_i(1)
$$

for every declared length.

A pure similarity transformation should preserve the collision/free
classification because all dimensionless geometric ratios are unchanged.

When a collision exists, dimensional penetration should satisfy

$$
p(s)=s,p(1),
$$

so the normalized penetration

$$
widehat p=rac{p(s)}{s}
$$

should remain invariant up to floating-point tolerance.

## Reference cases

The focused regression uses sampled refined-bracket points already established
by the clearance audit:

- $(g,m)=(2.5,0.05)$, colliding side;
- $(g,m)=(3.0,0.05)$, collision-free side;
- $(g,m)=(6.5,0.005)$, colliding side;
- $(g,m)=(8.25,0.005)$, collision-free side.

Each case is evaluated at scale factors 0.5, 1, and 2.

These labels describe the coarse `(13, 5, 24)` sampling grid only. In
particular, `(3.0, 0.05)` has two detected collisions on the denser
`(21, 9, 48)` grid and on a half-step-shifted coarse grid. Thus its coarse
"collision-free" classification is a missed collision, not continuous
clearance. The similarity test remains a fixed-grid covariance check. See
`toroidal_sampling_reliability_v0.1.md` for the resolution comparison.

## Evidence boundary

This audit can establish numerical similarity covariance for the tested Vesica
construction and sampling resolution.

It does not establish:

- Flower/Tree scale consistency;
- recursive-depth invariance;
- an optimal clearance ratio;
- a physical length scale;
- a dynamics law for adaptive or morphing geometry;
- that every possible similarity factor is numerically stable under finite
  precision.

## Next gate

If uniform similarity covariance passes, the next test is not another arbitrary
parameter scan. It is a topology-aware dimensionless comparison across Vesica,
Flower/Tree, and recursive depths using the same normalized geometric ratios.

That is the first appropriate place to test whether the routed geometry behaves
like a scale-consistent recursive or morphing fractal construction.
