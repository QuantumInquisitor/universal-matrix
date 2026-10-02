# Material and flow motion: cross-adapter shape regression

The existing common-scale flow motion cannot reproduce the existing labeled
relative-fold marker trajectory of the 22-body material specimen. This report
connects the two existing APIs; it supplies no point correspondence between the
22 material bodies and the separate 69 flow components.

This is a regression witness, not a new rigidity theorem. The fixed-Gram
argument and relative-motion negative control already appear in
`lynchpin_relative_motion_control_v0.1.md` and
`tests/test_lynchpin_relative_motion_control.py`. The common similarity and its
clearance inheritance are already documented in
`toroidal_assembly_breathing_v0.1.md`.

## Existing interfaces and comparison

`scripts/report_fold_kinematics.py:kinematics` supplies the ordered six panel,
four hub and twelve bridge owner markers. Panel markers are vertex means,
not area or mass centroids. All 231 labeled squared pair distances are divided
by their sum. Translation, orthogonal transformations and uniform scale leave
this normalized vector unchanged.

The report uses 17 samples of the original prescribed schedule. It compares the material
trajectory with scale-only material motion and the existing
`AssemblyBreathing.forward` operator applied to the same reference markers.
Those markers are **not flow-component anchors**. This operator-level comparison
requires no invented attachment, placement, material assignment or flow units.
It does not rebuild the flow inventory or rerun full-pair clearance.

At phases zero and one-half, both scale laws give one. The material fold angle
changes from zero to pi/6, changing normalized distances, while common scaling
preserves them. A witness independent of the full-cloud normalization is

`R(theta) = |hub-1 - hub-3|^2 / |hub-0 - hub-1|^2`

`R(theta) = (2 + cos(theta) - sqrt(3) sin(theta))/3`.

The formula follows from the original tetrahedral rays and the positive
transverse basis toward ray 1: `r1 dot r3(theta) =
1/9 - 4 cos(theta)/9 + 4 sqrt(3) sin(theta)/9`, while
`r0 dot r1 = -1/3`. Thus R changes from 1 to 2/3. Marker lengths, common size
and a global rigid frame cancel. The tests independently check both endpoints,
the transverse sign, multiple sizes and metre conversions.

The 1e-12 diagnostic bound controls floating-point regression comparisons.
It changes no existing geometry, physical tolerance, collision criterion or
solver acceptance rule. Numerical samples support the implementation checks;
the endpoint ratio supplies the explicit shape obstruction to a global
similarity reproducing this labeled trajectory.

## What remains missing

The material specimen has local-frame coordinates `(s,theta)` and a declared
synthetic conversion of 0.1 metres per reference unit. The toroidal assembly
has 66 conduits and three junctions in a separate dimensionless routing frame,
with 62 interfaces and eight ports. Its two modified hosts include actual
subtracted holes; enclosing component geometry alone is not their domain.
No common SI length/current conversion or frame registration has been supplied.

Both prescribed schedules use dimensionless phase, not measured seconds.
Material constitutive rest state `(1,pi/12)` differs from the geometry's initial
state `(1,0)`; neither is silently reassigned. A physical correspondence still
needs named many-to-many material/domain ownership, frame and unit conversion,
attachment regions, finite-thickness deformation, and interface/Jacobian/
clearance checks under that declared map. Existing material-overlay and viewer
adapters already handle their narrower 22-body source/local-frame contracts.

This result excludes only representation by the current common similarity.
It does not rule out arbitrary nonlinear correspondences, demonstrate an
actual 22-to-69 mapping, or validate attachments, forces or clearance.

## Reproduce

```sh
python -m pytest tests/test_material_flow_similarity.py
python -m scripts.report_material_flow_similarity --output artifacts/material-flow-similarity.json
```

The committed summary records source hashes, identities, phase samples and
scope flags. The focused workflow repeats tests and report acceptance.
