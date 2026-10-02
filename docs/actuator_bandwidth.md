# Synthetic actuator bandwidth control

This optional experiment extends the ideal-measurement paired-mode controller
with a first-order force lag. The original controller, reporter and historical
results remain unchanged. No stochastic noise, measurement delay, stiffness
mismatch, calibrated hardware or electrical supply is modeled here.

## Model and startup

The original unit-radius target, controller gains, plant damping and pump remain:
`q' = v`, `v' = -.04*v - k(t)*q + a`, `k(t) = 1 + .2*cos(2*t)`.
The original controller command is norm-clipped to the declared `10 m/s^2`
force-per-mass limit **before** entering the actuator:

```text
tau > 0: a' = (limited_command - a)/tau; a(0) = 0
tau = 0: a = limited_command
```

Positive lag therefore includes a declared zero-force startup transient. The
zero-lag mechanical trace agrees exactly with the original RK4 computation.
Command clipping and sampled applied-force saturation are separate diagnostics.
Neither sample fraction is a continuous-time occupancy guarantee.

RK4 integrates mechanical coordinates, actual force and three accounting
states together. Positive lag requires `dt/tau <= .5`; this conservative
resolution guard is numerical, not a physical bandwidth limit. Invalid or
unresolved inputs are rejected. At least five periods are required so the
existing final-five-period metric has its full declared window.

## Mechanical ledger

With unit modal masses, energy and cumulative work have units `m^2/s^2`:

```text
E = (|v|^2 + k(t)*|q|^2)/2
W_actuator' = a dot v
W_pump' = -.2*sin(2*t)*|q|^2
D' = .04*|v|^2
residual = E(t)-E(0)-W_actuator-W_pump+D
```

Actuator work is signed work delivered to the mechanical modes. This ledger
does not specify electrical draw, actuator storage, efficiency or regeneration.
Using the clipped command instead of actual force produces an intentionally
wrong work ledger; a negative-control test exposes its discrepancy.

## Bounded comparison and checks

The reporter runs `tau = 0, .1, .5, 2 s`, each for 20 target revolutions with
256 and 512 steps per revolution. The existing tracking criterion remains
`<= .05 m` position RMS over the final five revolutions. No pass/fail outcome
for positive lag is assumed in advance. This four-point scan is not a located
continuous stability boundary or a proof of indefinite stability.

| Time constant, s | Coarse late position RMS, m | Meets existing .05 m criterion |
| --- | ---: | --- |
| 0 | 9.55280e-9 | Yes |
| .1 | .0172621645 | Yes |
| .5 | .0855793124 | No |
| 2 | .3736028352 | No |

Refinement preserves all four labels; the largest coarse/refined coordinate
difference is `2.707e-7`. These results establish finite-run tracking failures
at the sampled settings, not divergent motion or a general instability theorem.

Numerical reproduction gates, separately from the tracking criterion, require
maximum coarse/refined state-coordinate difference below `1e-5` in the declared
coordinates, late-RMS difference below `1e-5 m`, agreement of tracking labels,
and mechanical balance residual below `1e-5 m^2/s^2`. These are computational
diagnostics, not measured material tolerances; comparing displacement and
velocity coordinates is not a dimension-independent physical norm.

Tests include analytic constant-command exponential response, sinusoidal gain
and phase, resolved approach to zero lag, unchanged zero-lag trajectories,
negligible/limited-force baseline controls, independent sampled power and
angular-momentum quadratures under refinement, the wrong-command-work negative
control, and validation of the added input fields.

Reproduce using `python scripts/report_actuator_bandwidth.py --output
artifacts/actuator-bandwidth.json --summary artifacts/actuator-bandwidth-summary.json`.
Full traces are generated artifacts; the compact committed summary records
outcomes and normalized UTF-8/LF source hashes. Broader bandwidth, delay/noise
combinations and calibrated actuator design remain separate work.
