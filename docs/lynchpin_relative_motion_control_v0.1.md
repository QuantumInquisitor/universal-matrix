# Relative Lynchpin ray-motion control

This optional experiment uses the existing four common-origin hinge rays and six panel incidences. It keeps the previously established alternatives separate: the 3D tetrahedral 109.471-degree corners and the 4D exact-108-degree corners.

## Fixed-angle result

Fixing the four unit lengths and all six pairwise corner angles fixes the complete Gram matrix of the four rays. Two configurations with that same Gram matrix differ only by an orthogonal transformation on their spans. Consequently this common-origin ray model has no finite internal folding freedom with every angle fixed. This does not prove that every disclosed Lynchpin mechanism is immobile: curved or flexible panels, nonconcurrent hinges, sliding connections, and other geometries have different constraints.

The numerical linearized audit agrees: in 3D the constraint matrix has rank 9 and nullity 3, entirely rigid rotations. In 4D its rank is 10 and nullity 6, again entirely rigid rotations. These numerical ranks diagnose the two fixed reference states; the full-Gram argument supplies the underlying rigidity statement.

## Positive relative-motion control

Hold rays 0, 1 and 2 fixed. Decompose ray 3 into a component along ray 0 and a perpendicular unit vector u. Choose w perpendicular to both in the span of the reference rays. Rotate the perpendicular component in the u,w plane by

`theta(p) = (pi/6) sin(pi p)^2`, for `0 <= p <= 1`.

This preserves unit length and the 03 corner angle continuously, while the three untouched-ray pair angles remain fixed. Panels 13 and 23 must change their corner angles. The rays return at phase 1, with zero endpoint speed. The 30-degree maximum rotation is an explicit experimental input, not a recovered mechanical limit, physical time law, or recursive phase assignment.

Tests verify the fixed-angle rigidity, the out-and-back endpoints, preserved angles and lengths, actual numerical velocities against the retained constraints, and failure of those velocities against the full rigid-panel constraints. A full common-origin ray path is defined, but full polygon surfaces, panel thickness, collisions away from the intended common origin, strain fields, actuator mechanics, flux, and recursive coupling are not modeled.

The next gate is a specified finite-panel realization of these two compliant corners, or another explicit relaxation of the rigid common-origin assumptions. It must retain the actual hinge identities and quantify surface deformation, contact and connectivity. This control must not be labelled a completed physical Lynchpin or living fractal.
