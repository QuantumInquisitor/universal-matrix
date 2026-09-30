# Folding geometry to material dynamics: dependency audit

30 September 2026. This audit advances P04/P07 prerequisites; it does not close
the whole-structure material, energy, or emergent-motion tasks.

**A connected folding specimen has already been constructed.** Its geometry
can replace an unspecified shape in a new mechanics experiment. It cannot yet
replace the two-mass benchmark with calibrated physical predictions: the
recovered specimen supplies geometry and prescribed deformation, while density,
constitutive response, supports and actuation still need explicit choices.
Synthetic choices are permissible when recorded as such.

## Evidence inspected

The current checkout was searched for hinge, compliant, folding, stiffness,
elastic and material references across `src`, `scripts` and `docs`. The preserved
older checkout was also searched for folding sources. The newer connected
modules are absent from this checkout; their pinned PR119 source was therefore
read directly at commit `60a7fd60f57d73b89ea5397db58a3ff5d291556c`.
This is a source audit, not a rerun of PR119's tests or a statement about its
current review status.

| Implemented source | What is available | Scope boundary |
| --- | --- | --- |
| `src/lynchpin_geometry_audit.py`: `LYNCHPIN_PANELS`, `LYNCHPIN_TRIPLE_HINGES`, `lynchpin_panel_adjacencies`, Gram/rank functions | Six panels indexed by tetrahedral edges; four triple hinge incidences; twelve adjacent panel pairs | Incidence does not specify free hinge travel, forces or a unique material |
| [PR119 relative-motion source](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_relative_motion_control.py): `reference_rays`, `constraint_jacobian`, `rigidity_report`, `compliant_rays` | Fixed-angle rigidity check; explicit ray-3 rotation with two changing panel angles | The pi/6 motion amplitude is a chosen control, not a recovered hinge limit |
| [PR119 finite-panel source](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_finite_panel_control.py): `pentagon_coefficients`, `panel_vertices`, `deformation_metrics`, `audit_core_cycle` | Trimmed affine pentagonal cores, principal stretches and area ratios, finite offset clearance | Offset geometry is not a complete through-thickness material map |
| [PR119 connected source](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_connected_control.py): `bodies`, `contact_check`, `audit_connected_cycle`, `scene` | Six cores, four hubs, twelve bonded bridge capsules; bounded contact regions and cycle clearance | New compliant joint construction; dimensionless geometry, no material solver |
| [PR119 breathing source](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_breathing_control.py): `BreathingCycle` | Prescribed size change, panel area/density ratios and similarity-current control | No physical period or autonomous forcing law |
| `src/toroidal_combined_aperture.py`: `combined_components`, `audit_combined_aperture` | 66 conduits, three junctions, 62 interfaces and eight ports | A different graph from the 22-body folding specimen |
| `src/toroidal_assembly_breathing.py`: `AssemblyBreathing`, `BreathingAssembly` | Common positive similarity of actual cut domains and signed flow | Keeps relative angles fixed; no relative fold |
| `scripts/report_material_specimen.py`, `docs/material_specimen.md` | Connected two-mass dynamics with explicitly chosen SI coefficients and work/dissipation ledgers | Not a reduction of either geometric assembly |
| `src/piezoelectric_mode_reference.py`, `docs/piezoelectric_mode_reference_v0.1.md` | Parameterized modal electromechanical energy and response | Effective modal coefficients still require geometry/material reduction or measurement |
| `docs/microplane_projection_reference_v0.1.md` | Stress/strain projection and work-conjugacy reference | Does not supply a calibrated constitutive law for this joint specimen |

## Known hinge locations are preserved

Panels are `01,02,03,12,13,23`; triple hinges are the three panels incident to
each tetrahedron vertex. Four fixed unit rays with all six fixed angles admit
no internal first-order motion beyond global rotations in the reviewed
reference configuration. In 3D their tetrahedral angle is approximately
109.471 degrees; exact equiangular 108-degree rays instead require rank four.
The existing construction resolves relative motion through compliance, rather
than silently making those six fixed-angle panels freely hinged.

`compliant_rays` fixes rays 0,1,2 and rotates ray 3 about ray 0 through
`theta(p)=(pi/6) sin(pi p)^2`. Consequently panels 13 and 23 change their corner
angles. Panel 03 moves without changing its ray-pair angle. The connected
specimen places hub i at `0.5 r_i`, with radius 0.05; each bridge runs from
`0.5 r_i` to `0.5 r_i+0.17 r_j`, radius 0.008. Panel cores use collar 0.15 and
offset radius 0.01. These are explicit dimensionless specimen choices.

The [pinned connected report](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/docs/lynchpin_connected_control_v0.1.md)
records 231 pairs with localized intended attachments, and a positive 3D
clearance lower bound over the prescribed path. It uses floating-point support
and analytic speed bounds, not outward-rounded interval arithmetic. Its 4D
counterpart is a mathematical control, not a 3D material realization.

