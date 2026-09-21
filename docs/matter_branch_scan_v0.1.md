# Nonlinear Matter Branch Scan v0.1

## Purpose

A single localized nonlinear solution is not enough to identify a stable matter
sector.

This utility scans controlled central-amplitude ranges and records the actual
solution branch.

Implementation:

`src/matter_branch_scan.py`

Tests:

`tests/test_matter_branch_scan.py`

## 1. Recorded quantities

For each central amplitude (A_0), the scanner records:

- solver status;
- solved harmonic frequency (omega);
- nodelessness;
- total energy (E);
- classical U(1) charge (Q);
- (E/Q);
- whether (E/Q<m_{m free}).

## 2. Valid branch filtering

A point is considered a physical candidate for further study only if:

[
	ext{solver status}=0
]

and the profile is nodeless.

Failed numerical points are not allowed to compete for "best" energy.

Excited/node-containing branches are also separated from the lowest nodeless
branch.

## 3. Stability filter

A converged localized solution is marked as an energetic candidate only when

[
oxed{
E/Q<m_{m free}.
}
]

This remains a necessary energetic diagnostic, not a proof of full dynamical
stability.

## 4. Why the scan is not run exhaustively in CI

Boundary-value branch scans can become computationally expensive and may
require continuation strategies.

Normal CI therefore tests the classification and filtering logic only.

Large scans should be explicit research runs with:

- parameter ranges recorded;
- solver tolerances recorded;
- failed points retained in output;
- continuation direction recorded;
- branch-crossing behavior inspected.

## 5. Next numerical improvement

The strongest next solver upgrade is pseudo-arclength continuation, which can
track nonlinear branches through folds where using central amplitude or
frequency alone becomes ill-conditioned.

## Status

The project now has a controlled workflow for searching stable nonlinear matter
branches without conflating solver failure, localization, and stability.
