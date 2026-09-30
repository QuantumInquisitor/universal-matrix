# Finite pentagon control for the relative fold

This local extension turns the existing ray motion into explicit affine pentagon surfaces. It is a declared computational specimen, not a unique reconstruction of the patent geometry or a material model.

## Geometry and deformation

Start with a regular, unit-side pentagon in 2D with one vertex at the origin and its adjacent vertices on the two 108-degree boundary rays. Express its vertices in coefficients (a,b) of those rays. For panel ij, map each coefficient pair to a*r_i(p)+b*r_j(p), using the existing compliant ray cycle.

The 4D reference begins with regular pentagons. The 3D reference begins with the already declared tetrahedral corner deformation. Deformation is measured relative to that reference, not relative to an unstated stress-free material.

For a two-ray row matrix R, the surface metric is G=R R-transpose. Squared principal stretches are the generalized eigenvalues of G(p) relative to G(0); the area ratio is sqrt(det(G(p))/det(G(0))). These are geometrical stretches, not stresses or constitutive-law predictions. Each panel remains a planar convex affine image while its rays remain independent.

## Hinge exclusions and thickness

The full panels share the recovered hinge-ray edges. Uniformly thickening them makes their joint neighborhoods overlap. This experiment therefore evaluates only the convex cores clipped by a>=0.15 and b>=0.15. The coefficient collar is not a constant physical clearance width. Removed regions are not implemented hinges, and the remaining cores alone are not a connected mechanical assembly.

Give each core an isotropic offset radius 0.01, so the sum of two radii is 0.02. In 3D this is a rounded finite-thickness panel body. In 4D it is a mathematical tubular neighborhood, not a claim about physical material in a fourth dimension. All units are dimensionless.

## Continuous clearance argument

At each interval midpoint, a projected optimization searches for a separating direction. Solver convergence is not used as evidence: the axis is checked against every vertex of both convex cores. The resulting support gap g bounds separation for the complete surfaces.

For the prescribed angle theta=(pi/6) sin(pi*p)^2, |theta'|<=pi^2/6. Multiplying by the rotating ray's perpendicular radius and the largest vertex coefficient gives a speed bound L for every point of a panel core. For a phase interval of width h, the whole-interval clearance lower bound is

`g - (L_left + L_right)*h/2 - 0.02`.

Intervals with insufficient bounds are subdivided. A witnessed offset intersection rejects an interval; reaching the depth limit without proof remains unresolved. Neither a missed sample nor failed optimization becomes a clearance claim. Bounds use floating-point arithmetic, not outward-rounded interval arithmetic.

## Result

All 15 core pairs pass over phase [0,1] for both references. The 3D audit covers 113 pair/time intervals with minimum reported lower bound 0.0049953571. The 4D audit covers 117 intervals with lower bound 0.0058922070.

Across 65 exported states, principal stretches range from 0.715518 to 1.290994 in 3D, and 0.777704 to 1.289899 in 4D. These sampled deformation ranges show substantial compliance demands; they are not continuous extrema certificates. The clearance argument, separately, covers the continuous path.

Sixteen new tests plus fourteen existing relative-motion tests pass. Controls include unchanged hinge incidence, regular 4D starting pentagons, independent metric eigenvalue formulas, independently differentiated vertex speeds, complete temporal coverage, known separating planes, untrimmed hinge overlap, and rejection of excessive thickness.

## Remaining work

A connected hinge/collar model, contact inside the excluded regions, material response, energy and current coupling, and recursive integration remain open. The full assembly is not certified. The exporter supplies full and trimmed surfaces and triangle indices; a downstream viewer must show the exclusions and dimensional projection explicitly.

Run `python scripts/report_lynchpin_finite_panels.py <output.json>` for the geometry packet and interval evidence.
