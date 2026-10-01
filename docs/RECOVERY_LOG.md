# Matrix Engine recovery and execution log

This is the durable resume point for the catch-up program. Read the [plan](RECOVERY_PLAN.md), [task register](recovery/tasks.json), and the latest dated entry before starting work. Update this log at each substantive checkpoint, including failures and interruptions. A plan, passing unit tests, publication and empirical validation are different states.

Latest checkpoint: the aperture integration entry below records 121 passing
tests, six reproduced signed-current cases and publication in draft PR 124.
Earlier next-action lists are historical snapshots.

The objective is a connected, breathing, folding recursive engine. Experiments have priority; the viewer must inspect actual computed state. Time crystals are optional subsystem candidates. Source documents and historical claims do not override tested implementation or supply missing physical inputs.

Each future entry must record: task IDs, baseline/branch, question and assumptions, changes, commands or reproducible procedure, result and limits, evidence locations, publication state, blockers and exact next action. Never mark work complete because a process started or a conversation promised it. Keep old entries; add corrections with a reference to the superseded statement.

## 30 September 2026 recovery and repository checkpoint

Baseline: main `a78576f83854a5b75c90815db121b1ca40a4f606`. The prior combined local experiment commit `fe414773d7dd24bba7217bbe9f809dcf0ee16df5` remains on its separate branch. This recovery branch starts from main and changes documentation/evidence only.

Work completed in this batch:

- Recovered a 12-step plan and 39 task records, including independent observational/source work and the older fundamental-physics program omitted by the first conversation-based plan.
- Inspected both known local repositories, worktree metadata, stashes, reflogs, unreachable objects, scratch experiment folders, source/test files and generated results. Both Git repositories reported no stashes or unreachable objects. The older checkout was clean; generated artifacts were untracked in the current checkout.
- Inventoried 2,859 files, including 2,447 hashed text/code files and 776 candidate question/status lines. These counts include duplicate and obsolete records and are not counts of experiments. Large/raw inventories remain local; they must be semantically reconciled before task closure.
- Enumerated 138 remote branches and all 121 PR records then present. Open issue enumeration contained the five open PRs and no separate open issue records.
- Completed remote comparisons for all 74 branch tips previously unavailable in the current clone: five ahead of main and 69 diverged. Sixty-four other tips are ancestors of main. Of the divergent branches, 54 have merged PR records at that exact tip; one E8 branch has a merged PR by name but a different tip and requires comparison. Fourteen historical exceptions received exact Git blob comparisons. See the JSON evidence files below.
- Confirmed that the two changed blobs on the old white-paper hierarchy branch are identical to main. The historical PR 7 closure explicitly explains why its separate transition kernel was superseded; preserve that decision.
- Found an unmerged patterned-Neumann-face-flux candidate. It adds spatial boundary-array validation and `solve_open_gauss_with_face_flux`; those functions are absent from main. Retrieved its exact source/test files from commit `daa54376e72470e9ea6c01cbead817db9d9f0c36` into an isolated scratch package. All 11 preserved tests pass, including nonuniform separated patches, flux/Gauss balance, uniform-solver equivalence and invalid-data rejection. Main's unchanged six-test baseline also passes. This reproduces bounded branch tests; independent manufactured-solution and integration review remain open.

Publication verification refreshed:

