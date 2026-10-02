# Dense governing-state recursive clearance audit

The exact recursive collision boundary is controlled by one repeated geometric relationship:
root panel-0 against depth-3 panel-5 on path [0,1,1], with both modules at the broad-grid corner
q=(1.1,0).

The four-stage vessel-ratio refinement narrowed the broad-grid boundary to:

14.9454706307 < ratio <= 14.9797492331.

This checkpoint asks whether that apparent worst state is truly the declared q-domain corner or
only a consequence of the coarse 3x3 q grid.

## Dense local state grid

Only the governing root/depth-3 module pair is densified.

Scale coordinate samples:

1.07, 1.08, 1.09, 1.095, 1.1.

Fold-angle samples in radians:

0, 0.0025, 0.005, 0.01, 0.02, 0.04.

That gives 30 local states per module and 900 independent state pairs for the governing module
pair.

The exact panel/bridge/hub primitive-distance kernel from the merged clearance audit is reused
without modification.

## Ratio refinement

The merged broad-grid lower and upper ratios are used as the initial bracket. If the old upper
sample becomes colliding on the denser q grid, three previously tested broad-grid free guard
ratios are available above it.

Once a dense collision/free bracket is found, eight bisection steps narrow it.

## Control

At the final dense collision-free ratio, the full 15-module broad 9x9 state audit is run once as
a control. This checks that another module pair does not become the assembly-level limiter while
the governing pair is being examined more densely.

## Claim boundary

This remains finite sampling and zero-thickness source geometry. It does not establish a
continuous state-space or vessel-ratio collision theorem, and it does not yet introduce
manufacturing margin or body thickness.
