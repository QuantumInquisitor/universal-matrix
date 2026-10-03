# Prescribed common breathing of the complete assembly

The complete 69-component aperture assembly now has an optional common-size
motion adapter. It transports both actual host cuts, all route components and
junctions with one map. This extends the existing PR119 size cycle to the flow
assembly. It does not apply PR119's relative hinge fold to this different graph.
No engine default or viewer is changed by this experiment.

## Recovered motion and explicit assumptions

The pinned source is [PR119's BreathingCycle](https://github.com/QuantumInquisitor/universal-matrix/blob/60a7fd60f57d73b89ea5397db58a3ff5d291556c/src/lynchpin_breathing_control.py).
The adapter uses its existing scale law:

`s(p) = 1 + a sin(2 pi p)`, `x = s(p) X`, `0 <= p <= 1`.

The reviewed range here is `0 <= a <= 0.1`, with reports using `a = 0.1`.
Phase is dimensionless. The cycle has no measured physical period, force law
or autonomous oscillator. All lengths, thicknesses, junction bodies, aperture
origins and cut domains scale together about the global origin. Fixed-width
walls, independently driven cells and stationary external ports are different
models and are excluded. Endpoints have the same position and velocity; this
periodic size cycle does not require endpoint velocity to vanish.

## Continuous geometry argument

For every pair of actual domains A and B, including the two subtracted host
apertures, `dist(sA,sB) = s dist(A,B)`. Their intersection is likewise the mapped
original intersection. Since `s >= 0.9`, strict separation stays strict,
declared contacts remain contacts, and every exact route/port match transports
with the same map. The deformation gradient is `F=sI` and its determinant is
at least `0.9^3 = 0.729` throughout the cycle. Positive reference chart
Jacobians remain positive when multiplied by this determinant.

This argument covers all 2,346 pairs continuously, rather than inferring safe
motion from sampled frames. It inherits the [static audit's](toroidal_combined_aperture_v0.1.md)
floating-point qualifications; it is not a new outward-rounded interval proof.
The adapter checks the static audit before use. `contains` pulls spatial points
back by `x/s`, then dispatches to the actual first or second host containment
function before considering generic enclosing geometry. Hole membership and
retained host fields are tested at contraction and expansion extrema.

## Current relative to a moving boundary

The reference current is transformed by `J_relative = J0(X)/s^2`. Cut area
scales by `s^2`, so signed flux through every transported cut is unchanged.
The 62 internal interfaces and eight junction ports inherit their reference
matching and balance. Numerical diagnostics additionally integrate all eight
moving annular ports at six phases for six signed-current cases.

For an explicitly supplied stationary reference scalar density `rho0(X)`,
`rho = rho0(X)/s^3`, boundary velocity per phase is `w=(s'/s)x`, and the
stationary-frame current is `J_lab = rho w + J_relative`. This obeys continuity
where the reference current is divergence-free. The correct moving-interface
balance uses `J_lab - rho w`. Requiring equal lab currents across a transported
density jump would be incorrect. Tests demonstrate this distinction and check
Eulerian continuity with nonconstant reference density.

Density is an additional transport assumption, not a recovered mass or charge
calibration. The port diagnostic uses a small current-proportional reference
density to keep subtraction resolved even in the tiny-current cases; it does
not validate arbitrary large advection-to-throughflow ratios. Port quadrature
evaluates reference cap charts before mapping them, avoiding roundoff that
could place an inverse-mapped boundary point just outside its cap. The
component-scoped adapter does not sum overlapping boundary charts or establish
a global material density law.

## Reproduce

```sh
uv run python -m pytest tests/test_toroidal_assembly_breathing.py
uv run python scripts/report_assembly_breathing.py --output-dir artifacts/assembly-breathing
```

The new test batch has 24 passing tests. The report reproduces I = +/-1,
+/-2e-8 and +/-7; compact results and source hashes are in
[assembly-breathing-summary.json](experiments/assembly-breathing-summary.json).
Full reports contain the 48 moving-cut diagnostics per current case. The
dedicated aperture workflow repeats tests, reports and scope assertions.

## Remaining motion gate

The recovered relative-fold specimen has six panel cores, four hubs and twelve
bridges. Its incidence graph is not the 66-conduit, three-junction flow graph.
No source correspondence was found in this batch that assigns that specimen's
hinge rays to all flow components. Uniform scaling preserves all angles and
relative shape: it does not demonstrate folding inward through itself.

Next define that correspondence, or a separately justified nonuniform map,
including how every finite-thickness route, junction and host cut deforms.
Then check Jacobians, interfaces and continuous clearance under that map.
The fixed-angle common-origin rigidity result from PR119 remains in force;
do not silently substitute rigid panels for its compliant specimen.
Material forces, energy accounting, emergent motion, recursive coupling,
wall-opening feasibility and the stagnating streamline remain open. Timing
subsystem and wave experiments retain their separate queues.
