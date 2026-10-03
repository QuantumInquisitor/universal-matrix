# Recovered powered-material validation controls

This test-only port recovers three bounded controls from the preserved original
`work/universal-matrix-current/tests/test_fold_material_supply.py`. Its raw SHA-256
is `b9aa86129e677a177cc743153eb9c2ffdf843cfa8fa188126e7cf16926e1f410`.
The associated original module hash is
`c8cb1c531548fdff188b69abb3250762f1a9dc06075df0a68b44d518a43ae11a` and saved summary
hash is `a493879dc3baea8fc3286026388f82afd175205270b265b3f661ffa24e0bb8ed`.
These identify preserved scratch evidence, not files to import or overwrite.

The accepted implementation already supplies powered constitutive material
mechanics. Its equations are consolidated in `report_fold_material_supply.py`;
the scratch module is not a missing engine feature. This recovery imports only
the accepted implementation and adds tests in
`tests/test_fold_material_supply_recovered.py`:

- Gain-zero and reserve-zero mechanical reduction to the accepted **constitutive
  material** passive graph with external source off, including damping and
  connector-work rates. Reserve/leakage ledgers are not mislabeled passive state.
- Independent centered finite differences of measured node/edge/group energy
  along the powered derivative with nonstationary modules and nonzero saved
  ledgers. External input is included exactly once. Omitting that input leaves a
  detectable apparent source in the root account.
- Full 48-component derivative similarity under length/time scale .5, with
  velocity scaling inversely, stored/cumulative energies scaling cubically and
  energy rates scaling quadratically, including the external input ledger. The
  supplied-input fixture is nonzero; unchanged input power would fail.

The port maps the accepted measurement's five-value return explicitly (groups at
index 4, rather than scratch index 3). All four nodes move and their coordinates
are perturbed; nonzero cumulative ledgers require true centered differences.
The energy finite differences use the original epsilon 1e-5 plus 5e-6 as a
bounded differencing check. Both must satisfy the original scratch energy bounds:
node absolute 2e-13/relative 2e-6; edge absolute 1e-15/relative 2e-7; group
absolute 3e-13/relative 2e-6. No claim of monotonic convergence below roundoff is made.
The derivative similarity bound remains relative 2e-13/absolute 1e-20.

Run the new instantaneous controls with:

```text
python -m pytest -q tests/test_fold_material_supply_recovered.py
```

No integration trajectories run in this file. The accepted RK45 equations,
schemas, tolerances and existing test criteria are unchanged. This does not port
the scratch RK4 trajectory suite or strict upper-capacity stage rejection: that
rejection is a different API policy and remains a separately scoped decision.
Longer passive-limit/full-state trajectory comparisons remain separate potential
follow-ups. No hardware supply, new material calibration, distributed powered
inertia, physical joints or stable breathing is established.
