# Time-crystal subsystem candidate: a timing input for the Matrix Engine

30 September 2026. **The question is what a time-crystal subsystem could do in
the engine, not whether the entire engine is a time crystal.** This experiment
tests one role: delivering repeatable ticks to the existing canonical clock.

## Source model and declared interface

The finite simulation implements Eq. 1 of
[Mi et al., Time-crystalline eigenstate order on a quantum processor](https://www.nature.com/articles/s41586-021-04257-w):

```text
U_F = exp[-i sum(h_i Z_i)/2]
      exp[-i sum(phi_i Z_i Z_(i+1))/4]
      exp[-i pi g sum(X_i)/2].
```

The rightmost pulse acts first. Independent quenched fields are uniform on
[-pi,pi] and nearest-neighbor coupling angles on [-1.5pi,-.5pi], with open
boundaries. Those distributions and the .97 near-pi setting come from the
paper. We use exact state-vector evolution for 6 and 8 spins, not the paper's
20-qubit experiment or its phase-validation procedure.

The application design below is ours. Each seed fixes the disorder and a
random initial computational-basis bit string. The source signal is
`C(n)=mean_i[z_i(0) <Z_i(n)>]`. Keeping the initial signs avoids cancellation
between differently prepared spins. Two signal versions are recorded: the
exact ensemble expectation, and a 256-shot estimate sampled from the full
joint computational-basis probabilities at each endpoint.

The receiver accepts only adjacent samples confidently below -.2 then above
+.2. That negative-to-positive edge advances one routing tick through the
existing `canonical_polarity_clock.clock_node` and phase functions. Missing or
weak samples suppress the tick; the receiver never reconstructs missing edges
from expected parity. Thus a complete source oscillation lasting 2 drive
periods supplies one engine tick. The existing 36-tick engine cycle would take
72 drive periods under this explicitly chosen mapping. No physical duration
of a period is assigned, and no production clock configuration is replaced.

The test judges delivery against edges at drive cycles 2,4,... and requires
zero missing or extra edges. The same receiver and threshold apply to every
source. Its outputs include exact tick errors, unresolved-sample fraction and
the final canonical node/phase. This establishes an optional software adapter,
not a physical actuation or breathing connection.

## Comparisons and results

There are 168 spin-chain runs: two sizes, eight seeds, four pulse factors
g=1,.97,.9,.6, both interaction-on and interaction-off; additional .97 runs
with pulse-angle and readout errors; and four seeds at N=8 run four times
longer. Default duration is 256 drive periods, expecting 128 engine ticks.
The longer run expects 512 ticks over 1,024 periods.

| Source / condition | Complete finite-shot tick delivery |
| --- | --- |
| Interacting, g=.97, 256 periods | 16/16 cases |
| Same preparation and fields, interactions removed, g=.97 | 0/16 cases |
| Interacting, g=.97 with errors described below | 16/16 cases |
| Interacting, g=.97, N=8, 1,024 periods | 4/4 cases |
| Interacting, g=.9 | 15/16 cases; one N=8 record missed a tick |
| Interacting, g=.6 | 0/16 cases |
| Perfect pulses g=1, either interaction setting | 32/32 cases |
| Ordinary coherent phase accumulator, g=.97 | 107 detected ticks; fails delivery target |
| Ideal digital divide-by-two driven by the same input pulses | 128/128 ticks; passes |

The explicit error condition adds independent Gaussian pulse-angle-factor
variations with standard deviation .01 around g=.97, plus independent 5%
bit flips in the endpoint readout. It does not model drive timestamp jitter,
decoherence, leakage, or fluctuating interaction gates. The ordinary phase
accumulator samples `cos(pi*g*n)`; it accumulates pulse-factor error without
locking. The digital divider does not depend on rotation-angle calibration.
This is a functional comparison, not a matched hardware-cost experiment.

Maximum state-norm error across all runs is 7.15e-13. Independent tests compare
factorized propagation with a dense matrix exponential, verify exact pi-flip
and no-pulse limits, check decoder failures, and exercise a nonideal source
through two complete canonical cycles. The 20-test timing/canonical-clock
batch passes. Eight disorder/state seeds are a finite sample, not a reliability
guarantee or an exhaustive parameter window.

## Engineering conclusion

**The modeled candidate can supply the engine's clock input, and interactions
improve this particular spin signal's tolerance of pulse imperfections.**
It does not outperform the ideal ordinary divider in this test. There is no
established practical advantage that justifies replacing the default timing
system. Retain this as an optional investigational subsystem, especially if
future engine work already needs a driven interacting-spin platform.

The main unresolved interface is readout. The paper uses repeated endpoint
measurements; the simulation follows that interpretation. Producing all 257
endpoint estimates at 256 shots each would involve 65,792 state preparations
and 8,421,376 total Floquet periods across those shots, assuming separate
preparation for every endpoint and shot. This is not continuous free readout
from one evolving device. Per period the model applies N transverse rotations,
N field rotations and N-1 interaction rotations when enabled. No energies in
joules can be inferred without hardware Hamiltonians, durations and controls.

Physical readout backaction, loading, latency, feedback, noise channels and
resource comparison remain untested. The stroboscopic record cannot measure
within-period timing jitter or provide an absolute reference independent of
its drive. Neither a fabricated time-crystal component nor a full physical
engine integration has been demonstrated.

As a separate application lead, [Qiao et al., Floquet-enhanced spin swaps](https://www.nature.com/articles/s41467-021-22415-6)
report improved finite-system spin-eigenstate swaps using related driven
interactions. Their projection-SWAP result is distinct from a coherent SWAP
gate and from a strict many-body time crystal. That suggests an additional
future role in state protection or transfer, not a capability implemented here.

## Reproduction and artifacts

```text
uv run python scripts/report_time_crystal_subsystem.py --output artifacts/time-crystal
uv run python -m pytest -q -p no:cacheprovider tests/test_time_crystal_clock_subsystem.py tests/test_canonical_polarity_clock.py
```

Full inputs, states' local polarizations, exact and finite-shot signals,
decoder events, summaries and source hashes:
`artifacts/time-crystal/time-crystal-subsystem.json`. Inspection figure:
`artifacts/time-crystal/time-crystal-subsystem.png`. Model and receiver:
`src/time_crystal_clock_subsystem.py`.
