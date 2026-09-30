# Connected material specimen baseline

This experiment advances P07/P08 with a connected, dynamical, two-mass specimen.
It complements the existing single-mode piezoelectric and pressure-storage
references. Its coefficients are chosen SI values, not measured materials or a
reduction of the 69-component assembly. Motion follows forces and initial
conditions; no displacement or breathing cycle is prescribed.

Two equal masses move along one axis. Each has an anchor spring and dashpot;
a spring and dashpot connect the masses. Displacements are relative to an
unspecified equilibrium, so this linear model does not establish absolute
geometry, collision clearance, nonlinear strain, or contact behavior.

Let x0,x1 be displacements, v0,v1 velocities, m mass, ka anchor stiffness,
kl link stiffness, ca anchor damping, and cl link damping. Define
L = kl(x1-x0) + cl(v1-v0). Then

```
m a0 = F(t) + L - ka x0 - ca v0
m a1 =      - L - ka x1 - ca v1
F(t) = A sin(omega t)
E = m(v0Â²+v1Â²)/2 + ka(x0Â²+x1Â²)/2 + kl(x1-x0)Â²/2
dW/dt = F(t) v0
dD/dt = ca(v0Â²+v1Â²) + cl(v1-v0)Â²
E(t)-E(0) = W(t)-D(t)
```

The link forces cancel internally. D is nonnegative for the admitted damping
parameters. External driving supplies energy; elapsed time is an independent
variable, not an energy source. Undriven damped motion decays, so this does not
claim self-sustained breathing.

Parameters: m=1 kg, ka=4 N/m, kl=2 N/m, ca=0.1 N s/m, cl=0.2 N s/m,
A=0.2 N, omega=1.5 rad/s. Initial displacements are (0.1,0) m and velocities
are zero. The saved report identifies all parameters for every control.

## Numerical evidence

Twelve runs cover driven/damped, drive-off, conservative, and disconnected
controls at steps 0.04, 0.02 and 0.01 s over 8 s. RK4 integrates external work
and damping at its stage states, independently of endpoint energy differences.
Snapshots contain both masses, both stored energies and both cumulative ledgers.

At the finest step the driven case has initial energy 0.03 J, external work
0.04120607990 J, dissipation 0.03203030144 J, and final energy 0.03917577875 J.
Its largest absolute ledger residual is 2.85e-10 J. Successive final displacement
differences decrease by a factor 15.74 and velocity differences by 17.86,
consistent with fourth-order refinement for this run. Displacement and velocity
norms are reported separately to avoid adding unlike units. This is a convergence
observation, not a general error bound.

Without drive, energy decreases from 0.03 to 0.00495153968 J. Disconnecting the
link leaves the initially resting second mass exactly at rest, while connecting
it transfers motion. The conservative case is checked against an independent
analytic solution with symmetric and antisymmetric frequencies 2 and sqrt(8)
rad/s. Twelve tests cover these controls, refinement and invalid inputs.

Run from the repository root:

```
python scripts/report_material_specimen.py --output docs/experiments/material-specimen-summary.json
python -m pytest tests/test_material_specimen.py -q
```

The JSON includes the reporter source hash and rejects nonfinite JSON output.
Remaining work: derive mass/stiffness/damping from a specified actual specimen,
calibrate coefficients, connect force laws to the assembly geometry, add nonlinear
deformation/contact and recursive coupling, and account for any drive reservoir
required for sustained motion. P07/P08 are advanced, not completed.

The committed JSON is a compact outcome snapshot with per-case traces omitted. Run the reporter with --output into artifacts to regenerate full traces.