| PR | Scope | Head | Broad verification |
| --- | --- | --- | --- |
| [119](https://github.com/QuantumInquisitor/universal-matrix/pull/119) | Folding and breathing | `60a7fd60f57d73b89ea5397db58a3ff5d291556c` | [Passed](https://github.com/QuantumInquisitor/universal-matrix/actions/runs/36779423445) |
| [120](https://github.com/QuantumInquisitor/universal-matrix/pull/120) | Waves and controllers | `615cee59c51df77406555ac56d40e8a1f1e73ec8` | [Passed](https://github.com/QuantumInquisitor/universal-matrix/actions/runs/36779529688) |
| [121](https://github.com/QuantumInquisitor/universal-matrix/pull/121) | Optional timing subsystem | `ec6489c56953ea0f2de1c78a7ed2adc8a298a710` | [Passed](https://github.com/QuantumInquisitor/universal-matrix/actions/runs/36779581931) |

The three PRs remain drafts and unmerged. Their earlier dedicated experiment, CodeQL and container checks passed. Prior local validation recorded 1,909 selected tests and nine reproduced report commands; those numerical tests were not repeated merely to create this log. Dependency PRs 117/118 are a separate maintenance queue.

Evidence committed with this checkpoint:

- [Plan and completion gates](RECOVERY_PLAN.md)
- [Task register](recovery/tasks.json)
- [All branch dispositions](recovery/branch-reconciliation.json)
- [Fourteen exception file comparisons](recovery/exception-file-comparison.json)
- [PR 7 supersession decision](https://github.com/QuantumInquisitor/universal-matrix/pull/7#issuecomment-5770950959)

Remaining recovery work: classify the remaining branch content differences, deduplicate and reconcile the 776 discovery lines with current code/results, and recover any further project locations identified by relevant artifacts. Do not claim an exhaustive audit of all files, other machines or unsaved state.

Exact next actions:

1. Review the E8 branch tip discrepancy and unresolved source/test differences in the exception comparison.
2. Complete independent manufactured-solution and robustness review of the recovered patterned boundary-flux candidate; its original 11 tests and unchanged six-test main baseline have been reproduced.
3. Turn the aperture/inner/outer/fan-out scratch family into an independently reproducible optional module batch without claiming whole-assembly closure.
4. Continue the W1/W2/crystal decision gates and independent source/observational tasks listed in the register; record named input blockers instead of inventing results.

Execution scope: this log records completed recovery work and queued experiments. It does not mean all research questions are solved or that unattended workers are running. No existing source behavior or default engine clock was changed by this documentation checkpoint.

Validation of this checkpoint: 12 documentation-governance tests passed. The isolated boundary test's first run printed a Windows WMI/Hypothesis diagnostic after reporting 11 passes; a clean rerun with unrelated plugin autoload disabled also passed all 11. Baseline and candidate reruns used `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, and `python -m pytest tests/test_open_boundary_solver.py -q -p no:cacheprovider` from their respective package roots. No source modification was needed for that reproduction.

## 30 September 2026 independent validation and recovered solver

Tasks: REC-NEUMANN, REC-BRANCH-DIFFS. Main was rechecked at `a78576f83854a5b75c90815db121b1ca40a4f606`; PR 122 remained open and unmerged.

The E8 branch tip is three commits ahead of the head recorded by merged PR 59.
Its net diff contains only one duplicate row in DOCUMENTATION_STATUS.md. No
scientific code or tests were lost in that discrepancy. The duplicate is not
restored. Evidence: [tip comparison](recovery/e8-tip-comparison.json).

Independent Neumann checks construct a dense graph matrix by enumerating links
and boundary incidences, without using the candidate's stencil helpers. On
three grids (2x3x4, 3x4x5, 4x4x4), manufactured potentials agree with a constrained
dense solve; the largest potential error is about 3.37e-12 and independently
computed Gauss residual about 1.77e-11. Energy identity error is below 2.85e-14.
The declared acceptance bound is 1e-9 in dimensionless lattice units.

All three numerical cases passed on the historical source, but all six invalid
input controls failed the intended early-rejection contract. Complex source and
face values could silently lose their imaginary part; infinite tolerance and
fractional/boolean iteration limits could be accepted; NaN tolerance reached a
solver breakdown instead of input rejection. The recovered implementation now
checks real numeric arrays, finite positive tolerance and positive integer
iteration limits before solving. Valid numerical results are unchanged.

Published as [draft PR 123](https://github.com/QuantumInquisitor/universal-matrix/pull/123),
head `b7add2892868d5e8150c3a4b148b3c3200642d57`. The source, original and corrected
reports, portable audit script and reproduction note are in that PR. This log
remains separately reviewable in PR 122; neither PR is merged. Remote CI for the
new solver was pending at publication.

Validation: 29 solver/related tests passed (11 original, 11 independent and
robustness tests, seven existing manufactured/property tests). Twelve
documentation-governance tests passed separately. Ruff check/format passed for
the changed Python files. These selected tests are not a fresh full-suite run.

Reproduction after checking out PR 123: `uv run python -m pytest
tests/test_open_boundary_solver.py tests/test_patterned_neumann_independent.py
tests/test_open_solver_manufactured.py tests/test_property_invariants.py`.
The audit command is `uv run python scripts/audit_recovered_neumann.py --candidate
src/open_boundary_solver.py --output artifacts/recovery/neumann.json`.

Limits remain: finite dimensionless graph, no continuum convergence study, no
physical material validation, and no completed whole-network moving geometry.
REC-NEUMANN is now validated and published for review, not merged or empirically
validated. Other branch/document differences and the discovery-line inventory
still require reconciliation.

Next executable batch: integrate the preserved aperture/inner/outer/fan-out
candidate as an optional reference with independent interface, flux and complete
declared-pair checks. Keep whole-assembly motion and material dynamics explicitly
open. Check PR 123 CI before any merge decision, and record failures here.

## 30 September 2026 aperture and fanout integration

Tasks: P03 and REC-APERTURE. Main was freshly checked at
`a78576f83854a5b75c90815db121b1ca40a4f606`. PRs 122/123 remained open and
unmerged. PR 123 CodeQL/container checks had passed; broader verification was
still running at this batch's initial inspection.

The local aperture/inner attachment, B-to-outer detour, original retained
collision control and second-aperture edge-2 replacement are now optional
repository modules. The default builders and original scratch files are
unchanged. Scratch-only imports and output paths were replaced with repository
imports and a portable exporter; fixed coordinates and field equations were
preserved. All 28 transitive existing source dependencies match main after
newline normalization.

Fresh checks: 121 selected attachment, fan-out and downstream tests passed in
73.22 seconds. Nine new Python files pass Ruff check/format. All six cases
I = +/-1, +/-2e-8, +/-7 reproduced successfully, and the dedicated workflow's
acceptance assertions also passed locally. Per case, the separate inventories
contain 117 inner pairs, 56 aperture/environment pairs, 508 outer pairs and 861
replacement-route pairs. These overlap and are not a unique global pair count.
The replacement has 13 internal interfaces. Maximum outer-cut relative flux
error is 1.97e-14. Host-field, divergence-refinement, positive-Jacobian and
adversarial port checks are part of the selected tests.

Published as [draft PR 124](https://github.com/QuantumInquisitor/universal-matrix/pull/124),
head `f5a317f9a0bfdfadb442d647decb629d0199d554`. Review entry:
`docs/toroidal_aperture_integration_v0.1.md`; compact results and source/provenance
hashes are in `docs/experiments/aperture-summary.json` and
`docs/experiments/aperture-integration-provenance.json` in that PR. Full reports
regenerate with `uv run python scripts/report_aperture_integration.py
--output-dir artifacts/aperture`. The dedicated workflow repeats the tests,
report generation and acceptance assertions. Remote CI was pending at
publication. Neither this result nor its log has been merged.

This closes the local-to-reviewable-repository integration for this candidate
family. P03 remains in progress because Tesla, helix and other recovered
candidates still need their own dispositions. P04 remains open: the separate
certificates do not prove complete combined retained-retained clearance, safe
motion, wall-opening feasibility, material dynamics, energy closure or recursive
coupling. The central stagnating streamline remains. Full-network and motion
completion flags remain false.

Next executable batch: create one combined component/port/contact inventory for
the first aperture, outer connection, replacement route and both modified hosts.
Reconcile every retained pair against that single state and emit explicit
unresolved contacts or collision witnesses. Only after that static audit should
the whole-assembly deformation path be tested. Keep W1/W2, crystal, material and
independent research queues visible in the task register.

## 30 September 2026: complete fixed assembly pair and port audit

Continued the next batch recorded above without replacing prior green work.
The combined construction removes the 13 original edge-2 components and uses
both modified host domains. It contains 69 components (66 conduits and three
junctions), four directed routes and 2,346 unique unordered pairs. Every pair
is classified, with declared contacts allowed. There are 62 internal route
interfaces and eight exact junction-port connections; signed current balances
at all three junctions. Twelve pairs require fresh special aperture/bend,
nested-transition or junction support-plane checks beyond the generic classifier.

Validation: 15 new tests passed in 27.60 seconds, including independent pair,
route and interface inventories and rejection controls for tiny displacement,
radius, orientation, signed-current and nonfinite-field errors. The six final
reports (I = +/-1, +/-2e-8, +/-7) reproduced after the last source change.
Maximum relative port residual is 2.07e-16. New Python files pass Ruff check and
format; report acceptance and source hashes were checked locally. This is in
addition to the previously recorded 121-test integration run, not a fresh
full-repository test run. An independent read-only code review found no blocking
issue in the fixed numeric-current scope.

Published by updating draft PR124 to
`e515134ddafd358616cb87cd37b2e90a3602cfae`. Review entry:
`docs/toroidal_combined_aperture_v0.1.md`; snapshot:
`docs/experiments/combined-aperture-summary.json`. Reproduce full pair and port
records with `uv run python scripts/report_combined_aperture.py
--output-dir artifacts/combined-aperture`. The dedicated workflow now repeats
the combined tests, exporter and acceptance assertions. Current-head dedicated experiment, CodeQL and container CI passed; broad verification remains queued. No merge was performed. The prior PR124 head had passed dedicated
experiment, CodeQL and container checks; its broad verification was still running.

Important geometry-to-viewer constraint: `combined_components()` contains the
original enclosing host geometry. Apply the first aperture's
`modified_host_contains` and `SecondAperture.contains` for the actual cut domains;
the raw tuple alone is not a renderable or globally sampled modified assembly.
This closes the combined fixed-state pair-inventory question only. P04 remains
in progress for safe continuous breathing. Floating-point bounds and sampled
fields do not establish interval proof, generalized motion or material physics.

Next executable batch: recover the existing permitted fold/breathing map from
PR119, define how both host cuts and every route/port move, and test the entire
out-and-back path with explicit Jacobian and clearance bounds. Report blocking
pairs or intervals rather than inferring motion from safe endpoints. Material
forces, energy accounting, emergent motion, recursive coupling, the central
stagnating streamline, W1/W2, timing-subsystem comparisons and remaining source
reconciliation retain their open dispositions in the unchanged 40-task register.

## 30 September 2026: complete assembly common breathing control

Verified live PR119, PR122 and PR124 heads and recovered the existing PR119
BreathingCycle at `60a7fd60f57d73b89ea5397db58a3ff5d291556c`. The published
relative-fold specimen has six compliant panel cores, four hubs and twelve
bridges; its hinge map is not assigned to the 66 conduits and three junctions
of the aperture flow assembly. No such correspondence was found in the source
reviewed for this batch. The common-size breathing law is reusable separately.

Added an optional whole-assembly map x=sX, s=1+0.1 sin(2 pi phase), with both
actual aperture cuts transported through inverse coordinates. All dimensions,
thicknesses and junctions share the same map. Positive common scaling preserves
the complete static pair classification continuously: all 2,346 pairs,
62 route interfaces and eight ports remain valid for this restricted motion.
Minimum scale is 0.9 and minimum deformation determinant is 0.729. The relative
Piola current J0/s^2 preserves transported cut flux; the lab-current adapter
adds an explicitly supplied advected reference density. Phase and rates are
dimensionless, with no measured period or force/energy model.

Validation: 24 new tests passed in 45.49 seconds. These cover valid-cycle limits,
invalid inputs, both moving host holes, signed cases, nonuniform-density
Eulerian continuity and moving-interface density jumps. All six report cases
I = +/-1, +/-2e-8, +/-7 reproduced. Each includes 48 moving-cut diagnostics;
maximum relative cut error is 2.11e-15. Ruff check/format, source hashes and both
dedicated-workflow report acceptance blocks passed locally. Independent read-only
review found no publication-blocking issue. This is not a fresh full-suite result.

Published in draft PR124, head `3249637f96c748ba2a08b7ad2c963fa0c5a33d59`.
Review entry: `docs/toroidal_assembly_breathing_v0.1.md`; snapshot:
`docs/experiments/assembly-breathing-summary.json`. Reproduce with
`uv run python scripts/report_assembly_breathing.py --output-dir
artifacts/assembly-breathing`. Dedicated CI now repeats the new tests and reports;
current-head dedicated experiment, CodeQL and container checks passed; broad repository verification remains pending. No merge was performed.

P04 remains in progress. This control proves prescribed common expansion and
contraction subject to the static floating-point assumptions, not inward relative
folding or an emergent living fractal. A graph-to-hinge correspondence (or another
explicitly justified nonuniform map) is the next missing input. Define its
finite-thickness route, junction and host-cut charts before a whole-path audit;
preserve PR119's rigidity result and compliant-panel assumptions. No viewer was
changed. Material forces, energy closure, emergent motion, recursive coupling,
wall-opening feasibility and the stagnating streamline remain open. W1/W2,
timing-subsystem comparisons and remaining source recovery retain their separate
dispositions. The register still contains 40 records; no tasks were silently closed.

## 30 September 2026: eight-image research and equation review

Individually examined all eight supplied originals, including equations,
diagrams, units, process panels and limits of legibility. Preserved originals
locally and recorded dimensions and SHA-256 hashes without publishing the
images themselves. Review: `docs/eight_image_research_review_2026-09-30.md`;
manifest: `docs/experiments/eight-image-manifest.json`. Primary sources are
linked beside biomedical, relativity, topology and quantum-operation claims.

Useful additions are explicit phase/winding/state bookkeeping, separation of
geometry/field/dynamics/observable layers, target-relative synchronization
diagnostics, resource/momentum/energy/heat accounting and data-backed cutaway
views. These are assigned to existing P04-P12 tracks rather than replacing
the catch-up program. None of the pictures supplies the missing hinge-to-flow
correspondence or a material/energy law.

Executed `scripts/report_image_claim_controls.py` and stored its results in
`docs/experiments/image-claim-controls.json`: 613 THz converts to 489.058 nm;
the literal 16-node azimuth formula has only 0/30/60/90-degree positions; the
printed frequency ladder grows twelvefold rather than one octave in twelve
increments; Hermitian phase decoration preserves eigenvalues to 5.33e-15 in
the seeded control; a specified traveling-phase pattern has zero common-phase
order but unit target alignment; a projector with 1% success gives a perfect
conditional target while retaining 99% failures. Conditional recurrence and
reflection-versus-rotation controls were also executed. These are mathematical
counterexamples/diagnostics, not physical device simulations. Script assertions
and Ruff check/format passed.

Continued the existing folding investigation by revisiting the implemented
inversion endpoint/path obstruction in light of Image 3. Its 23 existing tests
passed in 2.34 seconds. Kept its pole, determinant-sign and collision limits;
did not replace it with the picture's unsupported singularless threshold.
The 0.018451 number remains undefined as a physical parameter. No engine
defaults, source geometry or viewer were changed.

One new image-review record brings the catch-up register to 41 records. Review
and arithmetic controls are complete; new oscillator/material/recurrence
experiments remain explicitly proposed under existing task IDs. This does not
close relative folding, emergent motion, energy closure, recursive coupling,
the central stagnating streamline or any matter-synthesis claim.

## 30 September 2026: declared-state recurrence and exploratory-model intent

The user reaffirmed that the Matrix Engine should model the outside world and
explore alternative possibilities rather than use popularity as an acceptance
criterion. Preserved that intent in the new review document: candidates need
explicit assumptions, state, units and discriminating predictions; unfamiliar
models remain eligible for investigation. Validation distinguishes a result
inside an assumed model from agreement with observed physical behavior.

Added `src/declared_state_recurrence.py` and the assembly report adapter.
Position return, declared-state return and winding-history return are separate.
Winding affects the state verdict only under an explicit model policy; ordinary
periodic return remains valid when turn count is only historical bookkeeping.
Exact winding strings, stable identities, explicit units and per-channel
tolerances survive serialization. Changed models/inventories/units and invalid
rotation/state inputs are rejected. All comparisons are limited to the declared
variables; no hidden-state completeness is inferred.

The real 69-component breathing adapter was reproduced at currents +1 and -1.
Tick 18 has the same scale/representative positions as tick 0 but opposite
motion and different phase, so position returns while declared state does not.
Tick 36 returns the declared periodic state while all 69 winding counts advance.
An internal-state perturbation is detected despite equal positions. A tick-35
snapshot restores exactly and its phase/history reproduces the prescribed next
snapshot. The 36-tick-to-size-cycle alignment is an explicit dimensionless
assumption; representative enclosing-body centers and common shape parameters
are not a general mesh-state description. Rotation is relative to reference.

Independent review caught a norm-underflow false-return case at 1e-200 and a
missing adapter source hash. Both were fixed before publication, with tiny-change
regressions and adapter-inclusive model identity. The linked recurrence/clock
suite passes 32 tests (26 new and six existing) in 1.72 seconds. Both final
reports, normalized source hashes, Ruff check/format and all three workflow
acceptance blocks pass. This is not a fresh full-repository validation.

Published in draft PR124 at `3efe05db6ac3d247ac1e7bdec83a8a906d700036`.
Review: `docs/declared_state_recurrence_v0.1.md`; compact snapshot:
`docs/experiments/assembly-recurrence-summary.json`. Reproduce full snapshots
with `uv run python scripts/report_assembly_recurrence.py --output-dir
artifacts/assembly-recurrence`. Current-head container CI passed; dedicated experiment, CodeQL and broad verification remain in progress. No merge
was performed. The catch-up register retains 41 tasks; P10 is not closed by
this recorder.

Next bounded experiment: compare explicitly specified common-phase and
traveling-phase targets under a declared graph and coupling law, measuring
noise/delay sensitivity, recovery and resource costs. Use the recorder for
state/history observations; no memory force is supplied by a policy flag.
Relative inward folding, material forces, energy closure, emergent motion,
recursive dynamics and observed-world calibration remain separate open work.


## 2026-09-30 - Phase-pattern controls and time-hypothesis source review

Read the user's pasted time/Kozyrev thoughts as reference ideas, not instructions.
Preserved primary-attributed source distinctions and falsifiable next steps in
`docs/phase_pattern_and_time_hypotheses.md`. No time-energy source, preferred
handedness or physical time-crystal claim was installed in the engine.

Completed 108 dimensionless reciprocal-ring cases (8/16/24 nodes, three seeds,
two encoded targets, three uniform drifts and coupling on/off). Ten new tests
pass in 0.62 seconds; Ruff check and formatting pass. Step halving reduces the
reference balance residual from 9.29477e-7 to 5.63146e-8, with final phase
disagreement 7.28e-13. Conjugate-phase trajectory error is zero in that control.
The full local report is artifacts/phase-pattern-controls/results.json; compact
results and executable reproduction are included in the recovery publication.

Independent review confirmed the negative-gradient sign and dissipation identity.
It also established that encoded common/traveling targets are exactly equivalent
after subtracting their offsets. This is a diagnostic/control result, not a
discovery of spontaneous waves. Added an explicit equivalence and mean-phase
test, and renamed the balance test to avoid implying physical energy validation.

P05 remains in progress; P06/P08/P09/P10 remain incomplete. The next discriminating
step is an explicit chiral/nonreciprocal alternative with zero/sign controls,
followed by detuning/noise/delay and physical work/reservoir accounting. Full
assembly force coupling and recurrence integration are not part of this batch.
Publication target: existing recovery draft PR122; no merge authorized/performed.


## 2026-09-30 - Parallel directed-phase, delay and material baselines

User requested continued parallel execution. Three bounded agents implemented
independent experiments while the parent checked exact remote heads, CI, the
task dependencies and one historical branch exception. No existing green engine
source was rewritten. The catch-up register remains 41 tasks, not 41 completions.

- Directed phase coupling: 36 zero/sign/coupling/size controls; 13 tests. A named
  asymmetry produces opposite signed transport rates (~+/-0.38257 for the N16
  illustrative case), while explicit model work and dissipation balance. It
  does not discover a preferred handedness or extract energy from time.
- Ordinary delayed tracker: 54 controls; 13 tests. Paired interventions have
  zero effect before imposed transport arrival; finite-record recovery and
  noise/response tradeoff are reported. This is an ordinary comparison baseline,
  not a proven time-crystal advantage or physical propagation experiment.
- Connected material specimen: 12 runs; 12 tests. Synthetic SI two-mass forces
  generate motion, with independently accumulated work, stored energy and
  damping loss. Finest driven residual 2.85e-10 J. Displacement/velocity
  refinement ratios ~15.74/17.86; no mixed-unit physical error norm is claimed.

Peer reviews checked each other's equations, causal controls and limits. Added
Fourier observability guards so vanished modes cannot produce invented phase
rates; bounded the chiral measurement's amplitude/timestep envelope. Clarified
the material convergence units and ensured reporter output directories exist.
Combined validation: 60 tests pass in 3.11 seconds (48 experiment tests plus 12
documentation tests). Ruff check and format pass for all eight experiment files.
All reporters are reproduced through a dedicated CI workflow with source-hash
and numerical acceptance checks. Compact snapshots omit long traces; full
local reports are under artifacts/control-baselines and reproducible via CLI.

The exact-head CI snapshot records successful listed workflows for draft
PR119/120/121/123/124. PR122 had container and CodeQL success with broad checks
running when inspected. The new publication requires its own fresh CI results.
No merge was performed. Existing draft PR122 carries this recovery experiment
batch and log; main and the other draft heads remain unchanged.

Historical recovery also dispositioned the bend-spacing exception as superseded:
the baseline keeps the scan and adds finite-sampling provenance/corrected scope.
Other branch exceptions still need semantic review.

Remaining order: map material forces and directional couplings to actual
geometry; apply matched timing readout/loading/cost assumptions; add feedback
delay/detuning/saturation; then test sustained autonomous breathing, conservative
recursive exchange and viewer replay of those computed states. P04-P10 are not
closed by isolated baselines. Independent R01-R24 research remains recorded in
tasks.json and must not disappear behind these integration experiments.


## 2026-09-30 - Switched material replay, owner energy and recovered fold mapping

Continued the parallel queue with a material persistence experiment and an
independent geometry-to-material source audit. PR122 at 262ed151 had successful
experimental-control, container and CodeQL workflows; broad verification was
still running at the last check. No old branch was reset or merged.

The new switched-drive adapter reuses the unchanged two-mass force law. It
preserves absolute integer steps, timestep, cutoff schedule, both source hashes,
parameters, x/v, cumulative external work, separate losses and link transfers.
Three timestep cases replay bit-for-bit in the same environment through saved
checkpoints before, at and after drive removal at 4 seconds. Post-cutoff work
is exactly zero. A checksum detects unreflected payload alterations; it is not
authentication or proof that a state came from a real experiment.

Body kinetic/anchor energies and one link spring account avoid duplicated
storage. Independent power integration closes each owner's budget; finest total
residual is 3.25e-10 J. The input-off continuation agrees with an analytic damped
modal solution. Positive anchor damping and stiffness exclude a sustained
nonzero unforced periodic orbit in THIS model. No autonomous breathing claim is
made; active reservoir laws and actual folding material remain open.

Independent review verified ownership signs, interval-owned cutoff integration,
source identity and analytic continuation. Eighteen new tests pass; combined
validation with prior controls and documentation: 78 passed in 4.55 seconds.
Ruff check/format pass. The fresh report and dedicated workflow acceptance block
pass locally. New publication needs its own GitHub CI. Saved evidence:
docs/material_restart.md, docs/experiments/material-restart-summary.json,
docs/passive_material_motion_limits.md. Full reproduction remains scripted.

Source audit recovered the existing PR119 connected 22-body geometry: six
compliant cores, four hubs and twelve bridges. It supplies a concrete next
specimen rather than another invented shape. The audit identifies two essential
gaps: bonded overlap needs nonduplicated mass ownership; occupied sets do not
uniquely define interior material-point correspondence. Independent size/fold
coordinates also exceed the old prescribed path's clearance certificate.
See docs/fold_material_mapping_audit.md for pinned sources, functions, equations
and admissibility checks. Those 22 bodies are not automatically a deformation
mapping for the separate 69-component flow graph.

Next: implement the reduced fold specimen's kinematic adapter and derivatives,
then declared mass/potential laws with geometric inertial terms and energy
controls. Keep actual material calibration, whole-flow correspondence, recursive
coupling, matched time-crystal usefulness and viewer integration visibly open.
The register still contains 41 tasks; this batch does not close P04-P10.


## 2026-09-30 - Recovered fold kinematics, lumped inertia and fresh geometry audit

Extended actual pinned PR119 geometry rather than replacing it with a new shape.
The adapter has independent coordinates s and theta, analytic positions and
first/second derivatives, and exactly one synthetic point mass for each of the
six panels, four hubs and twelve bridges. Panel points are arithmetic means of
coefficient vertices, explicitly not volume centroids. Chosen masses total
0.74 kg; length scale 0.1 m/reference unit is illustrative, not measured.

Derived M=sum m J^T J and checked kinetic-energy equivalence. Positive inertia
throughout the admitted rectangle follows a rank argument using fixed hub 0's
scale motion and hub 3's independent fold motion, beyond sampled eigenvalues.
The map is a reduced point model, not a through-thickness material map, solid
inertia calculation, force law or autonomous breathing implementation.

Independently executed the four original geometry/control modules plus original
geometry definitions, with eight hashed local import dependencies. Nine phases
and 22 bodies per phase reproduce source mean-vertex positions within 2.78e-17 m.
All 13 executed source hashes are in fold-original-source-fixture.json. The
fixture exporter executes supplied trusted code and records provenance; it does
not authenticate that a directory is a Git checkout. The adapter is not used to
generate the reference fixture.

Also reran the original complete 3D clearance auditor (amplitude 0.1, maximum depth 10):
accepted, 231 pairs, 1,208 intervals, minimum scaled bound 3.773014616157734e-05
reference units. The source's theta path covers every theta in [0,pi/6]; common
positive scaling of ALL occupied envelopes and attachment regions transports
this result across s in [0.9,1.1]. This improves the earlier audit's open domain
question. It does not validate nonuniform scaling, full solid material-point
correspondence, changed thickness, negative folds, or the 69-component network.
Floating-point support/analytic-speed limitations remain, not interval arithmetic.

Independent review confirmed signed rotation basis, derivatives, inertia and
scope. Input conversion now rejects oversized integers cleanly. Validation:
32 new adapter/reference tests; combined existing experiment/document suite
110 passed in 6.19 seconds. Ruff check/format and CI acceptance block passed.
Report hashes, original-source fixture, export reproduction and source links
are persisted. Prior PR122 head ced2c935 had experimental-control and container
success; remaining workflows were not complete at initial check. Fresh
publication requires new CI, and no branch was merged.

Next bounded step: use these derivatives for an explicitly synthetic reduced
potential/damping model, including coordinate-dependent inertia, prescribed
external-work accounting, conservative and drive-off controls, and boundary
rejection. Full solid calibration, active reservoirs, recursive exchange,
whole-flow mapping and actual viewer integration remain open. Task count: 41.


## 2026-09-30 - Force-driven reduced folding and visible energy evidence

Continued from verified PR122 head c62ff718; its experimental-control, container
and CodeQL workflows passed, with broad verification still in progress when
checked. Reused unchanged fold kinematics and mass ownership. No merge or
replacement of earlier validated code.

Implemented M(q) qddot + b(q,qdot) + grad V + D qdot = Q(t), where b is derived
from the actual marker Jacobians/Hessians. Chosen positive quadratic potential,
damping and generalized force have explicit units and synthetic status. Motion
is now computed from forces, not programmed as a size/fold trajectory. Damping
and drive work are accumulated separately from endpoint T+V. A tapered drive
stops at one second without force discontinuity; the chosen continuous forcing
extracts net energy in this run, which the signed ledger correctly records.

Six cases at three timesteps: equilibrium, conservative, damped, driven,
drive-off and intentionally omitted inertia (18 runs). Correct-model fine-step
maximum residual <=6.37e-17 J; omitted-inertia residual 1.33e-7 J. Independent
finite-difference Christoffel vector and directional energy derivative checks
detect missing geometric inertia. Exact passive initial energy is below the
minimum boundary-potential lower bound, a model-specific unforced confinement
argument. RK stages/endpoints are checked, but no general continuous driven
trajectory certificate is claimed.

Independent review found no blocking mathematics defect. Added overflow
rejection and labelled coordinate extrema as sampled. Convergence errors keep
scale/angle/rate units separate. Sixteen new tests pass; focused linked fold,
source-fixture and documentation suites: 60 passed in 5.03 seconds. Existing
unrelated phase/material-restart suites were not unnecessarily rerun. Ruff and
format checks pass, full reporter regenerated, and the workflow acceptance
block passed locally. Fresh publication requires its own GitHub checks.

Published compact report: docs/experiments/fold-dynamics-summary.json. Full
endpoint traces and sampled actual 22-body coordinates are reproducible using
scripts/report_fold_dynamics.py. Scientific chart generated by
scripts/plot_fold_dynamics.py, checks both source hashes and performs no new
simulation/fitting. Visually inspected artifact:
artifacts/fold-dynamics/motion-and-energy.png. Graphs show computed size/fold,
work-minus-loss agreement and the failing omitted-inertia control. It is not
a replacement for the XR engine-state viewer.

Scope remains the synthetic 22-point reduction: no calibrated solid material,
distributed strain, body rotational inertia, active reservoir, recursive
whole-structure exchange or autonomous sustained breathing. Task count remains
41. Next bounded checks are longer/perturbed modal response and law sensitivity,
before introducing an explicit finite reservoir for sustained-motion tests.


### 2026-09-30 — Finite fold sensitivity and independent modes

Preserved force-driven model and original geometry. In parallel, added a
24-case sensitivity ensemble and an independent small-amplitude eigenmode
reference. Ensemble: 21 accepted, 3 deliberately high-rate domain rejections,
zero numerical errors. Domain rejection is not collision evidence. Accepted
maximum ledger residual 2.998e-12 J (relative 1.4245e-8); a 10-second refinement
reduces residual 1.541e-13 to 4.298e-15 J. Damping removes energy; external
forcing can add it. Two seeded perturbations are not statistical assurance.

Two synthetic modes: 0.2741982850 and 0.3163579847 Hz. Six nonlinear/linear
comparisons at 10 seconds plus a refined seventh run; halving amplitude gives
approximately fourfold smaller position discrepancies. Independent dynamics
Jacobian, generalized eigenvalue invariants and linear energy checks support
the local equations. Frequencies are model predictions, not measured material
resonances; the finite window spans roughly three cycles. Refinement is not
a measured convergence order. Independent review found no blocking math issue;
scalar validation and numerical-error classification were hardened.

Validation: 75 linked fold tests passed in 11.72 s; Ruff and format pass for
four new code/test files. Source-hashed compact reports and reproduction steps
are in docs/fold_modes.md and docs/fold_robustness.md. Workflow gains report
reproduction, hash and numerical acceptance checks. Existing unrelated suites
were not rerun. Previous PR122 head 2084560f has passing experiment, container
and CodeQL runs; broad verification still running at this snapshot. A new head
needs fresh CI. No merge performed.

Task count remains 41. P07/P08/P09 remain in progress. Physical calibration,
recursive coupling, energy reservoirs, autonomous motion and XR integration
remain open. Next bounded step: an explicit finite reservoir with transfer and
loss accounting, without assuming sustained motion or free energy.


### 2026-09-30 — Finite internal reservoir and feedback

Added optional nine-state reduced fold experiment with velocity-aligned feedback,
finite reserve, delivered work and separate damping/conversion/leakage ledgers.
Existing geometry and force model are reused unchanged. No external time waveform.
Six ten-second cases plus refined fueled run: empty, disconnected, equilibrium,
ideal transfer, fueled and intentionally missing reserve debit. Reserve falls
from 2e-5 to 6.61439e-7 J, below the 3.33333e-6 J mechanical-growth threshold.
This supports transient amplification, not indefinite autonomous breathing.

Total balance residual 1.83306e-13 J, refined 8.49182e-15 J; ideal-control
residual 8.00817e-13 J. Missing-debit control fails at 1.54121e-5 J. Independent
review found no blocking issue and independently differentiated total energy
(residual 4.07e-14 J/s). Exact equilibrium remains at rest, leakage matches its
analytic exponential, disconnected motion matches the prior passive model.
No clipping; invalid reserves/stages reject. Finite supply W<=eta R_initial.

Validation: 17 reservoir tests plus 16 existing dynamics tests: 33 passed in
5.83 seconds. Ruff passes; final reports regenerated, source hashes and workflow
acceptance checked locally. Previous PR122 head 44cb8193 has passing experiment,
container and CodeQL checks; broad verification was still running. New head
requires fresh CI. No merge. Reports: docs/fold_reservoir.md and
docs/experiments/fold-reservoir-summary.json. Task register retains 41 entries.

Next: explicit equal-and-opposite exchange between two modules and global
accounting before recursive whole-structure composition. Material calibration,
continuous collision proof, XR integration and sustained motion remain open.


### 2026-09-30 — Two-module generalized fold exchange

Coupled two existing reservoir modules through a positive generalized spring
potential. Each module keeps separate connection work, while the connection
owns its potential once. Global mechanics+reserves+connection+losses is constant.
Module B begins at rest with an empty reserve. Conservative transfer gives B
7.00014e-6 J mechanically at 10 s; disconnected B stays at zero. Initial spring
energy contributes to transfer and is explicitly counted (1.05e-6 J).

Four 10-second cases and a refined fueled run: coupled/fueled, disconnected,
conservative and reversed-B-reaction negative control. Global fueled residual
2.47678e-13 J improves to 1.04661e-14 J. Wrong reaction fails connection/global
accounts at 3.243e-5 J while local work accounts remain nearly balanced. Independent
review confirms equations, indexing and signs; directional global energy error
3.39e-15 J/s and predicted wrong-reaction error 3.16e-6 J/s. Complete initial
states added to reports for reproducibility. Source hashes cover all four scripts.

Validation: 14 new coupling tests plus 33 linked reservoir/dynamics tests passed.
Ruff and formatting pass. Workflow reproduces reports and checks hashes,
connection/global/local ledgers, transferred energy and negative controls.
Previous PR122 head 17b1af10 has successful experimental, container and CodeQL
checks; broad verification still running at snapshot. New publication requires
fresh CI. No merge. Reports: docs/fold_coupling.md and
docs/experiments/fold-coupling-summary.json. Task count remains 41.

This is a synthetic generalized-coordinate connection, not a spatial joint,
Cartesian momentum claim or intermodule collision certificate. No full recursive
structure or sustained breathing claim. Next: a small graph with one energy
owner per connection, then recursive composition and separate spatial mapping.


### 2026-09-30 — Small fold graph and single-owner edge energy

Extended the existing module/pair law to validated graphs of up to eight nodes;
reported six four-node, four-second cases plus chain refinement. Each connection
owns its potential once and tracks both endpoint works. Node, edge and global
accounts remain separate. Duplicate/reversed duplicate edges, self-links and
invalid indices or stiffness weights reject. Initial state and five source
hashes are recorded. No prior model or default engine behavior was changed.

Chain/star/cycle/disconnected/conservative cases have global residual <=4.605e-13 J.
Chain .02/.01 s refinement gives 1.883e-13/9.027e-15 J, per-coordinate differences
<4.194e-9. Broken edge1 creates 3.955e-7 J defect while other edge residuals remain
<5.31e-14 J. Conservative downstream transfer occurs without reservoir work;
initial mechanical and edge potential energy are accounted for. Graph cycles
are not spatial fractal closure or sustained breathing evidence.

Independent review found no blockers. Directional total-energy derivative
-3.73e-14 W; deliberate active-edge sign reversal -4.20e-6 W. Endpoint orientation
and node relabeling controls preserve dynamics; two-node reduction matches the
verified pair. Twenty new network tests plus 31 pair/reservoir tests: 51 pass
in 16.56 s. Ruff/format pass; workflow report/source-hash/numerical acceptance
passed locally. Prior head afa3ae79: container and CodeQL passed; experimental
and broad verification were still running at snapshot. Fresh head needs CI.
No merge performed. Results: docs/fold_network.md and
docs/experiments/fold-network-summary.json. Register retains 41 tasks.

Next: explicit parent/child grouping with accounting and trajectory invariance
for the same graph, then separately justify cross-scale coupling laws. Spatial
joints, intermodule collision, material calibration, full recursive structure,
sustained breathing and XR integration remain open.


### 2026-09-30 — Parent/child regrouping invariance

Added validated hierarchy leaves and lowest-common-ancestor connection ownership.
Independent recursive force traversal retains the same degrees of freedom and
force laws. Flat, balanced, deep and reordered layouts are integrated against
a flat graph reference for two seconds. All saved coordinate/rate and energy
states match exactly in this run. Inclusive group accounts balance to 1.342e-13 J
when crossing-boundary work is included. Parent accounts overlap children and
must not be summed across levels. The root counts nodes and edges once.

Double-counted edge accounting control overcounts initial energy by 1.05e-6 J
and creates a spurious -7.36997e-7 J change. This is an accounting negative
control; graph force-sign controls remain separate. Independent review found
no blockers and subgroup directional energy-minus-boundary errors <1.15e-14 J/s.
Input validation rejects incomplete/duplicate leaves, invalid depth and timesteps.

Validation: 22 hierarchy tests and 20 linked network tests pass. Ruff and format
checks pass. Report stores six source hashes, initial state, ownership tables
and group accounts. Experimental workflow reproduces and checks invariance,
source hashes and the accounting control. Prior head e31d252a container passed;
CodeQL, experimental and broad verification were running at snapshot. New head
requires fresh checks; no merge. Report: docs/fold_hierarchy.md and
docs/experiments/fold-hierarchy-summary.json. Task count remains 41.

This validates regrouping only, not new physical scales, calibrated materials,
spatial collision/joint assembly, sustained breathing or XR mapping. Next: an
explicit mapped cross-scale potential and its derivative forces, with energy
checks before whole-structure application.


### 2026-09-30 — Mapped connector and interruption recovery

Recovered saved mapped-connection implementation after a usage-limit interruption.
Verified live PR122 remained at af94ba28; all four workflows on that prior head
completed successfully. Preserved existing green work. New optional connector
uses f(q,l)=l[s-1,s sin(theta-theta=0)] and derives both generalized forces from
one quadratic port mismatch potential through their respective Jacobians.
Module mass, inertia and material parameters remain unchanged: leverage-only
scaling, not validated geometrically scaled solids.

Five four-second cases and half-port refinement cover length ratios 1/.5/.25,
conservative transfer and deliberately incorrect child Jacobian. Correct global
residual <=2.068e-13 J; half-port refinement 2.036e-13 to 1.018e-14 J. Wrong child
mapping violates connector/global accounts at 1.416e-6 J while node accounts
remain balanced. Independent review found no blockers: 24 interior configurations
energy-rate checks within 4.41e-14 W and local Hessian agreement within 8.03e-14.

Validation: 18 mapped tests plus 31 linked pair/reservoir tests: 49 passed in
14.17 s. Ruff and formatting pass. After interruption, source hashes and full
workflow numerical acceptance were verified against saved reports. Results:
docs/fold_mapped.md and docs/experiments/fold-mapped-summary.json. New head
requires fresh CI. No merge; register remains 41 tasks.

Next: state length/mass/inertia scaling assumptions explicitly and independently
validate them before applying the connector across recursive levels. Spatial
attachment, collision, calibration, full recursive assembly, sustained breathing
and XR mapping remain open.


### 2026-09-30 — Conditional body scaling laws

Reconstructed the synthetic point geometry at length factors1/.5/.25 and masses
factor cubed, without changing prior experiment sources. Generalized inertia,
fixed-rate geometric bias and point angular inertia scale to the fifth power.
Assumed equal strain-energy density gives cubic potential; chosen fourth-power
damping preserves damping ratios. Corresponding durations are2/1/.5 seconds,
not equal physical times. Initial rates scale inversely with length.

All stored coordinates/rescaled rates/energies match the original passive solver
for the binary factors tested. Residuals8.170e-15/1.021e-15/1.277e-16 J. Deliberately
wrong cubic acceleration inertia creates3.210e-7 J energy defect. Independent
review found no blockers:24 interior configurations including nonbinary.37 give
energy-rate errors<=4.793e-14 W and acceleration similarity<=9.715e-17. These
are consequences of explicit synthetic assumptions, not measured material laws.

Validation:15 new scaling tests plus37 linked kinematics/dynamics tests passed
(52 total,8.73s). Ruff/format and source-hash/workflow acceptance pass. Prior
head f025063a: container passed; experimental, CodeQL and broad checks running
at snapshot. Fresh publication requires CI; no merge. Results in docs/fold_scaling.md
and docs/experiments/fold-scaling-summary.json. Task count remains41.

Whole-system similarity also requires connector stiffness proportional to length:
fixed stiffness produces quadratic connector energy rather than cubic. Next is
a combined scaled-body and scaled-connector experiment. Calibration, actual
attachments/collision, full recursive physical assembly, sustained breathing
and XR mapping remain open.


### 2026-09-30 - Consistently scaled passive pair

Combined reconstructed body geometry/mass/inertia with mapped connector forces.
Parent scales 1/.75/.5, child fixed at half parent size. Physical connector
stiffness scales with overall length, giving cubic potential/force scaling.
No active reservoirs included. Corresponding physical durations 1/.75/.5 s.
Correct trajectories match under scaled time (rate difference <=2.776e-17);
maximum energy residual <=5.775e-17 J. Independent half-step agreement gives
component differences <1.821e-9 with each unit kept separate. Same-grid similarity
is a scaling consistency check, not an independent accuracy estimate.

Fixed-stiffness comparison still conserves energy (2.376e-17 J residual) but
child angle differs by .004220 rad from the resized reference. This is a valid
alternative law that breaks similarity, not broken energy physics. Independent
review found no blockers: force-gradient error 2.45e-15 and energy-rate errors
3.71e-16/4.50e-16 J/s for scaled/fixed stiffness. Comparison now rejects mismatched
reference scales, grids and relative sizes; refinement labels distinguish rates.

Validation: 17 scaled-pair tests plus 33 scaling/mapped tests pass (50 total).
Ruff/format and regenerated source hashes/workflow numerical acceptance pass.
Prior head 05513696: CodeQL and container passed; broad and experimental checks
were running at snapshot. New head requires fresh CI; no merge. Results:
docs/fold_scaled_pair.md and docs/experiments/fold-scaled-pair-summary.json.
Task count remains 41. Next: multiple absolute body sizes in a small graph,
explicit per-edge stiffness law, and hierarchy boundary accounts. Material
calibration, real joints/collisions, full recursion, sustained breathing and XR
mapping remain unvalidated.


### 2026-09-30 - Mixed-size passive graph and boundary accounts

Four modules with relative sizes 1/.75/.5/.5 use scaled body mechanics. Edge
stiffness is weight*max(endpoint sizes)*K0, an explicit symmetric homogeneous
synthetic choice. Each edge owns potential once; each node and subgroup records
its boundary work. Global scales 1/.75/.5 preserve relative geometry and the
conditional similarity law. No active reservoir is present in this experiment.

Root energy residuals 7.940e-17/3.350e-17/9.925e-18 J. Wrong edge 1 reaction
creates 1.701e-10 J defect while other edges remain within 3.81e-16 J. Both
child-group ledgers still balance because they record actual crossing work;
the edge and root identify the defect. Half-step agreement is within 1.944e-10
for coordinates and 7.749e-10 for rates, with units kept separate.

Validation: 15 new tests passed in 34.42 s; 39 linked pair/hierarchy tests passed
in 21.72 s, 54 total across those runs. Ruff/format and report-source hashes/CI
acceptance pass. Parent independent edge-power check 6.54e-15 W, endpoint reversal
exact; tests additionally cover subgroup power, node permutation and pair reduction.
Saved-sample plot generated and visually inspected at
artifacts/fold-multiscale/computed-network.png; plotting code checks source hashes.
The graph and plot are not spatial placement or XR validation.

Prior head 4d7f271f experimental/container/CodeQL checks passed; broad verification
still running at snapshot. New head requires CI. No merge. Reports in
docs/fold_multiscale.md and docs/experiments/fold-multiscale-summary.json.
Task register retains 41 entries. Next: explicit size laws for reservoir capacity,
transfer power and leakage timescales before active graph composition. Materials,
real attachments/collisions, full physical recursion and sustained breathing remain open.

### 2026-09-30 - Finite reservoirs across unequal-size modules

- Added explicit capacity/activation s^3, feedback damping s^4 and leakage-rate .15/s laws to the four-node mixed-size network. These are synthetic similarity assumptions, not measured material laws.
- Separate node mechanical/reservoir accounts, edge potential ownership and subgroup boundary work preserve complete energy accounting. No external replenishment; negative reserves rejected without clipping.
- 19 focused and 32 linked passive-network/reservoir tests passed (51 total); Ruff and workflow acceptance passed. Computed plot visually inspected. Maximum valid root residual 4.632e-16 J; missing node-1 debit detected at 2.438e-9 J and localized to its subgroup/root. Empty-reservoir and zero-gain reductions, independent group energy derivatives, finite supply and fixed-leakage alternative checked.
- Half-timestep comparison: root residual 5.789e-17 to 3.131e-18 J, coordinate/rate differences 2.033e-10/1.192e-9. No convergence-order or sustained-breathing claim.
- Source-hashed report: docs/experiments/fold-active-multiscale-summary.json. Methods: docs/fold_active_multiscale.md. Computed plot source: scripts/plot_fold_active_multiscale.py. Automated acceptance added to experimental-control workflow and executed locally.
- P08/P09/P10 remain open; next work must address longer-duration behavior, physical supply/material laws and actual assembly constraints rather than treating short transients as a completed science engine. Existing 41-task register preserved.

### 2026-09-30 - Longer finite-source duration and depletion audit

- Added scripts/report_fold_duration.py, tests/test_fold_duration.py and source-hashed docs/experiments/fold-duration-summary.json. Existing mechanical equations and geometry limits unchanged.
- Active, passive and exact-rest cases completed 60s. All reserves stayed positive/decreased. Active one-percent brackets: node 0: 27.91895-27.95163 s; node 1: 22.04491-22.07788 s; nodes 2/3: 15.16578-15.19336 s.
- Derived R<=R0 exp(-.15t/s) and gain 4 damping dominance by s*log(6)/.15, at most 11.945 s. Active mechanical energy showed no increase across 1,443 accepted intervals beyond that threshold. Exact rest retained zero motion; passive mechanics decreased.
- Active root accounting error 5.3307e-14 J, refined 5.0714e-15 J; final coordinate/rate differences 7.1395e-10/1.1895e-9. Active final mechanical+connector energy 5.0280e-8 J versus initial 4.9344e-7 J. No sustained-breathing claim or finite-time zero-motion claim.
- 18 focused tests passed (17+1), Ruff/format, all 12 source hashes and complete workflow acceptance passed. Scope and negative-reserve stage controls retain the last accepted state without clipping; unknown errors propagate. Computed plot visually inspected; separate duration CI job added.
- Prior draft head b38ecdd: experimental, container and CodeQL checks passed; legacy compatibility and Python 3.14 subjobs passed, broader verification still running at snapshot. No merge. Draft publication of this new checkpoint requires fresh CI.
- Methods/results and next power-source boundary: docs/fold_duration.md. All 41 tasks preserved; P09 remains open. A replenished model must account for injected energy and compare timing/control choices at equal power budget; time-crystal component usefulness is not inferred from this finite-source test.

### 2026-09-30 - Explicit replenishment and repaired scientific CI setup

- Added optional ideal external power law J=6e-6*s^2*max(0,1-R/Rcap), Rcap=2e-5*s^3, with four cumulative input ledgers. Existing mechanics unchanged; lossless charging is an explicit idealization, not hardware validation.
- Powered/source-off/finer-powered cases completed 20 seconds. Received input 78.3829 microjoules; final mechanical+connector energy 3.16379 versus 0.694234 microjoules (4.557 ratio, not efficiency). Powered energy still increased over the last five seconds; stable breathing remains unproven.
- Root accounting errors: powered 6.7935e-14 J, off 3.1798e-14 J, fine 1.6618e-14 J. Deliberately omitting source input in postprocessing produces 7.8382923857e-5 J error. Refinement coordinate/rate differences <=3.0568e-9/1.2747e-8; body energy ledgers <=1.293e-13 J.
- 18 focused tests passed; Ruff/format, source hashes, finite JSON and workflow acceptance passed. Tests cover independent subgroup-energy derivatives, source-off reduction, exact rest charging, size similarity, power/capacity bounds, stage failures and missing-input detection. Plot visually inspected. Completed cases separately checkpointed under artifacts/fold-supply keyed by sources/settings.
- Recovered prior-head CI failure: duration job 110208866158 in run 36811997803 failed collection with ModuleNotFoundError: No module named scipy. Controls job passed. Corrected duration and supply jobs to explicitly install/use the scientific extra and select Python 3.12; previous setup silently followed .python-version 3.14. No physics thresholds weakened. Fresh-head remote verification still required.
- Reproduction: docs/fold_supply.md, scripts/report_fold_supply.py, docs/experiments/fold-supply-summary.json and scripts/plot_fold_supply.py. Duration documentation now states the required scientific extra.
- All 41 tasks preserved. P08/P09 remain open for calibrated supply/materials and longer stability/perturbation tests. The source law makes exact rest an invariant solution with negative linear damping for small motion (feedback16/7); this is not spontaneous startup or a physical time-crystal advantage.


### 2026-09-30 - Powered continuation and accounted disturbance

- Continued the pinned 20-second powered seed to physical 60 seconds without changing mechanical/source equations. Baseline, 1% velocity intervention and finer baseline all completed; 161 common samples each and complete 50-60 second windows. Restart ledgers are rebased without altering physical derivatives.
- Independent quadratic kinetic calculation verifies the intervention adds 1.2086158011e-8 J. Charging law/cap are shared, but actual received energy differs and is separately accounted; this is not an equal-received-energy comparison.
- Baseline mechanical+connector energy rises from 33.8093 to 49.2218 microjoules over seconds 50-60 (45.6%); disturbed final energy is 49.2986 microjoules. No settled breathing demonstrated. Maximum scale/angle separation 0.000308773/0.000648664 rad does not by itself establish attraction or instability.
- Finer-reference maximum coordinate differences 1.339e-8/2.484e-8 rad, rate differences 5.600e-8/s and 1.184e-7 rad/s, energy difference 2.259e-12 J. Largest group residual 3.424e-12 J. Reserve, input and capacity bounds pass.
- 17 focused tests passed; strengthened four tamper cases rechecked. Ruff/format, 13 source hashes, seed hash, finite JSON and complete workflow acceptance passed. Saved-sample plot generated and visually inspected. Per-case checkpoints preserve expensive runs.
- Prior PR122 head 851920dfc0f452564b0851be2e3202d1585881a8 now has all four listed workflows successful, including broad verification. This new checkpoint requires fresh CI; no merge.
- Methods: docs/fold_stability.md; report: docs/experiments/fold-stability-summary.json. Added separate stability CI job. All 41 task entries/statuses preserved.
- Next discriminating test: source sweep around the derived 0.6 microwatt unit-size linear damping threshold (current source 6 microwatts). Threshold is conditional on synthetic laws, not a material constant or stable-cycle proof. Material calibration, assembly constraints, full recursion, XR and time-crystal component benefit remain open.


### 2026-09-30 - Equilibrium-reserve power onset sweep

- Added optional threshold experiment reusing the unchanged supplied four-node dynamics. Five source coefficients 0/0.3/0.6/0.9/1.2 microwatts start with identical small coordinate displacements, zero velocities/ledgers and power-dependent equilibrium reserves. Initial mechanical energy 2.7687834892e-10 J is shared; total initial energy and received energy are not equal.
- Independent review verified R*/Rcap=p/(p+3e-6), feedback/damping=8p/(3p+3e-6), and threshold 0.6 microwatts under the synthetic size laws. For initial R<=R*, reserve interval is invariant and mechanical+connector energy is nonincreasing at/below threshold. Conservative connector powers cancel. Exact rest has zero physical derivatives but nonzero balanced input/leak ledgers.
- All five cases plus finer 0.9 microwatt repeat completed 20 seconds. Final/initial mechanical-energy ratios: 0.22079648, 0.55159631, 0.99997741, 1.52235386, 2.08333465. Decay below onset and finite-time amplification above agree with the prediction; no stable breathing claim. Late slopes use actual saved endpoints after 15s, with explicit coverage.
- Worst group/root residual 3.4152e-16 J. Finer endpoint ratio 1.52235512; coordinate/rate differences <=3.600e-10/7.604e-10, mechanical difference 3.488e-16 J. Separate coordinate/rate/joule guards pass. Nineteen focused tests, Ruff/format, 13 source hashes, finite JSON, input/reserve bounds and complete workflow acceptance pass. Computed plot visually inspected.
- Independent stiffness-energy bound confines smallest-node deviations below threshold to scale <=0.0004786865 and angle <=0.0008739579 rad while a smooth exact solution exists. This is not collision or numerical-stage certification.
- Prior head 2a9f550a222f57c1bd584c2545a00fb06107716b: experimental controls including stability, CodeQL and container passed; broad verification still running at snapshot. New threshold CI job added; fresh-head CI required. No merge.
- Evidence: docs/fold_threshold.md and docs/experiments/fold-threshold-summary.json; source/plot scripts report_fold_threshold.py and plot_fold_threshold.py. All 41 task entries and statuses preserved. Next: longer above-threshold continuations and initial-condition comparisons using existing reservoir feedback, with scope termination retained. Materials, whole assembly, full recursive coupling and XR remain open.


### 2026-09-30 - User-authorized reprioritization: breathing is not a global gate

- Preserve the completed synthetic breathing/power controls as regression evidence. Do not continue long amplification runs merely because settled breathing is still unproven.
- Prioritize P04/P07 connected geometry and explicit material forces, then P08/P10 energy ownership and recursive coupling. P11 computed-state viewer mapping advances alongside those interfaces. P05/P06/P12 independent experiments can continue in parallel.
- Corrected task-register gating: P07 no longer requires independent wave/crystal tracks to finish before material work; P10 no longer requires P09 stable breathing. Integration still requires the relevant geometry/energy evidence. Dependencies mean interface prerequisites, not blanket closure gates.
- All 41 task entries and statuses preserved; no scientific task is marked complete by reprioritization. Breathing remains a system-level test after relevant model changes and must emerge from declared equations rather than a prescribed outcome.


### 2026-09-30 - Parallel geometry-derived constitutive and generated-harmonic checkpoints

- P04/P07: introduced a separate static potential on six exact affine panel midsurfaces and twelve source bridge centerlines. Synthetic Young=1000 Pa, nu=.3, effective reference thickness=1e-4 m and bridge EA=.1 N; reference q=(1,pi/12). Analytic gradient gives restoring generalized force with the negative sign. Old point inertia and quadratic-law dynamics remain unchanged; no silent double spring.
- All 22 body vertex sets replayed at nine pinned fixture phases (198 comparisons), max error 2.776e-17 m. Reference potential/gradient zero; independent scale-energy error 3.05e-20 J, sampled virtual-work gradient error <=1.35e-13, symmetric positive reference tangent. Membrane-only, axial-only and zero-law controls pass. Axial bridge length is independent of fold angle; no bridge bending supplied. Four hubs have no constitutive law. Reduced energies are not an overlapping solid-volume partition or measured material data.
- P05 recovery: source files absent from this checkout were found in PR120 head 615cee59c51df77406555ac56d40e8a1f1e73ec8. W1 recorded source hashes match after explicit LF/CRLF and terminal-newline reconstruction. W2 saved artifact already has force-limit, delay, disturbance and mismatch cases, but no source hashes. Provenance limits recorded in docs/recovery/wave-source-provenance.json; no legacy simulations repeated.
- P05 new experiment: cubic odd-cosine Galerkin modes {1}, {1,3}, {1,3,5}, finer three-mode repeat and pump-off control all reach 20 periods / 201 matched samples. Generated q3/q5 sampled magnitudes .00926230/.000186143 from zero higher-mode initial states. Pump-off still generates q3 while total energy decays and external work is zero. No pattern-selection, traveling-wave, quantum or material-coupling claim.
- Wave mode-truncation effects: adding mode3 changes q1 by 9.2553e-4; adding mode5 changes q1 by 1.5914e-7 and q3 by 4.9619e-6. Same-model numerical refinement <=1.624e-12 coordinates and 8.043e-12 rates. Worst ledger residual 1.52e-13 dimensionless model energy units. Quadratic modal energies explicitly exclude shared nonlinear/pump terms.
- Combined validation: 57 tests passed in 3.55 s (33 constitutive + 24 harmonic); Ruff/format, source and fixture hashes, finite JSON and new workflow acceptance pass. Constitutive geometry/energy plot generated and visually inspected. Reports reproduce from tracked files only; legacy wave artifacts are not runtime dependencies. New dedicated material-and-harmonics job added.
- Evidence: docs/fold_constitutive.md, docs/wave_harmonics.md and their source-hashed reports under docs/experiments. All 41 task entries retained. Next material step is conservative/passive/driven integration of this potential; recursive coupling and independent wave tests advance without requiring settled breathing. Full assembly/contact, calibration and XR remain open.

- Publication gate snapshot: prior PR122 head e14b677c6682c93b91fcbba18926290d884bfde5 has experimental controls, CodeQL and container workflows successful; broad verification remains running. This new checkpoint requires fresh CI; nothing merged.


### 2026-09-30 - Six-draft capability audit and lynchpin/material reconciliation

- User requested reviewing the drafts and lynchpin work for forgotten completed capabilities. Owner-scoped GitHub search returned six visible open drafts, all in QuantumInquisitor/universal-matrix; the two known local clones share that origin. Full changed-file inventories captured for PR119-124. This is not a rescan of every closed historical PR.
- PR119/120/121 contribute 24/17/8 published files absent from this checkout (49 total), not missing implementation. PR123 seven files and PR124 twenty-eight files match their published contents locally. All listed workflows pass for 119/120/121/123/124; PR122 at 7dd38fb has experimental/container/CodeQL success with broad verification running at snapshot. No merges.
- Lynchpin work already includes rigidity/compliance controls, finite panel stretches, 22 connected bodies, localized attachments, continuous clearance and a 202-frame exporter. PR124 already includes the fixed 69-component full pair inventory, common scaling/current transport and declared-state/winding replay. These fill prior geometry/interface gaps but do not equate the 22-body material specimen with the 69-domain flow assembly.
- P05 corrected to reuse 14 nonlinear, 8 two-mode and 11 controller robustness runs; stochastic ensembles and broader comparisons remain. P06 corrected to reuse 168 six/eight-spin runs, selected error/size/long-duration comparisons and resource counts. The ordinary divider also passes; no practical timing advantage was established. All 41 task IDs/statuses preserved, scopes and historical plan reconciled.
- Implemented a reference-correct overlay joining the original nine fixture frames to synthetic constitutive data by all 22 stable IDs. Old geometry strains reference theta=0; new material law references theta=pi/12. Rebasing phase 0.25 and removing its 1.1 scale gives agreement on 54 independent original-vertex SVD stretch comparisons within 8.89e-16. Wrong old-reference control differs by 0.17537. Source replay 198 vertex sets <=2.78e-17m; sum of 18 energies exact; four hubs explicitly unmodeled. No new dynamics or viewer integration.
- Validation: 14 new overlay tests; 47 linked overlay/constitutive tests passed together in 3.12 s. Agent independently reran 28 local geometry/address tests in 3.18 s. Ruff/format and expanded material/harmonic/overlay workflow acceptance pass. Previously published clearance/test counts were inspected evidence, not rerun wholesale.
- Found five initial local/published documentation differences caused by encoding drift, including mathematical symbols. Publication payload now explicitly reads UTF-8; local mathematical text preserved, fourteen corrupted range dashes repaired in the older plan. Source code and validated numerical reports were not rewritten for this documentation correction.
- Evidence: docs/recovery/DRAFT_CAPABILITY_AUDIT.md, docs/recovery/draft-capability-audit.json and docs/experiments/lynchpin-material-overlay.json. Reuse/stage draft geometry interfaces, then connect material/inertia/energy and actual viewer state using these IDs and reference metadata. Stable breathing remains a milestone test, not a global gate.


## 2026-09-30 - Explicit constitutive force-driven motion

Connected the geometry-derived membrane/axial potential to the existing 22-body
point-mass integrator through an explicit potential selector. The historical
quadratic default remains; no spring energy is silently added to material energy.
Owned inertia, geometric inertial bias, external work and damping loss are retained.

Validation: 12 new tests and 16 historical dynamics tests passed together (28,
22.13 s); 33 constitutive tests passed separately (1.55 s). Independent finite-
difference energy gradients and Cartesian kinetic energy checks pass. A wrong
quadratic-force law and a doubled spring are detectable negative controls.
At dt=.01 s over .4 s the conservative balance error was 2.86e-15 J, passive
1.19e-15 J and driven 1.14e-15 J. Directional energy-rate error was 1.23e-13 J/s;
omitting geometric inertia gives 1.11e-5 J/s error. Report reproduction adds
three step sizes and equilibrium/drive-shutoff controls with source hashes.

See docs/fold_material_dynamics.md and
scripts/report_fold_material_dynamics.py. This is synthetic reduced mechanics,
not calibrated materials, stable breathing, distributed rotational inertia,
contact, whole-flow coupling or completed XR. Existing network and finite-supply
experiments have not silently inherited this new potential. P07/P08 remain open.