## Minimal next implementation

Build a **reduced compliant-specimen model**, retaining the two-mass benchmark
as an independent energy-integrator control. Start in 3D with generalized
coordinates `q=(s,theta)` for positive size and relative fold. Use the existing
coefficient geometry and ray rotation to form panel midsurfaces
`x_a(q)=ell*s*sum_i c_ai*r_i(theta)`, where ell is metres per reference unit.
Do not identify dimensionless routing ticks with seconds without a declared
clock conversion.

First implement a kinematic adapter and its derivatives, independently of a
constitutive choice. Check that the recovered prescribed path is reproduced,
that angle changes and panel stretches agree with the existing functions, and
that velocity is `x_q*qdot`. Two independent coordinates explore states beyond
the original one-parameter trajectory: the old path audit is not automatically
a two-dimensional admissibility certificate. Define and check the admissible
`(s,theta)` region and halt trajectories at unvalidated boundaries.

Next assign a reference material partition. Panel/hub/bridge bodies overlap in
bonded regions: summing every enclosing-body volume double-counts material.
Choose a disjoint union mesh or explicit lumped mass allocation with documented
ownership. The panel offset and rotating capsule descriptions specify occupied
sets, but not unique correspondence of every interior material point. Supply
that correspondence, or explicitly restrict the model to reference surface and
centerline quadrature with lumped inertia. Do not claim full solid strain from
midsurface principal stretches alone.

For a declared reference partition, derive rather than guess generalized mass:

```
M_ab(q) = integral rho0(X) [dx/dq_a dot dx/dq_b] dV0
T = (1/2) qdot^T M(q) qdot
V(q) = integral W(F(q), X) dV0 + joint/support potentials
M_ab qddot_b + Gamma_abc qdot_b qdot_c + dV/dq_a
    = Q_a - C_ab(q) qdot_b
Gamma_abc = (d_b M_ac + d_c M_ab - d_a M_bc)/2
d(T+V)/dt = Q dot qdot - qdot^T C qdot
```

Use a positive semidefinite damping matrix and a differentiable declared
potential. If a parameterized quadratic modal potential is used first, label
it a synthetic reduced law; it does not establish material strain limits.
Coordinate-dependent inertia requires the geometric inertial term above.
Dropping it would corrupt the energy control during large folds. Supports must
state how the fixed reference rays are maintained and which reactions or
actuator work they represent. A two-coordinate reduction suppresses other
modes by assumption; it does not establish their stability.

Required controls: zero-input equilibrium, conservative energy/refinement,
damped decay, externally supplied work, coordinate-derivative checks, positive
mass matrix, disconnected/zero-coupling comparison, recovered-path geometry,
and admissibility rejection. Record the drive reservoir before claiming a
closed energy budget or sustained autonomous breathing. The existing material
state/restart experiment can proceed independently of this reduction.

## Inputs still requiring explicit selection or calibration

- Physical scale ell, reference densities or masses, and bonded-volume ownership.
- Panel, bridge and hub constitutive response, thickness correspondence,
  allowable strain, damping and any temperature dependence.
- Reference stress/rest state, support constraints, preload and actuator
  locations; force/torque or electromechanical coupling and drive limits.
- Contact/friction law if trajectories leave the previously separated region.
- Measured response data for calibration and an independent validation case.

The search found parameterized mechanical references and chosen benchmark
values; it did not find a material dataset assigning those inputs to these
22 bodies. This is a bounded search result, not an assertion that such data
cannot exist elsewhere.

## Whole-flow-assembly gate remains separate

To apply relative folding to the 69 flow components, assign every conduit,
junction, interface and both host cuts to a deformation chart or material
attachment. The 22-body graph is not that assignment. Preserve stable component
IDs and actual aperture domains: `combined_components` returns enclosing host
geometry, while `BreathingAssembly` dispatches to the cut containment/current
functions. Require agreement on shared boundaries, positive volume Jacobians,
transported port normals/areas, current conservation and continuous clearance.

For a valid common material map with gradient F and J=det(F)>0, the natural
transport control is `rho=rho0/J`, `j_relative=F*j0/J`, and
`j_lab=rho*w+j_relative`. This formula is conditional on constructing compatible
charts; it cannot fill missing geometric correspondence. The existing uniform
similarity is its verified restricted case. No image, phase pattern or hinge
incidence substitutes for this whole-assembly mapping.


## Follow-up implementation

The kinematic/derivative and synthetic point-ownership prerequisite is now
implemented in [fold_kinematics.md](fold_kinematics.md). The independent-domain
question is resolved conditionally by [fold_domain_inheritance.md](fold_domain_inheritance.md),
with a fresh original-source clearance run saved in the fixture. These results
do not supply a full solid material-point partition or calibrated force law.
