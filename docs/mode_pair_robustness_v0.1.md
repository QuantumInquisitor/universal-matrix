# Paired-mode tracking: limits of the recovered ideal controller

30 September 2026. This implements a scoped classical control from the recovered
24 September `quantum_mode_pair_solution.md` and tests limitations that were
previously explicitly unfinished. No quantum bath, particle interpretation or
full moving-material model is implemented.

## Model and experiment

The two spatial partners obey `q'' + .04 q' + k_actual(t) q = f`, where
`k_actual(t)=stiffness_ratio * [1+.2 cos(2t)] /s^2`.
The target is `q_d=(cos(t),sin(t)) m` at angular frequency 1 rad/s.
The controller assumes stiffness ratio one and uses

```text
f = (k_assumed-1) q_d + .04 q_d'
    + (k_assumed-1) e_measured - .6 e_measured'.
```

With exact, instantaneous measurements and no clipping, substitution gives
`e'' + .64 e' + e = 0`. It actively supplies the traveling response;
it does not generate spontaneous chirality. Error starts at (.25,0) m with
zero velocity error. The negative-time history keeps this error constant
relative to the target. Coefficients and scales are synthetic.

Limit the Euclidean force-per-mass norm to `force_limit`. For delay tau, measure
the actual state and desired state at `t-tau` and apply that old error with the
current feedforward command. Add a deterministic measurement disturbance with
components `a(sin(7t),cos(11t),cos(7t),sin(11t))` to the measured displacement
and velocity, in m and m/s respectively. This specified two-frequency disturbance
is not a stochastic noise ensemble or a bandwidth-independent robustness test.

Integration uses RK4 with interpolated stored history for positive delay,
256 steps per target revolution, and 20 revolutions. Positive delay must be at
least one step; zero delay uses each RK stage's current state. The final five
revolutions define the position RMS tracking error. The declared target is
<=.05 m, or 5% of the unit-radius target. It is an engineering comparison
threshold, not an experimentally calibrated tolerance.

## Results

All unmentioned parameters retain the ideal values: force limit 10 m/s^2,
zero delay/disturbance and stiffness ratio one.

| Change | Late position RMS, m | Meets .05 m target |
| --- | ---: | --- |
| Ideal | 9.55e-9 | Yes |
| Force limit .05 m/s^2 | 5.2128 | No |
| Delay .1 s | 5.32e-5 | Yes |
| Delay 1 s | 5.55e-5 | Yes |
| Delay 2 s | 810.99 | No; large growing error in the tested record |
| Measurement disturbance amplitude .02 | .0002002 | Yes |
| Stiffness ratio 1.02 | .031392 | Yes |
| Stiffness ratio 1.05 | .078281 | No |
| Stiffness ratio 1.2 | .299704 | No |
| Limit .15, delay .1, disturbance .02, stiffness 1.2 | .689125 | No |

The last case clips at about 82.66% of recorded sample times. All force commands,
including RK stages, are norm-clipped; the reported fraction samples grid times.
At the specified settings, the observed pass/fail bracket is between 2% and 5%
stiffness mismatch and between 1 s and 2 s delay. These sparse comparisons do
not establish unique, monotone or exact stability thresholds. The large errors
are failures of this synthetic control, not predicted physical displacements.

Nine tests pass: the exact ideal error solution, the unforced circulation law
`ell(t)=ell(0) exp(-.04t)`, force limiting, delayed/disturbed step refinement and
input guards. The additional 2 s delay run at 512 steps checks that its failure
is not removed by halving the integration step; its full result is retained.

## Reproduce and remaining work

```text
uv run python scripts/report_mode_pair_robustness.py --output artifacts/waves/mode-pair-robustness.json
uv run python -m pytest -q -p no:cacheprovider tests/test_proposed_mode_pair_control.py
```

The output contains all trajectories, the ten comparison cases and one delayed-
failure refinement. W2 is advanced from an ideal scratch derivation to an
optional engine module and finite robustness grid. Remaining work includes
controller redesign or calibration for the exposed mismatch sensitivity,
stochastic noise ensembles, broader parameter/delay thresholds, real actuator
bandwidth, and coupling to physical material dynamics. No work/loss budget for
the connected folding structure is claimed by this controller study.
