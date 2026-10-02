# Finite-source folding over longer intervals

This experiment extends the mixed-size reservoir network in
`fold_active_multiscale.md` without changing its equations. It asks whether the
short transient persists as the finite reservoirs drain. No refill is added.

## A bound independent of the numerical trajectory

For node size s, reserve obeys `Rdot = -P/.8 - (.15/s) R`, with
`P >= 0`. Therefore `R(t) <= R(0) exp(-.15 t/s)` while the model is valid.
The feedback force has coefficient `4 R/(R+Rstar)` relative to damping.
It becomes no stronger than damping when `R <= Rstar/3`.
Since `R(0)=2 Rstar`, this occurs no later than `s log(6)/.15` seconds.
For the largest node this upper bound is approximately 11.945 seconds.
Smaller nodes reach their bound earlier. Reserve cannot subsequently increase.

After all nodes pass that threshold, the derivative of total mechanical plus
connector energy is nonpositive: conservative connector transfers cancel and
every remaining velocity-dependent term is dissipative. This rules out
indefinitely powered motion for this unreplenished model. It does not prove
that the coordinates reach equilibrium at any finite time, establish a decay
rate, or establish validity outside the declared geometry domain.

At 60 seconds, the largest reserve fraction is bounded above by `exp(-9)`
(about 0.01234 percent). The two half-size nodes have the tighter `exp(-18)`
bound. A one-percent reserve crossing is a reporting threshold, not exact
exhaustion; these equations approach zero continuously. The latest one-percent
crossings from leakage alone are approximately 30.701, 23.026, 15.351 and 15.351 seconds for
nodes 0 through 3. Useful work can only make those crossings earlier.

## Numerical protocol

Compare gain-four feedback, zero-gain passive mechanics and exact equilibrium
with leaking reserves. Keep the original coordinate domain. A rejected solver
stage is reported with the last accepted state and time; it is not a certified
boundary-crossing time or a physical collision finding. Unknown errors must
not be disguised as expected domain stops. All energy ledgers remain separate.

Timestep/tolerance refinement tests numerical agreement independently of the
analytical depletion bound. Sampled extrema and threshold brackets describe
accepted numerical states, not guaranteed extrema between states.

## Results

All three runs reached 60 seconds within the model domain. The active case
used 1,871 accepted steps; passive mechanics used 1,693 and exact rest used
1,201. Every reserve stayed positive and decreased. At 60 seconds the active
reserve fractions were 6.9064e-5, 4.5880e-6, 1.3988e-8 and 1.3850e-8.

| Active node | First accepted-endpoint bracket below 1% (seconds) |
| --- | --- |
| 0 | 27.91895 to 27.95163 |
| 1 | 22.04491 to 22.07788 |
| 2 | 15.16578 to 15.19336 |
| 3 | 15.16578 to 15.19336 |

Active total mechanical plus connector energy fell from 4.9344e-7 J initially
to 5.0280e-8 J at 60 seconds after an initial amplification transient. There
were no positive energy increments across the 1,443 accepted intervals wholly
after the analytical damping threshold. Passive mechanical energy decreased
to 8.1962e-9 J. Exact rest retained zero motion and matched exponential leakage.
These endpoint checks supplement the analytical bound; they do not prove
pointwise numerical behavior between accepted endpoints.

Maximum root balance errors were 5.3307e-14 J (active), 1.8574e-14 J (passive)
and 5.4211e-20 J (rest). The finer active run reduced its maximum root error to
5.0714e-15 J. Final coordinate and rate differences were at most 7.1395e-10
and 1.1895e-9 respectively, with energy-state differences below 1.937e-14 J.
Two settings establish numerical agreement, not a convergence order.

Eighteen focused tests passed across the original 17-test run and one added
negative-reserve stage-stop test. Source hashes, Ruff/format and the complete
workflow acceptance checks passed. The computed plot was visually inspected.
The full four-integration report took approximately 10.5 minutes on the local
Windows host; CI has a separate duration job to keep this work isolated.

## Reproduction

The adaptive solver requires the project's `scientific` extra (SciPy); plotting
requires its `visualization` extra. The source-hashed numerical report is
`experiments/fold-duration-summary.json`. Its accepted-step accounting covers
all accepted solver endpoints; compact plotted samples are less frequent.

```sh
uv run --extra scientific python scripts/report_fold_duration.py --output artifacts/fold-duration/report.json
uv run --extra visualization python scripts/plot_fold_duration.py --input docs/experiments/fold-duration-summary.json --output artifacts/fold-duration/computed-duration.png
```

The report records solver settings, initial/final states, termination reasons,
reserve threshold brackets and separate energy accounts. The plotting script
checks the source hashes before showing the saved samples.

## Limits

This is a synthetic finite-source experiment. Material calibration, reservoir
hardware, real attachments, collision clearance, full recursive assembly and
XR mapping remain separate open tasks. Sustained breathing would require a
specified energy source and a demonstrated stable motion regime; it cannot be
inferred from this unreplenished transient.


## Next experiment boundary

A replenished version must specify an input power law and track its source.
If node i receives power J_i, its reserve law gains that term, and the total
account subtracts the integrated injected energy. That is a new model to test,
not a reinterpretation of the current finite-source result. Before claiming
sustained breathing, compare it with passive and externally driven controls,
measure startup dependence and robustness, and verify every energy transfer.

A proposed time-crystal timing component would need its own control-interface
and drive-energy accounting. Changing a timing signal does not remove the
finite-energy bound of the present model. Component usefulness must be tested
against the same input-power budget and an ordinary timing control.
