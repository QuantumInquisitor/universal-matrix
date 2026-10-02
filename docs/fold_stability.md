# Replenished folding: continuation and small-disturbance audit

This experiment continues the saved powered state at physical time 20 seconds
from `fold_supply.md`, aiming for physical time 60 seconds. It changes no
mechanical or charging equations. The declared geometry limits still apply.
The seed report and all of its source hashes are checked before continuation.

## Restart and energy ownership

The restart retains each node's coordinates, velocities and reserve. It resets
cumulative work, losses, connection-work and received-energy ledgers to zero.
Those ledgers record the interval; they do not drive the equations. Each new
account starts from the actual energy and reserve at the restart. Replaying a
state with rebased ledgers must give the same physical derivative.

The reference branch continues unchanged. The disturbed branch multiplies all
node velocities by 1.01 at the same coordinates and reserves. This is a declared
one-percent initial velocity intervention, not unaccounted emergent energy.
For the pinned seed this adds 1.2086158011e-8 J (12.086 nanojoules).
Its preparation energy is calculated independently as
`Delta E = (1.01^2 - 1) sum_i [v_i^T M_i(q_i) v_i / 2]`.
Elastic and connection energies do not change at the intervention. Subsequent
source input is tracked separately. Both branches use the same charging law
and power cap; actual received energy can differ because charging depends on
reserve state. This is not an equal-received-energy comparison; comparing full
energy from before the intervention must include this preparation energy.

A finer reference continuation checks numerical agreement at a shared end
time. Each completed case is checkpointed with source and seed provenance so
an interruption does not erase its results.

## What the comparison can establish

Compare coordinates and rates separately at common times, using only
interpolation inside accepted solver steps. Do not compare samples taken at
different times or extrapolate beyond a terminated run. The last requested ten
seconds are analyzed only to the extent they were actually reached; missing
coverage must be explicit.

Energy trends and coordinate/rate ranges describe a finite observation window.
A single disturbance cannot establish a stable limit cycle. In particular,
phase displacement can persist even near an attracting periodic orbit, while
bounded motion over a short interval can precede later growth. Neither distance
between two trajectories nor visual repetition alone proves attraction.

If a solver stage leaves the declared geometry or reserve scope, the report
retains the last accepted state. That is not an exact boundary crossing or a
physical collision result. No domain widening, reserve clipping or energy
threshold relaxation is used to keep a run going.

## Reference continuation observation

The reference branch reaches physical time 60 seconds without a declared-domain
stop. Mechanical plus connector energy grows from 33.8093 to 49.2218 microjoules
across physical time 50-60 seconds, an endpoint increase of about 45.6 percent.
The corresponding endpoint slope is 1.5413 microjoules per second. This is a
finite-window observation of continuing growth, not an asymptotic growth-rate
estimate or a proof that growth will continue indefinitely.

## Disturbance and numerical checks

All three branches complete physical time 20-60 seconds, with 161 shared samples.
The disturbed branch ends at 49.2986 microjoules. Maximum coordinate separations
are 0.000308773 in scale and 0.000648664 radians in fold angle. This alone does
not measure attraction because phase and received energy can differ.

The finer reference differs by at most 1.339e-8 in scale and 2.484e-8 radians;
maximum rate differences are 5.600e-8 per second and 1.184e-7 radians per second.
Maximum mechanical-energy difference is 2.259e-12 J. The largest subgroup/root
accounting residual across the three cases is 3.424e-12 J. All recorded reserves,
capacity and input-budget checks pass. These are numerical consistency checks,
not calibrated physical accuracy.

Seventeen focused tests cover restart invariance, independent kick energy,
source/seed tampering, independent subgroup derivatives, short RK4 agreement,
scope handling and invalid settings. The workflow acceptance also checks full
window coverage, provenance, budget residuals and common-time refinement.

## Reproduction

The adaptive integration requires the `scientific` extra (SciPy); plotting
uses the `visualization` extra. The seed is pinned using normalized UTF-8 text
hashing so Windows and Linux newline conventions do not change provenance.

```sh
uv run --extra scientific python scripts/report_fold_stability.py --output artifacts/fold-stability/report.json
uv run --extra visualization python scripts/plot_fold_stability.py --input docs/experiments/fold-stability-summary.json --output artifacts/fold-stability/computed-stability.png
```

## Next discriminating test: supply threshold

For a general unit-size source coefficient p (watts), the resting reserve is
`Req/Rcap = p/(p+3e-6)`. Linearizing the velocity feedback at rest gives the
multiplier `8p/(3p+3e-6)` relative to damping. It equals one at
`p = 6e-7 W` (0.6 microjoules per second at unit size). The present coefficient
is ten times that threshold and gives multiplier 16/7.

This predicts the sign of linear damping near rest under the current synthetic
laws. It does not locate a finite-amplitude stable cycle. A useful next test is
a controlled sweep below, near and above this onset while preserving the same
source accounting and geometry limits, followed by longer runs only where the
amplitude appears to settle. This separates the imposed feedback mechanism
from an unsupported claim of spontaneous or physically validated breathing.

## Boundaries

The power port remains an ideal external source with uncalibrated material
parameters. A continuation within this model does not validate physical
hardware, the whole recursive structure, XR fidelity or a time-crystal timing
advantage. Sustained breathing remains an open hypothesis until the required
motion, robustness and energy evidence is established.
