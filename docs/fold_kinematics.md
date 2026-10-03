# Folding specimen: geometry-derived lumped inertia

30 September 2026. This bounded adapter recovers the 22-body geometry from
PR119 commit `60a7fd60f57d73b89ea5397db58a3ff5d291556c` and provides analytic
kinematics for two independent coordinates `q=(s,theta)`. It supplies no forces,
constitutive material law, solver or autonomous breathing claim.

## Material-point reduction

The source contains six panel cores, four hubs and twelve bridge capsules.
The adapter retains their exact names and coefficient geometry. Each panel's
representative point is the arithmetic mean of its trimmed core vertices;
this is **not claimed to be its area or volume centroid**. Each hub uses its
center, each bridge its centerline midpoint. Rotation of ray 3 uses the source's
signed transverse basis, not an arbitrary cross-product convention.

There is one synthetic mass owner per body ID: 0.1 kg per panel, 0.02 kg per
hub, 0.005 kg per bridge, totaling 0.74 kg. These are explicit benchmark choices,
not density integrations. Overlapping bonded envelopes are never summed as
solid volumes. This point-mass reduction omits distributed rotational inertia
and through-thickness strain. Its mass matrix therefore belongs to this
declared reduction, not an inferred complete solid.

The physical-length conversion is explicitly chosen as `ell=0.1 m` per
reference unit. All points are `x_n=ell*s*C_n*r(theta)` with original coefficient
rows `C_n`. No routing tick or prescribed phase is identified with seconds.

## Derivatives and inertia

Writing `b=C*r`, `b_theta=C*r_theta`, the adapter returns

```
x_s = ell*b                 x_theta = ell*s*b_theta
x_ss = 0                   x_s_theta = ell*b_theta
x_theta_theta = ell*s*b_theta_theta
M_ab = sum_n m_n (x_n,a dot x_n,b)
T = sum_n m_n |J_n qdot|^2 / 2 = qdot^T M qdot / 2
```

Position, Jacobian and Hessian shapes are respectively `(22,3)`, `(22,3,2)` and
`(22,3,2,2)`. Hessian coordinate order is `(s,theta)`. With positive masses,
`M` is positive definite throughout the allowed rectangle: the fixed hub 0
forces `sdot=0` for any zero point velocity field; the moving hub 3 then forces
`thetadot=0`, because its rotation radius is nonzero and `s>0`. This rank argument
extends beyond the sampled eigenvalue controls.

The coordinate dimensions differ: `s` is dimensionless and `theta` is radians.
Entries carry the corresponding generalized inertia units. Test rates are
chosen per-second rates solely to evaluate the kinetic identity, not measured
motion or the prescribed path's physical frequency.

## Allowed domain and evidence limits

Inputs are restricted to `s in [0.9,1.1]`, `theta in [0,pi/6]`, length conversion
in `[1e-6,1e3] m`, and each synthetic mass in `[1e-9,1e6] kg`. The length/mass
ranges are numerical scope choices, not material limits. Invalid inputs stop
the calculation.

The [domain audit](fold_domain_inheritance.md) explains conditional inheritance
of the original occupied-set separation/contact result over this rectangle:
the old fold reaches every allowed angle and positive similarity preserves
separation if **all** bodies, radii and attachment regions scale together.
The point adapter does not itself represent those complete occupied sets or
rerun their continuous clearance audit. Sample replay must not be presented as
a new collision certificate or a full-volume material map.

## Reproducible controls

Run `scripts/report_fold_kinematics.py --output
docs/experiments/fold-kinematics-summary.json` with the repository Python
environment. The finite JSON report records original commit, adapter hash,
fixture hash, original executed-source hashes, 17 prescribed-path samples,
mass matrices and kinetic identity residuals. The separate fixture was obtained
by executing the original pinned geometry/control sources, with explicitly
hashed local import dependencies; the adapter was not used to generate it.
Nine fixture phases compare all 22 mean-vertex positions.

The integrating run also reran the original 3D clearance auditor: accepted,
231 pairs, 1,208 intervals, minimum scaled bound `3.773014616157734e-05`
reference units. That separate full-envelope result is in the fixture; the
point adapter itself remains a reduced model. See the domain audit for its
conditional use across independent size/fold coordinates.

To reproduce the fixture, place the four pinned `lynchpin_*_control.py` modules
listed in the report plus pinned `lynchpin_geometry_audit.py` in a trusted source
directory. Run `python scripts/export_fold_reference_fixture.py --source-dir
artifacts/fold-pinned --dependency-dir src --audit-clearance --output
docs/experiments/fold-original-source-fixture.json`. Imports beyond those five
files use the local dependency directory. Compare every recorded source hash
with the saved fixture when changing checkouts. The exporter executes supplied
source and records hashes; it does not authenticate a Git checkout itself.

Tests check first derivatives by position differences, second derivatives by
Jacobian differences, positive inertia and kinetic equality, mass/length
scaling, ownership, path endpoints and rejected inputs. Original-source replay
is checked separately against the saved fixture. Passing these controls validates
this kinematic reduction; it does not calibrate its masses or validate material
behavior.

Next steps are a declared potential, damping and supports, the geometric
inertial terms derived from these derivatives, energy-controlled integration,
and drive/reservoir accounting. The 69-component flow assembly is a different
graph and still needs its own compatible material correspondence.
