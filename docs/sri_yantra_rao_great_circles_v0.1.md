# Rao great-circle incidence audit v0.1

This checkpoint reconstructs nine spherical generators from the Rao Table 1
reference row (constraints 1, 2, 4, 5, 10, 19), with two explicitly audited
formula corrections. It verifies numerical incidence equivalence for this row.

## From rounded parameters to geometry

`src/sri_yantra_rao_spherical_reference.py` retains the six printed parameters
and their approximately 3.2e-7 maximum constraint residual. The new
`src/sri_yantra_rao_great_circles.py` refines those six equations with SciPy.
Every refined parameter stays within its printed six-decimal rounding interval;
the maximum residual is below 1e-12 (about 5.6e-16 in the reference run).
This is numerical refinement of one solution, not a uniqueness proof.

Axis latitude theta and perpendicular arc x give the unit-sphere point
`(sin(x), cos(x)*sin(theta), cos(x)*cos(theta))`.
The nine roots use Rao's axis points and transverse arcs, with four upward
and five downward triangles. The two outer spanning triangles share the
specified circumcircle. All generators lie in the open northern hemisphere.

## Formula audit

The scanned primary source was checked against Figure 2.2 and equations 2.22
and 2.41. These issues have different origins:

| Equation | Issue | Treatment |
| --- | --- | --- |
| 2.41 | The saved implementation used capital V8 where the paper has lowercase v8. | Correct the transcription to `sin(u7 + v8)`. Test point 14 against its defining great circle. |
| 2.22 | The printed denominator `sin(r+c)` does not put point 16 on the great circle through P4 and point 6. | Preserve literal `derived.x16`; use a separately named `corrected_x16` with denominator `sin(d+g)` for geometry. |

The second correction follows from the defining axis arc P4P7 = d+g.
The printed and corrected widths are approximately 0.1083091702 and
0.3061976124 radians. Their normalized great-circle plane residuals are
approximately 0.16431 and 6.4e-17. The six selected parameter constraints alone
do not detect either width error; geometric incidence tests are essential.
This is our geometric correction to the printed formula, not a claim that a
published erratum exists.

## Derivation and comparison

The gnomonic chart `(X/Z, Y/Z)` sends great-circle segments in this hemisphere
to straight segments. Its inverse normalizes `(u,v,1)`. Thus the independent
finite-segment chamber extractor can compute intersections without sampling
curved edges. The spherical edge path is the inverse image of each entire
projected segment, and lies in its defining plane through the origin.

The resulting arrangement contains:

| Object | Count |
| --- | ---: |
| Vertices | 69 |
| Atomic edges | 142 |
| Bounded faces | 74 |
| Odd-coverage triangular chambers | 43 |
| Remaining bounded faces | 31 |

The outer-to-inner chamber circuits have sizes 14, 10, 10, 8, 1.
These counts are computed rather than supplied as extraction targets.
Each vertex is labelled by its incident original generator edges. These labels
produce a bijection with the Huet arrangement that preserves every atomic
edge, every bounded face, and every selected chamber in its ring. This is a
stronger check than agreement of the five counts alone.

Tests also sample all 142 atomic edge paths for unit norm, projection round
trip, and great-circle plane membership. Those numerical checks accompany the
analytic chart argument; finite sampling alone would not prove the edge rule.

## Reproduce

Install the existing scientific extra, then run:

```sh
python -m src.sri_yantra_rao_spherical_reference
python -m src.sri_yantra_rao_great_circles
python -m pytest -q tests/test_sri_yantra_rao_spherical_reference.py tests/test_sri_yantra_rao_great_circles.py
```

## Evidence boundary and next gates

This validates one refined, corrected Rao reference construction to numerical
tolerance. It does not establish equivalence for every spherical parameter
row, all twenty constraint functions, degenerate limits, or any Meru metric.
The stereographic topology control remains a separate construction whose
edges generally are not great circles. Neither result establishes physical
particles, forces, units, or empirical cosmology.

The next geometric gate is an explicit nonplanar Meru incidence model with
stated metric assumptions and edge paths; the broader Rao family requires
separate continuation and degeneracy checks. See `MATRIX_ENGINE_WORK_QUEUE.md`.

## Primary source

C. S. Rao, “Sriyantra - A Study of Spherical and Plane Forms,”
Indian Journal of History of Science 33(3), 1998, 203–227.
[Scanned article](https://insa.nic.in/writereaddata/UpLoadedFiles/IJHS/Vol33_3_3_CSRao.pdf).
