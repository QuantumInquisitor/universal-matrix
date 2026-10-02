# Accounted replenishment of the folding network

This optional experiment adds an explicit ideal external power port to the
finite-reservoir model. Existing mechanics, mapped connectors, damping,
conversion efficiency and geometry limits remain unchanged. The source is a
stated mathematical boundary condition, not a specified material or device.

## Supply law and accounting

Each node of relative size s has a declared reserve capacity
`Rcap = 2e-5 s^3 J` and maximum incoming power `Jmax = 6e-6 s^2 W`.
The charge controller supplies `J = Jmax max(0, 1-R/Rcap)`.
Charging falls to zero at capacity. J is power delivered into the reserve;
charging is idealized as lossless. Wall-plug or upstream source losses are not
modeled and must be added for a physical implementation. The reserve state itself is never clipped.
The reserve law becomes `Rdot = J - P/.8 - (.15/s)R`, where P is the
mechanical feedback power already defined in `fold_active_multiscale.md`.

A separate cumulative input ledger integrates J for every node. The correct
whole-network account is mechanical energy + reserve + connector potential +
damping/conversion/leakage losses - cumulative input. Every subgroup also
subtracts its own nodes' input and its mechanical boundary work. Delivered
feedback work is an internal transfer and is not counted again as new energy.

This explicitly open network can receive energy continually. Nothing here
creates energy or establishes a physical power-source implementation. The
power cap gives `0 <= input_i(t) <= Jmax_i t`; input is nondecreasing.
For the exact equations and initially admissible reserves, R cannot cross zero
or capacity: at zero its derivative is positive when powered, and at capacity
its derivative is nonpositive. Numerical stage checks do not replace a
physical containment or collision model.

The area scaling of maximum power and volume scaling of capacity preserve the
previous conditional length-timescale similarity. They are modeling choices,
not measured material laws. All four initial reserves are full; only node 0
starts mechanically perturbed, as in the finite-source baseline.

## Independent controls

Turning supply power off must reproduce the existing finite-source derivative
exactly. At mechanical equilibrium the geometry stays still and reserve has an
independent closed-form solution. With `k=Jmax/Rcap + .15/s` and
`Req=Jmax/k`, it is `R(t)=Req+(R0-Req)exp(-kt)`. The cumulative source input is
`Jmax[(1-Req/Rcap)t - (R0-Req)(1-exp(-kt))/(Rcap k)]`.
Replenishment alone does not start motion from exact equilibrium, because
feedback force is proportional to velocity. With the chosen power coefficient,
`Req = (2/3) Rcap`. At that reserve the mechanical feedback coefficient is
`4 Req/(Req+Rstar) = 16/7`, above the unit damping coefficient. Thus exact rest
is a solution, but the linearized mechanical equations have negative damping:
small motion is amplified. This is a consequence of the imposed feedback law,
not evidence of a new physical source or spontaneous motion from exact rest.
Whether reserve depletion regulates that amplification into a stable cycle
requires separate evidence.

Compare powered and unpowered trajectories over the same 20-second horizon.
Repeat the powered case with tighter tolerances and half the maximum step.
The missing-input diagnostic deliberately recomputes the powered account
without subtracting its source ledger; it is a postprocessing failure control,
not another simulated trajectory. It must expose the received energy as an
accounting error. Separate finite-difference checks test subgroup power.

## Computed results

Powered, source-off and finer powered runs all reached 20 seconds within the
model scope. The powered network received 7.8382923925e-5 J (78.3829 microjoules).
Final mechanical plus connector energy was 3.16379 microjoules powered versus
0.694234 microjoules with the supply off, a ratio of 4.557. This ratio is a
state comparison, not an energy-conversion efficiency: their remaining
reserves and accumulated losses also differ.

Over accepted endpoints in the last five seconds, powered mechanical energy
ranged from 2.06692 to 3.16379 microjoules and was still increasing overall.
The source-off case declined over that window. There is no demonstrated stable
cycle. The chosen feedback law explains the amplification; it does not establish
a material mechanism or motion starting from exact rest.

Maximum whole-network accounting errors were 6.7935e-14 J powered,
3.1798e-14 J source-off and 1.6618e-14 J in the finer powered run.
Omitting input from the powered accounting creates a 7.8382923857e-5 J error,
equal to received energy within the numerical residual. Final coordinate and
rate differences under refinement were at most 3.0568e-9 and 1.2747e-8;
body energy-ledger differences were below 1.293e-13 J. These are numerical
agreement checks, not a demonstrated convergence order.

All reserves remained nonnegative and within capacity; received energy was
nondecreasing and within the specified power budget. Eighteen focused tests,
Ruff/format, all 12 source hashes, finite-JSON validation and complete workflow
acceptance passed. The computed plot was visually inspected.

## Reproduction and dependencies

The adaptive solver requires the project's `scientific` extra (SciPy).
Plotting additionally needs the `visualization` extra. The dedicated automated
jobs explicitly select these scientific dependencies and Python 3.12.

```sh
uv run --extra scientific python scripts/report_fold_supply.py --output artifacts/fold-supply/report.json
uv run --extra visualization python scripts/plot_fold_supply.py --input docs/experiments/fold-supply-summary.json --output artifacts/fold-supply/computed-supply.png
```

The report preserves source hashes, settings, input/state accounts, termination
and the finer comparison. Each completed case also writes a separate local
checkpoint keyed by sources and parameters. The plot checks source hashes and
shows saved samples, with joining lines used only as guides.

## Limits and next decision

A nonzero final motion or a rising energy trace over 20 seconds does not show a
stable cycle or sustained breathing. Longer traces, perturbation recovery,
startup dependence and amplitude regulation remain necessary. Any declared
geometry-limit stop is a numerical-scope finding, not a collision certificate.
A physically specified power source and material laws remain open tasks.

Timing components, including a proposed time-crystal component, must be
compared against ordinary controls under the same input-energy budget. This
experiment establishes the power boundary needed for that comparison; it does
not establish any timing-component advantage or physical realization.
