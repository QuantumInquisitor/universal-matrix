# Coupled LC reference

This optional model describes two synthetic lumped electrical loops coupled by
mutual inductance. It is a conventional declared circuit control, with no
geometry-derived parameters, measured apparatus reconstruction, or historical
source claim. It does not connect to the material engine or piezoelectric port.

For signed charges `q` in coulombs and currents `i = qdot` in amperes:

```text
L = [[L1, M], [M, L2]]       henries
K = diag(1/C1, 1/C2)         inverse farads
R = diag(R1, R2)            ohms
L qddot + R qdot + K q = u  applied loop voltage in volts
E = (q.T K q + i.T L i)/2   joules
dE/dt = u.T i - i.T R i    watts
```

Require positive self-inductances/capacitances, nonnegative resistances and
`abs(M) < sqrt(L1*L2)`. This makes magnetic storage positive definite in exact
arithmetic. Mutual energy is `M*i1*i2`, counted once. All supplied parameters
are synthetic SI inputs with explicit provenance. Numerical lossless modes
solve `K v = omega**2 L v`; damped poles are reported separately.

The source contains only the model and validation. The report script checks
four preserved cases (equal loops, detuned loops, lossy detuned loops, and
uncoupled loops), analytic roots against a Cholesky-reduced eigenproblem,
modal residuals and orthogonality, normal-coordinate equal-loop modes,
winding reversal, passive poles, zero/small coupling, and the global identity
`A.T H + H A = blockdiag(0,-2R)`. Signed forced states separately verify input
power minus losses. No trajectory integrator is used.

Run from the repository root after installing the test/lint dependencies:

```text
python -m pytest -q tests/test_coupled_lc_reference.py
python -m scripts.report_coupled_lc_reference --output artifacts/coupled-lc-reference.json
```

The committed `docs/experiments/coupled-lc-reference-summary.json` records the
four synthetic cases. The original 13 rejection controls still run unchanged.
Pytest adds malformed scalar/state controls and extreme finite overflow checks;
it reruns the independent physical audits rather than trusting stored statuses.

## Recovery provenance

This is a promoted copy of the preserved local `coupled_resonance.py` scratch
control, hardened through an independent local input review. Original files
remain preserved. Exact SHA256 records:

- Original source: `bf1fa88fe6dad993f15e13aea911fdc10fc918963509c290b06e2d712d5d20af`
- Original report: `515884f60a7edb70e5da307740c934ff3ca51776737485b75b108a62717c7191`
- Intermediate hardened source: `189e258d948ebe9909791b8757044719e1247415d7206ef93565c5ba722cbb86`

The promotion preserves every original numerical report field exactly in the
local reproduction. Report scope/provenance metadata changes to omit historical
claims; therefore the promoted JSON is not claimed byte-identical to the old
report. Cross-platform regression checks permit the original declared floating
point tolerances, while the independent physical checks retain their thresholds.

## API and limits

Scalar parameters accept finite Python/NumPy real numeric scalars. Booleans,
complex values (including zero imaginary parts), strings, and scalar arrays
are rejected before conversion. `energy(q, i)` requires shape `(2,)` finite
real vectors, accepting lists, tuples and arrays. Mixed boolean/complex lists
are inspected before lossy coercion. Values already coerced by the caller
cannot recover their original type.

Nonfinite derived values, arithmetic overflow, failed matrix solves and
nonpositive computed squared modes raise `ValueError`. In particular, finite
but extreme charges/currents cannot silently return infinite energy. This
is a float64 model, not arbitrary precision; broad conditioning, underflow,
and parameter-range accuracy are not certified by these moderate test cases.
A model with representable input matrices may still reject a later operation
whose result cannot be represented.

A physical bridge still needs measured or electromagnetically reduced L/C/M/R,
winding and terminal conventions, driving/loading, and an explicit reciprocal
piezoelectric connection with capacitance stored once. This reference does
not complete that bridge or establish physical device performance.
