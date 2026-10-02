# Contact and phase/current continuation

This supplements CHECKPOINT_2026-10-02_RECURSIVE_SPATIAL_PHASE.md. It does not
replace its prior results or the wider tasks.json queue.

## Spatial lane: green PR #143, not merged

PR #143 head 3400bf5fb09c49fc9e36c0ba5e96c7fd6080a29b passed workflow
https://github.com/QuantumInquisitor/universal-matrix/actions/runs/36951074833
after six Ruff-only formatting changes. The Python syntax tree is unchanged.

Its local numerical bracket is
`14.964074019232122 < boundary <= 14.964074019742913`, width
`5.10791409169542e-10`. Upper clearance is `1.2934153748034363e-11 m`, with
collision tolerance unchanged at `1e-11 m`. Root panel-0 versus depth-3
[0,1,1] panel-5 remains governing at both scales 1.1 and child theta 0.
Root-theta difference is zero; the full 15-module broad-grid control passes.
This is not global continuous certification or manufacturing clearance.

PR #143 and this phase/current audit are sibling branches from the recovery
branch, so neither needs the other's unmerged implementation. Recheck their
live heads and review disposition before integration.

## Phase/current lane: reproducible finite contract audit

The parallel zero-fit comparison requested in the earlier checkpoint is now
implemented in scripts/report_phase_current_contract.py with focused tests
and CI. The conserved quantities and dimensional gaps are specified in
docs/phase_current_contract.md. No physical units conversion is invented.

Local validation: 30 tests pass, including the existing U(1) continuity/Gauss
and mechanical modal phase tests. Twelve mechanical fixtures and ten gauge
fixtures pass. Maximum independent storage-derivative balance residual across
three finite-difference steps is 3.682951601297838e-14 W. Deliberately reversed
child power and missing gauge-link transformation are detected. Ruff passes.

Remote CI must validate the published head independently. This audit does not
close the physical adapter, full trajectory comparison or plasma questions.
The checked report is docs/experiments/phase-current-contract.json.

## Other work preserved

P11 has an existing computed-state adapter; direct viewer consumption with
units, provenance, energy ledger, replay and visual/headset validation remains.
The physical attachment frame remains unresolved despite the completed marker
searches. Keep the abstract connector labeled as a reduced coordinate.

P04/P07/P08 geometry, materials and energy work remains distinct from relative
folding of the separate 69-domain flow assembly. P05 wave/control, P06 timing
component usefulness and P12 source/experiment queues remain independent.
Some older task-register summaries lag merged work; reconcile against the
checkpoint addenda and executable sources rather than restarting experiments.

The older local aperture checkout and its uncommitted supply files were not
changed. Synced project sources remain read-only.
