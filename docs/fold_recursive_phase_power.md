# Recursive modal phase and mechanical power-flow audit

This checkpoint uses a mathematical idea that is standard for oscillators: a periodic state can
be represented as rotation in a two-dimensional phase plane.

For one linearized module mode, define

`x = v^T(q-Q0)`

and use its natural angular frequency `omega` to define the quadrature coordinate

`y = -v^T(qdot)/omega`.

For an ideal harmonic mode,

`x = A cos(phi)`

and

`y = A sin(phi)`.

The pair `(x,y)` therefore traces a circle while either coordinate alone appears as a wave.
The 0, 90, 180 and 270 degree landmarks are simply the four quarter-cycle points.

## What is measured

No force law is changed.

For representative recursive edges at child levels 1, 2 and 3, every stored full-tree sample is
converted into modal phase states for the parent and child.

The report keeps:

- parent and child phase-space amplitude;
- phase angle;
- cosine and sine projection;
- nearest quarter-cycle landmark;
- wrapped child-minus-parent phase lag;
- instantaneous parent connector power;
- instantaneous child connector power;
- connector storage rate.

The child connector power is also labeled mechanical energy current to the child. This is a power
flow diagnostic in joules per second. It is not electric current.

For each mode and depth, the report measures the correlation of sine/cosine phase lag with child
power and connector storage rate. These correlations are reported rather than assumed.

## Why this matters

Earlier audits showed that deeper recursive attenuation is dominated by the parent trajectory,
phase history and elastic connector storage rather than by a defective local 1:2 coupling law.

The phase-space representation gives that timing a direct angular coordinate. It lets the engine
test whether power transfer changes systematically with relative phase, which is the rigorous
part of the circle-to-wave idea.

## Plasma boundary

This checkpoint does not model plasma, charge carriers, current density, electric fields or
magnetic fields.

A future plasma comparison would require explicit charged-particle or continuum variables and
electromagnetic field equations. Only then would quantities such as electric current density,
plasma frequency, electromagnetic phase and collective modes be physically comparable with this
mechanical phase/power diagnostic.

No plasma correspondence is inferred from a visual similarity between waves.
