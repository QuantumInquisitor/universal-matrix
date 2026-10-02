# Recursive exact zero-thickness clearance audit

The earlier placement audit used module bounding spheres to obtain conservative separation
conditions. Those spheres are useful for pruning but are not exact collision certificates,
especially across nested generations.

This checkpoint evaluates the actual source geometry.

## Geometry

Each material module contains:

- six panel midsurface polygons;
- twelve bridge line segments;
- four hub points.

No physical body thickness is introduced. Collision therefore means intersection of the declared
zero-thickness source primitives within a small numerical tolerance.

Distances are computed from exact primitive combinations:

- point-point;
- point-segment;
- segment-segment;
- point-triangle;
- segment-triangle;
- triangle-triangle.

Panel polygons are triangulated as a fan from their first vertex. The source panel polygons are
planar by construction.

Axis-aligned bounding boxes and whole-module bounding spheres are used only as lower-bound
pruning devices. They cannot create a collision or certify the final minimum by themselves.

## State coverage

The three Seed-axis candidates were previously proven rigidly equivalent, so this audit evaluates
one canonical axis only.

Every pair among the 15 recursive modules is tested. For each module pair, the full declared
nine-state q-grid is combined independently, giving 81 relative state pairs. This pairwise
independent grid is stronger than synchronizing every module to the same q value: if every module
pair is separated for all 81 state pairs at a sampled vessel ratio, any assembly built from those
sampled module states is pairwise collision-free at that ratio.

## Vessel-ratio scan

No physical vessel/module ratio is selected.

The coarse scan begins at the previously established local spherical containment ratio and samples
larger multiples. The final sample is the previous conservative all-module sphere bound, which is
a sufficient outer collision-free sample. The exact body geometry can therefore replace that
large sphere bound with a narrower sampled collision/free bracket when possible.

This is still finite sampling. The first sampled collision-free ratio is not a continuous
clearance theorem.

## Next step

If the coarse audit finds a mixed collision/free outcome, refine only the first sampled bracket
with additional vessel-ratio samples, preserving the same independent state grid and exact body
distance kernel.

Physical thickness, manufacturing margin and a literal connector attachment geometry remain
separate later inputs.
