# Finite reservoirs in a mixed-size fold network

This optional experiment adds finite internal energy sources to the passive
network in `fold_multiscale.md`. Body geometry, inertia and mapped connector
potentials retain their previous assumptions. Each node receives its own
size-dependent reservoir; no external replenishment or time waveform is added.

## Explicit size laws

For body size s relative to the reference specimen:

| Quantity | Rule | Interpretation |
| --- | --- | --- |
| Initial reservoir capacity | `2e-5 s^3 J` | Assumed constant stored-energy density |
| Feedback activation energy | `1e-5 s^3 J` | Same normalized reserve fraction |
| Generalized damping/feedback matrix | `s^4 D0` | Preserves the chosen mechanical similarity |
| Leakage coefficient | `.15/s per second` | Leakage timescale proportional to length |
| Conversion efficiency | `.8` | Fixed synthetic efficiency |
| Feedback gain | `4` | Fixed dimensionless gain |

The feedback force is `A = gain R/(R+Rstar) s^4 D0 v` and delivered power
`P = A dot v`. Reserve decreases at `-P/efficiency - leakage R`.
Conversion loss is `(1/efficiency-1)P`; damping loss and leakage loss are
tracked independently. Thus delivered work cannot exceed efficiency times
the initial reserve. Empty reserves disable feedback; negative numerical
reserves are rejected without clipping.

Under uniform global scaling by lambda, coordinates follow corresponding
times t/lambda and rates scale inversely. The feedback activation fraction is
unchanged, generalized forces scale cubically, and delivered/leakage power
scales quadratically. Integrated work, reserves and losses scale cubically.
These are model choices needed for similarity, not measured storage-device
properties. A fixed leakage coefficient is a different, energy-conserving
law that generally does not preserve the same time similarity.

## Accounting and failure controls

Each node has separate mechanical and reservoir accounts. Each connection
owns its potential once. Every group's inclusive total includes its descendants'
mechanical energy, reserves and all losses, plus internal connection potentials;
boundary work explains changes. Parent and child totals overlap and must not
be summed across levels. Reservoir work is an internal transfer, not additional
energy to add to the global total.

The four-node network has relative sizes 1, .75, .5 and .5. Only node 0 starts
displaced and moving; all nodes begin with their stated finite reserves.
Three uniformly scaled runs test corresponding time evolution. A deliberately
omitted reservoir debit at node 1 should break that node's reserve account and
ancestor totals, while mechanically honest work accounts can still pass.
A separate half-timestep run checks integration agreement.

The reproduction report is `experiments/fold-active-multiscale-summary.json`.
It retains source hashes, initial states, settings and separately measured work,
losses, connection energies and group totals.

## Computed results

The three valid runs have maximum whole-network residuals of 4.632e-16,
1.954e-16 and 5.789e-17 J at global scales 1, .75 and .5 respectively.
The omitted node-1 debit creates a 2.438e-9 J discrepancy, localized to that
reservoir, its subgroup and the root. Mechanical and connection accounts
continue to pass. Every valid reserve remains positive and decreases.

Halving the timestep at global scale .5 reduces the root residual from
5.789e-17 to 3.131e-18 J. Maximum final coordinate and rate differences are
2.033e-10 and 1.192e-9 respectively. This is a refinement check, not a
convergence-order claim. Exact binary half-scale agreement is structural
similarity in this numerical model, not independent experimental validation.

Validation: 19 focused tests, including independent energy derivatives,
unit-size reduction, empty-reservoir and zero-gain passive reductions,
finite supply, invalid inputs and deliberate missing-debit detection.
Generate the computed visualization with:

```sh
python scripts/plot_fold_active_multiscale.py --input docs/experiments/fold-active-multiscale-summary.json --output artifacts/fold-active-multiscale/computed-network.png
```

The plot verifies source hashes and uses the report's saved samples.

## Limits

Finite stored energy can amplify transient motion but cannot supply unbounded
work. A one-second reference interval does not establish a sustained oscillation,
stable limit cycle or spontaneous startup from exact equilibrium. No material
calibration, physical reservoir implementation, real attachments, collision
clearance or whole-structure recursive validation is claimed.
