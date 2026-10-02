# Supply onset in the synthetic folding network

The 60-second supplied continuation was still gaining mechanical energy. This
experiment asks a narrower question: where does the present feedback law change
from removing small motion to amplifying it? It does not change the mechanical,
connector or charging equations and does not assume a stable breathing cycle.

## Controlled starting state

The four sizes remain 1, 0.75, 0.5 and 0.5. Each power case starts with the same
small declared coordinate displacement from rest, zero velocities and zero
cumulative ledgers. Each reserve starts at its own power-dependent resting
equilibrium. Thus initial mechanical energy is shared, but initial reserve
energy and subsequent received energy differ. This is a sweep of a source-law
parameter, not an equal-energy comparison of competing technologies.

The unit-size power coefficients are 0, 0.3, 0.6, 0.9 and 1.2 microwatts.
The 0.9 microwatt case is repeated with finer integration settings. Each run
covers at most 20 seconds and retains the existing geometry/reserve limits.
No precharged state from the earlier 6 microwatt continuation is reused.

## Equilibrium and damping threshold

Write `s` for body size, `r = R/Rcap`, and `p` for the source coefficient in
watts. The current assumptions give

```
Rcap = 2e-5 s^3
J = p s^2 (1-r)                    for 0 <= r <= 1
leakage = (0.15/s) R
P = a(R) s^4 v^T D v >= 0
a(R) = 4 R / (R + 1e-5 s^3)
Rdot = J - leakage - P/0.8
```

At rest, `P=0`. Solving the reserve balance gives
`r_eq = p/(p+3e-6)`. The size factors cancel because supply scales as area,
capacity as volume and leakage rate inversely with size. This cancellation is
a consequence of chosen laws, not an experimentally measured universality.

The equilibrium feedback multiplier is `a_eq = 8p/(3p+3e-6)`. It equals one
at `p=6e-7 W`: 0.6 microwatts at unit size. Below that coefficient the linear
velocity term damps motion; above it the term supplies mechanical energy.
Exactly at the threshold the linear damping term vanishes; this does not
establish neutral nonlinear behavior or a finite-amplitude oscillation.

Exact rest stays motionless: there is no velocity-independent startup force.
For positive power, the input and leakage ledgers nevertheless keep increasing.
Only the physical coordinates, velocities and equilibrium reserves are steady.

## Stronger result below the threshold

With initial `0 <= R <= R_eq`, each reserve remains in that interval while the
continuous model stays within its declared domain. At zero reserve, replenishment
is nonnegative and active power is zero. At `R_eq`, reserve change is `-P/0.8`,
which is nonpositive. The reserve vector field therefore points into the interval
at both ends. In particular, feedback cannot exceed its resting-equilibrium value.

Conservative connector power cancels in the total mechanical-plus-connector
energy account, leaving

```
dE_mechanical/dt = sum_i [(a(R_i)-1) s_i^4 v_i^T D v_i].
```

For `p <= 0.6 microwatts` and these reserve initial conditions this derivative
is nonpositive. Below the threshold it is strictly negative whenever any node
has nonzero velocity. This excludes growing mechanical energy under those
conditions; it does not specify a decay rate, certify geometry outside the
model's domain, or establish a stable nonzero breathing cycle. A previously
overcharged reserve would invalidate the stated initial-condition premise.

Above threshold, reserve depletion can reduce the active multiplier, so the
near-rest sign alone cannot predict the eventual amplitude. Finite traces can
show amplification over the observed interval; they cannot establish an
attracting cycle, robustness to other initial states, or physical feasibility.

## Coordinate confinement under the energy bound

The initial mechanical-plus-connector energy is 2.7687834892e-10 J. With
positive masses, positive-definite body stiffness `K` and nonnegative connector
potentials, each coordinate obeys

```
|q_ij - Q0_j| <= sqrt(2 E0 (K^-1)_jj / s_i^3)
```

whenever total mechanical energy is at most `E0`. This follows by applying
Cauchy-Schwarz in the stiffness inner product to the body spring energy.
The least restrictive bounds, at size 0.5, are 0.0004786865 in scale and
0.0008739579 radians in angle. Both are strictly inside the admitted coordinate
rectangle around rest (scale 1 and angle pi/12). For the exact smooth solution
and the subthreshold reserve premise, this bounds the deformation beyond the
20-second observation window. It does not bound solver trial stages, certify
the separate velocity guard, or establish absence of physical collisions.

## Observed 20-second sweep

All five source settings complete 20 seconds within the declared domain.
Initial mechanical-plus-connector energy is the same 2.7687834892e-10 J.

| Unit-size coefficient (microwatts) | Resting feedback / damping | Final / initial mechanical energy | Received energy (microjoules) |
| --- | --- | --- | --- |
| 0 | 0.000000 | 0.22079648 | 0.000000 |
| 0.3 | 0.615385 | 0.55159631 | 11.250018 |
| 0.6 | 1.000000 | 0.99997741 | 20.625070 |
| 0.9 | 1.263158 | 1.52235386 | 28.557846 |
| 1.2 | 1.454545 | 2.08333465 | 35.357404 |

The 0 and 0.3 microwatt cases decay. At 0.6 microwatts, mechanical energy is
almost unchanged over this short interval, with a small decrease. The 0.9 and
1.2 microwatt cases amplify the displacement's mechanical energy. This agrees
with the near-rest prediction; none of these results demonstrates an attracting
breathing cycle. Received energy is not mechanical-energy gain: ongoing leakage
and other losses are separately accumulated, and the initial reserves differ.

Late-window slopes use the actual saved accepted endpoints at or after 15
seconds and the final point at 20 seconds. The first saved point is not exactly
15 seconds, so those slopes must be interpreted with their recorded coverage.
The finer comparison uses the common final time, not mismatched intermediate
samples. Coordinate, rate and joule-ledger errors have separate tolerances.

## Validation and next experiment

Nineteen focused tests passed, including independently reconstructed damping
power, physical rest versus flowing accounting ledgers, equal mechanical
preparation, reserve interval boundaries, invalid settings and short energy
budgets. The complete report passes the workflow's provenance, finite-value,
coverage, source-budget and per-account energy checks. The largest root/group
residual is 3.4152e-16 J. The finer 0.9 microwatt run ends with energy ratio
1.52235512 versus 1.52235386; maximum coordinate difference is 3.600e-10,
maximum rate difference 7.604e-10 per second and mechanical-energy difference
3.488e-16 J. These are consistency checks, not material-accuracy estimates.

Next, continue the above-threshold cases with unchanged equations and trace
whether reserve feedback limits amplitude before the declared domain is left.
Compare multiple small initial disturbances and phases, with finer integration
where outcomes are sensitive. A persistent amplitude must still pass recovery
and energy checks before it can be called stable breathing. Do not prescribe
the desired output waveform to obtain that result.

## Reproduction and scope

```sh
uv run --extra scientific python scripts/report_fold_threshold.py --output artifacts/fold-threshold/report.json
uv run --extra visualization python scripts/plot_fold_threshold.py --input docs/experiments/fold-threshold-summary.json --output artifacts/fold-threshold/computed-threshold.png
```

Reports preserve the full source inventory, initial conditions, termination,
input/loss/reserve accounts and refinement settings. Plots use saved samples;
joining lines do not add measured observations. The source remains ideal and
the mechanics uncalibrated. Full physical assembly, recursive coupling beyond
this four-node network, XR mapping and time-crystal component benefits remain
separate open tasks.
