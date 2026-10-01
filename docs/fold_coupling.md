# Two-module fold energy exchange

The optional `scripts/report_fold_coupling.py` connects two existing nine-state
finite-reservoir modules. Each retains its geometry-derived inertia, restoring
potential, feedback source and separate losses. Module B begins at equilibrium,
at rest, with no reserve. Module A begins displaced and moving.

The connection has potential `U = (qA-qB)^T C (qA-qB)/2`, where
`C=diag(.003,.001)` acts on scale and fold-angle coordinates. Its generalized
forces are `FA=-C(qA-qB)` and `FB=+C(qA-qB)`. This is a synthetic coordinate
coupling, not a reconstructed spatial joint. The matrix entries carry the
corresponding energy-per-coordinate-squared units. Equal and opposite generalized
forces alone do not establish Cartesian momentum or torque conservation.

## Three independent accounts

1. Each module tracks mechanical energy, reservoir-supplied work, damping loss
   and work supplied by the connection.
2. The connection satisfies `U-U_initial + W_connection_A + W_connection_B = 0`.
3. Mechanical energies + both reserves + connection potential + all damping,
   conversion and leakage losses equal their initial total.

Connection work is not included a second time in the global total. The work
received by B need not equal the work lost by A at each instant: the connection
can release or store energy. Its initial potential in these runs is 1.05e-6 J.

## Results and controls

Four 10-second cases plus one refined run are recorded with complete initial
states and four source hashes in `experiments/fold-coupling-summary.json`.

| Case | Maximum global residual (J) | B mechanical energy at 10 s (J) |
| --- | ---: | ---: |
| Fueled A, coupled B | 2.477e-13 | 6.915e-6 |
| Disconnected modules | 1.833e-13 | 0 |
| Conservative, no fuel or damping | 1.861e-13 | 7.000e-6 |
| Deliberately reversed B reaction | 3.243e-5 | invalid as conservative transfer |

The conservative run demonstrates energy arriving at B without any reservoir
input. Its energy comes from A and the initially strained connection. The
disconnected B remains at rest. In the fueled pair, B receives 9.34127e-6 J of
connection work; some becomes damping loss, leaving 6.91478e-6 J mechanically.

Refining the fueled step .02 to .01 seconds reduces total residual from
2.47678e-13 to 1.04661e-14 J. Each coordinate/rate difference is below 9.887e-9
in its respective units. This demonstrates step agreement, not a measured
convergence order. The deliberately wrong reaction leaves individual module
work ledgers nearly balanced while breaking the connection and global accounts:
the checks localize the error to the coupling law.

Tests independently differentiate the spring potential and global energy,
recover the existing isolated module, check label-swap symmetry and synchronous
states, and verify transfer without fuel. Independent review obtained a global
directional-energy residual 3.39e-15 J/s; the wrong reaction produced the predicted
3.16e-6 J/s defect. No blocking mathematical issue was found.

## Remaining scope

This is two synthetic modules over a finite interval. No spatial placement,
intermodule collision clearance, material calibration, full-structure recursive
coupling or sustained breathing is established. Stage/endpoint coordinate-domain
checks are inherited; they do not certify continuous physical trajectories.
Next: compose a small graph with each connection owning its stored energy once,
and test that module-local and graph-global energy totals remain consistent.
