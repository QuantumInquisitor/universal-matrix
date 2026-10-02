# Recursive exact-clearance bracket refinement

PR #140 established the first exact finite-grid recursive collision/free bracket using actual
panel polygons, bridge segments and hub points:

- colliding at vessel/module ratio 10.9691527565;
- collision-free at 19.7444749617.

The broad interval is refined here without changing any geometry, tolerance or state coverage.

## Method

The canonical Seed-axis placement and all 105 module pairs are reused. Every module pair retains
the same independent 9 x 9 q-state coverage from the coarse audit.

Each refinement stage divides the current bracket into four equal subintervals and evaluates the
five bracket points. Previously evaluated endpoints are cached and are not recomputed.

If the sampled collision/free mask contains exactly one colliding-to-free transition, that
sub-bracket becomes the next stage.

If multiple transitions or a collision re-entry appear, refinement stops and reports the mask
instead of assuming monotonic clearance.

Four stages are requested, narrowing a single-transition bracket by up to 4^4 = 256 in width.

## Claim boundary

This remains finite sampling on the declared q-grid and zero-thickness source geometry. The final
sampled bracket is not a continuous collision theorem and is not yet a physical manufacturing
clearance.

No common vessel/module ratio is selected by this audit.
