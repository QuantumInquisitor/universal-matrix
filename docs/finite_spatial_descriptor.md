# Finite spatial descriptor for one material snapshot

This optional static comparison uses the accepted material-viewer example at recovery `57f812f0122aea43b085204777950010fd6c8c87`. It selects frame 0 at 0 seconds and only `module-0`, retaining its verified local metre coordinates. The small [frozen input](experiments/finite-spatial-descriptor-input.json) stores the exact 58 selected coordinates, identities, selection and original full-source hash. Its projection was compared exactly with the immutable accepted Git blob. The frozen input's normalized-text SHA-256 is pinned before parsing; later changes to the live viewer example do not silently change this dated experiment. No dynamics, viewer, material law or global placement is changed.

## Population and frozen comparison

All 22 bodies contribute 58 vertex occurrences, each retaining its body/vertex identity. Exact numeric-coordinate deduplication gives 46 points and retains all occurrence memberships. Signed zeros compare equally; near-coincident values remain separate. These are two different equal-weight populations, not equivalent mass distributions. Neither is a calibrated scattering model.

For each population the reporter evaluates `S(k)=|sum exp(i k dot r)|²/N` along the local x,y,z axes over 0–200 radians/metre, first at 2 and then 1 radian/metre spacing. The grid, module, seeds and control scales were fixed before evaluating descriptors. Full values and pair distances are saved, including zero-distance pairs among coincident occurrences. No radial average replaces the directional data.

Each population has one PCG64 seed 7 uniform-random comparator with the same point count and axis-aligned bounding window, and one seed 19 Gaussian-jitter comparator with per-coordinate standard deviation 0.002 metres. Jitter is not clipped, so its window can expand. The same seeds are restarted for each population; these are separate paired-size examples, not an ensemble or matched density across occurrence and unique populations. Exact generated coordinates are saved. Uniform random points have no excluded-volume constraint.

A separate 3x3x3 cubic lattice with 0.05 metre spacing supplies the known-peak control. It is not count/window matched to the specimen. The three analytic reciprocal vectors of magnitude 2pi/0.05 return `S=27`; its finite-array extinction is independently tested.

## Observations and their limits

The [saved report](experiments/finite-spatial-descriptor.json) contains every coordinate, identity, population membership, reciprocal grid, descriptor value and pair distance. Across specimen, random and jittered populations, the largest sampled nonzero value lies at the first nonzero grid point: 2 radians/metre on the coarse grid and 1 on the fine grid. Excluding only `k=0` therefore does **not** remove the forward lobe. These maxima are not resolved nontrivial peaks or evidence of crystallinity, and the grid was not changed to seek a different conclusion.

For illustration, the fixed 100 radians/metre samples in the fine grid are:

| Population | Comparator | S along x | S along y | S along z |
|---|---|---:|---:|---:|
|58 occurrences|Specimen|2.049726|4.863858|6.785274|
|58 occurrences|Uniform random|0.486729|0.613895|0.519821|
|58 occurrences|Jittered specimen|1.897648|3.803121|6.176118|
|46 exact-coordinate points|Specimen|0.092307|0.723854|1.509606|
|46 exact-coordinate points|Uniform random|0.704618|0.476585|0.676714|
|46 exact-coordinate points|Jittered specimen|0.176091|0.490573|1.865502|

This descriptive slice is not a predeclared hypothesis test or significance result. Weighting/deduplication changes the statistic substantially; silently identifying repeated owners would change the question. One random realization cannot assign a chance probability. Full curves are supplied to avoid reducing the result to this illustrative sample.

## Independent checks and reproduction

Tests compare the Fourier sum with the independent pair-sum formula and a two-point analytic identity. They check normalization `S(0)=N`, nonnegativity, inversion symmetry, permutation and translation invariance, simultaneous point/reciprocal-vector rotation covariance, common-scale identity, known cubic peaks/extinction, exact ownership preservation and near-coincident behavior. A deliberately unmatched rotation demonstrates why fixed directional cuts are not rotation invariant.

Run `python -m pytest tests/test_finite_spatial_descriptor.py -q -p no:cacheprovider`, then `python scripts/report_finite_spatial_descriptor.py --output docs/experiments/finite-spatial-descriptor.json`. The report includes normalized-text hashes of its fixture, implementation and reporter, plus NumPy version and exact random coordinates.

Remaining: an independently validated quasiperiodic reference; a justified nontrivial-peak/forward-lobe statistic and randomized ensemble; reciprocal-space/window sensitivity beyond three axes; separate controlled size/depth sequences; justified scatterer or mass weights where physically claimed. A finite snapshot does not establish bulk crystal/quasicrystal order, physical diffraction, space-time order, a 22-to-69 correspondence or a global assembly frame. The quasiperiodic comparison is explicitly deferred rather than assigned to an arbitrary 13-coordinate projection.
