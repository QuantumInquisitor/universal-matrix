# Unequal-size passive material graph

This checkpoint asks whether the geometry-derived material law can participate in
an unequal-size network with consistent local and group energy accounting. It is
an additive experimental model; the pinned historical restart and older model
implementations are preserved.

## Declared scaling law

Let a be the module's length scale relative to the reference specimen. This model
holds Young's modulus and Poisson ratio fixed while scaling every geometric length,
including membrane thickness, by a. Bridge cross-sectional area, and therefore EA,
scale by a squared. The concrete constitutive parameters are length=0.1a metres,
effective thickness=1e-4a metres and bridge EA=0.1a^2 newtons.

Membrane area times thickness scales as a^3. Axial energy EA*(extension)^2/(2L)
also scales as a^3. The potential and its generalized gradient therefore both scale
as a^3 at the same dimensionless coordinates. The separately declared point masses
scale as a^3 and coordinate derivatives of position as a, so generalized inertia
scales as a^5. The existing synthetic damping rule is a^4 and the mapped connector
stiffness scales with length, giving connector energy proportional to a^3 under
uniform scaling of the entire graph. Similar trajectories consequently use time
scaled by a and generalized rates scaled by 1/a.

These are conditional model assumptions. Constant sheet thickness yields membrane
energy proportional to a^2, and constant bridge EA yields axial energy proportional
to a; neither supports the same similarity claim. Fixed density/mass scaling is
still independently specified, not derived from measured sheet density or hub
material. There is no calibrated material or distributed rotational inertia here.

## Ownership and limits

The four-module graph uses relative sizes (1, .75, .5, .5), four mapped connectors
and the existing two-level grouping. Each node owns its kinetic and material energy
and damping loss. Each edge owns one connector energy. Group accounts include their
internal edges once and separately track work crossing their boundaries.

This is passive force-driven motion, not the prescribed geometry phase. It adds no
reservoir, supply or perpetual energy source. The generalized connectors do not
establish intermodule spatial placement, joint strength or collision clearance.
It is not the whole 69-domain flow assembly or a complete recursive material engine.

```sh
uv run python scripts/report_fold_material_multiscale.py --output artifacts/fold-material-multiscale/report.json
uv run python -m pytest tests/test_fold_material_multiscale.py
```

## Recorded results

The reference run spans 0.2 seconds and the half-size run 0.1 seconds, representing
the same dimensionless interval. Maximum reference node residual is 3.74e-16 J;
maximum group residual is 2.17e-16 J. The finer half-size run reduces these to
2.46e-18 J and 1.28e-18 J. Coordinate differences under rescaling are zero at
reported precision; maximum rescaled rate difference is 8.68e-19 per second.

The deliberately reversed reaction at edge 1 produces 3.01e-13 J imbalance,
over 1100 times the largest healthy edge residual. The root account detects it;
the two child-group accounts still balance their independently measured boundary
work. This localizes the inconsistency rather than only reporting a global total.

At the tested half-size state, homothetic material energy agrees with a cubed
scaling to reported precision; keeping thickness and EA fixed instead changes
energy by 2.26e-6 J. This is a comparison between declared models, not a new
experimental law of matter. Longer time, more graph depths and active power are
still outside this checkpoint.
