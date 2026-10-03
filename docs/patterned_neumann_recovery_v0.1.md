# Patterned boundary flux recovery

This recovers the unmerged candidate at commit
`daa54376e72470e9ea6c01cbead817db9d9f0c36` and validates it against independent
finite graph equations. The existing uniform gate API remains available;
`solve_open_gauss_with_face_flux` additionally accepts six spatial face arrays.
Positive values mean outward flux, and their total must equal total enclosed
source. Arrays use the two tangential lattice dimensions of each face.

The historical implementation passed its 11 original tests, but independent
input checks exposed six gaps: nonfinite tolerance, fractional/boolean iteration
limits, and complex source/face values. The corrected solver rejects these
inputs explicitly, including on zero-source early-return paths. Face data are
validated and copied. Valid uniform gate problems retain their existing
behavior; invalid values formerly cast or accepted can now raise ValueError.

Independent validation enumerates every cell link and boundary incidence to
assemble a dense graph matrix without calling the production stencil helpers.
Three noncubic/cubic manufactured-state cases compare recovered potentials to
known states and a constrained dense least-squares solve, independently check
Gauss balance, and compare link energy with the quadratic matrix form. The
seed is fixed at 20260930. Numerical comparisons require errors below 1e-9 in
dimensionless lattice units. This is a finite-grid algebraic test, not a spatial
continuum convergence study or physical/material validation.

Reproduce from the repository root:

```sh
uv run python -m pytest tests/test_open_boundary_solver.py tests/test_patterned_neumann_independent.py
uv run python scripts/audit_recovered_neumann.py --candidate src/open_boundary_solver.py --output artifacts/recovery/neumann.json
```

The report script accepts an explicitly selected trusted Python module and
executes it; it does not download candidates. The historical report is retained
at `docs/recovery/neumann-independent-audit.json`, and the corrected snapshot at
`docs/recovery/neumann-corrected-audit.json`. Source hashes distinguish them.

Remaining limits: dimensionless unit lattice spacing, no material constitutive
law, no whole-network geometric embedding, and no moving-boundary dynamics.
This solver is an optional boundary-model capability, not completion of the
breathing recursive assembly. Independent control results do not certify every
possible array size, condition number, or floating-point magnitude.
