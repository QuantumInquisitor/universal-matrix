# Time-order diagnostics and nonlinear standing-wave control

Local numerical investigation, 30 September 2026. This advances the W1 backlog
and supplies comparison cases for the crystal investigation. It does not couple
the wave to the connected folding specimen or establish a time-crystal phase.

## Declared model

The existing `RingMode` supplies the linear scales. The optional extension is

```text
q'' + 2 gamma q' + omega^2 [1 + h cos(Omega t)] q + beta q^3 = 0.
```

The base uses L=2 pi m, wave speed=1 m/s, spatial mode n=1, gap=0,
omega=1 rad/s, gamma=.02/s, h=.2, Omega=2 rad/s, beta=1/(m^2 s^2),
q(0)=.01 m and q'(0)=0. These are synthetic declarations; beta was not derived
from the folding panels, measured materials, or the cited time-crystal papers.
The cosine spatial mode remains selected in advance. Its amplitude evolves
numerically; no sinusoidal output is prescribed for that amplitude.

`nonlinear_trace` uses DOP853, relative tolerance 1e-9, absolute tolerance 1e-11,
and maximum step T/32, where T=2 pi/Omega. The normal run lasts 400 drive
periods. Refinement uses T/64 and tolerances 1e-11/1e-13; the longer run lasts
800 periods. These checks support the reported finite trajectories, not a
proof of infinite lifetime or a global stability theorem.

## Diagnostics

At a fixed drive phase, record the vector `(q, q'/omega)` in metres. Inspect the
last 128 samples. Remove its mean and calculate the state RMS, normalized
one- and two-cycle differences, alternating-vector coherence, and the ratio
of RMS in the second half to the first half. A 1e-8 m signal floor suppresses
ratios of effectively vanishing traces. Records are cropped to equal even
halves. Coherence can exceed one by floating-point roundoff.

A T-periodic oscillator appears constant when sampled once per drive period;
an unresolved centered record does not imply no motion between samples.
Displacement-only sampling can hit a node, hence the velocity coordinate.
Sample times and drive phase are caller obligations; the diagnostic does not
infer them from an arbitrary record. These functions deliberately return no
time-crystal classification.

## Measured results

| Case | Last-window state RMS, m | Result |
| --- | ---: | --- |
| Cubic base | .3590132 | Nearly stationary alternating response |
| No cubic term | 3.32149e13 | Continued linear growth; late/early RMS ratio 412.21 |
| No pump | 9.10e-11 | Below the diagnostic floor |
| Strong damping, gamma=.08/s | 9.05e-15 | Below the floor |
| Exactly zero initial state | 0 | Remains zero in the deterministic model |
| Omega=1.8 rad/s | 1.81e-11 | Below the floor |
| Omega=1.92 rad/s | .1303733 | Alternating late response |
| Omega=2.08 rad/s | .5072534 | Alternating response with larger remaining transient |
| Omega=2.2 rad/s | 3.91e-10 | Below the floor |

For the base, the normalized two-cycle error is 1.77e-8, alternating coherence
is approximately one, and late/early RMS is .9999999977. The refined final
state differs by 1.45e-13 in the numerical `(q,q')` coordinates. Doubling run
duration changes the final state by 1.75e-11 and reduces the late two-cycle
error to 2.27e-13. These coordinate-norm comparisons use the declared units;
they are numerical consistency measures, not a unit-independent physical norm.

The opposite seed produces the opposite phase with zero observed symmetry
error. A velocity-only seed reaches the same sampled RMS. Restarting after 400
periods with q multiplied by 1.2 and velocity increased by .02 m/s returns
within 7.91e-8 of a phase-equivalent base state after 200 more periods.
Only this one disturbance was tested. The five detuning points do not locate
a phase boundary or prove robustness throughout the intervals between them.

The enormous linear amplitude is an extrapolation of the selected linear
equation beyond a credible material regime, retained to demonstrate its missing
saturation mechanism. It is not a prediction of a physical displacement.

## What the time-crystal comparison establishes

An imposed alternating sequence passes the same strong two-cycle diagnostics.
The ordinary single-mode cubic control also has a stable-looking subharmonic
response over the tested record. Thus period doubling, coherence, phase choice
and recovery from one perturbation do not by themselves establish collective
time-crystal order. No interacting many-body limit, spatial order, lifetime
scaling, disorder ensemble or thermodynamic limit was tested here.

This supplies a necessary comparison for the separately reviewed time-crystal subsystem research.
The investigation must next distinguish collective ordering from these ordinary
responses. W1 still needs multimode competition, spontaneous spatial pattern
selection, realistic finite boundaries and empirical coupling. The connected
fold still needs its own material/energy model and recursive coupling.

## Reproduce

```text
uv run python scripts/report_time_order_controls.py --output artifacts/waves
uv run python -m pytest -q -p no:cacheprovider tests/test_time_order_diagnostics.py tests/test_proposed_nonlinear_wave_control.py tests/test_proposed_scalar_wave_control.py
```

The 52-test batch passes, including agreement with the existing linear
monodromy, an analytic damped oscillator, a conservative cubic invariant,
vanishing-seed behavior and misleading imposed-signal controls. Full traces,
parameter choices, source hashes and diagnostics are in
`artifacts/waves/time-order-controls.json`; the figure is `artifacts/waves/time-order-controls.png`.

The other resumed wave task is documented in
[paired-mode robustness](mode_pair_robustness_v0.1.md).
