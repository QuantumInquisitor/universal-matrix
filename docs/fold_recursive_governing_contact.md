# Governing recursive panel-contact solve

The exact assembly audits converged on one limiting body relationship:

- root module panel-0;
- depth-3 module [0,1,1] panel-5;
- both material scale coordinates near 1.1;
- child fold angle near zero.

The dense finite-grid bracket is already extremely narrow, but it is still a sampled q-grid result.
This checkpoint treats the identified feature pair as a local continuous numerical optimization
problem.

## Local state box

The optimized variables are:

- root scale in [1.07, 1.1];
- child scale in [1.07, 1.1];
- child theta in [0, 0.04].

Root theta is omitted from the optimizer because panel-0 contains only nonrotating rays 0 and 1.
That invariance is checked separately over 13 root-theta values spanning the full declared domain.

A deterministic simplicial SHGO search minimizes exact panel-panel distance inside this local box
for every tested vessel ratio.

## Contact-ratio solve

The dense finite-grid colliding/free bracket seeds an 18-step bisection. Each midpoint is
classified from the globally optimized local panel-pair clearance using the already declared
collision tolerance.

Previously tested free guard ratios remain available if the dense finite-grid upper endpoint does
not remain free under continuous local optimization.

The result is an operational numerical collision-tolerance boundary for this feature/state box,
not an analytic collision theorem.

## Monotonicity diagnostics

At the final free ratio, one-dimensional dense axes separately vary:

- root scale;
- child scale;
- child theta.

The report records whether clearance is nonincreasing or nondecreasing along each axis within the
existing numerical collision tolerance. No direction is assumed in advance.

## Assembly control

The full 15-module broad q-grid exact scan is repeated once at the final local free ratio. If it
collides, the local feature solve cannot be used as the assembly boundary.

## Limits

This is a local continuous numerical optimization around the already demonstrated governing
feature family. It is not a proof over the entire continuous q domain. Source geometry remains
zero-thickness, and no manufacturing margin or physical vessel/module ratio is selected.
