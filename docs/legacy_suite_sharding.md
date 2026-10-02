# Full legacy suite scheduling

Run 37050300656 exhausted the 40-minute full-suite job budget after reporting
28% progress. Its log showed no failure before cancellation; the unfinished
tests were not validated. Core and long Q-ball jobs passed separately.

Pull requests into the recovery integration branch now run this workflow too,
so scheduling changes and accepted recovery work can be verified before merge.

The full suite now runs in eight independent jobs, with a 60-minute budget per
job. All collect the same complete pytest suite using the same Python 3.12
environment and all optional runtime groups. A stable SHA-256 of the file
portion of each node ID assigns tests to jobs, preserving file-local ordering
and module fixtures. Session fixtures run once per job; this is not a claim
of identical cross-file shared-process behavior.

Each job records full collection, selected IDs, completed IDs and exit status.
The final job retains the **Full legacy compatibility suite** check name and
requires all eight jobs to succeed. It rejects missing/duplicate manifests,
different collections, assignment errors, incomplete execution and nonzero
exit status. Test skips retain pytest's existing semantics; they are not
relabelled as assertions passed. Empty partitions can succeed only when the
overall collection is nonempty. A failed or cancelled job cannot produce a
green aggregate check.

No test list, scientific criterion or source model was removed or changed.
Durations are reported for future balancing. File-based partitioning reduces
the accumulated runtime; a single file can still exceed a job's budget and
must then be investigated explicitly.

Validation uses a real parametrized pytest suite across all eight partitions
and a real failing test, plus manifest fault controls. The remote complete
suite is the final validation, not the small harness tests.
