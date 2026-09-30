# Matrix Engine recovery and execution log

This is the durable resume point for the catch-up program. Read the [plan](RECOVERY_PLAN.md), [task register](recovery/tasks.json), and the latest dated entry before starting work. Update this log at each substantive checkpoint, including failures and interruptions. A plan, passing unit tests, publication and empirical validation are different states.

Latest checkpoint: the continuation entry below records independent solver validation,
six corrected input defects, publication in draft PR 123, and closure of the E8
tip discrepancy. Earlier next-action lists are historical snapshots.

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
